#!./env/bin/python -u
"""
   ___  ___   ___         _
  / __\/ __\ / __\ /\   /(_)____ /\/\   ___
 / _\ / /   / /    \ \ / / |_  //    \ / _ \
/ /  / /___/ /___   \ V /| |/ // /\/\ \ (_) |
\/   \____/\____/    \_/ |_/___\/    \/\___/

"""


if __name__ in ('__main__',):
    import log
    log.init_new_log()


import sys
import datetime
import time
import pymongo
import tarfile

import database
import vizmo_import
import vizmo_aggregate
import meta
from log import config_decorator


@config_decorator
def _transfer_aggregations(_config=None, db=None, log=None):
    """
    Transfer the completed aggregations and bin meta from the private db to the public one.
    """

    db_public = database.Connection('public')

    log.info("Transferring new aggregations")

    # Drop AGGREGATIONS_MONGO_TO collection if it already exists.
    db_public[_config['vizmo_python']['aggregations_mongo_to']].drop()

    # Create an index for our new aggregations collection.
    db_public[_config['vizmo_python']['aggregations_mongo_to']].create_index([('id.geo_id', pymongo.ASCENDING),
                                                                              ('id.geo_type', pymongo.ASCENDING),
                                                                              ('id.time', pymongo.ASCENDING)])

    for aggregation in db[_config['vizmo_python']['aggregations_mongo_from']].find():
        db_public[_config['vizmo_python']['aggregations_mongo_to']].insert(aggregation)

    log.info("Transferring new bin meta")

    # Drop the _config['vizmo_python']['bins_mongo_to'] collection if it already exists.
    db_public[_config['vizmo_python']['bins_mongo_to']].drop()

    # Create indexes for our new bin meta collection.
    db_public[_config['vizmo_python']['bins_mongo_to']].create_index([('geo_id', pymongo.ASCENDING)], unique=True)
    db_public[_config['vizmo_python']['bins_mongo_to']].create_index([('geometry', pymongo.GEOSPHERE)])

    for bin_meta in db[_config['vizmo_python']['bins_mongo_from']].find():
        db_public[_config['vizmo_python']['bins_mongo_to']].insert(bin_meta)


@config_decorator
def _update_db(_config=None, db=None, log=None):
    """
    Use vizmo_import and vizmo_aggregate to update the aggregations with the new tests.
    """

    log.info("Importing new tests")
    while True:
        try:
            vizmo_import.main([])
            break
        except tarfile.ReadError:
            log.info("Attempted to import tests and failed! Waiting to" +
                     " try again...")
            _idle()
            continue

    log.info("Binning and aggregating new tests")
    vizmo_aggregate.main([])

    meta.main([])

    _transfer_aggregations()
    db.meta.update({'type': 'flags'}, {'$set': {'map_complete': False}}, multi=True, upsert=False)


@config_decorator
def _idle(_config=None, db=None, log=None):
    """
    Idle for the configured amount of time.
    """

    time.sleep(int(_config['vizmo_python']['sleep_time']))


@config_decorator
def main(argv, _config=None, db=None, log=None):
    """
    Import, bin, and aggregate the new data and then transfer it to the public database on completion.
    """

    while True:

        # Check the value of map_complete
        map_complete = db.meta.find_one({'type': 'flags'})['map_complete']

        if map_complete:
            # Check for new tests to import
            today = datetime.datetime.now() - datetime.timedelta(days=1)
            today_str = "{:%Y%m%d}".format(today)

            latest_aggregated_date = db.meta.find_one({'type': 'dates'})['latest_aggregated_date']

            if today_str in (latest_aggregated_date, ):
                _idle()
            else:
                _update_db()

        _idle()

if __name__ in ('__main__',):
    main(sys.argv[1:])