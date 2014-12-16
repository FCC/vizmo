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


import datetime
import sys
import os
import pymongo.errors

from download import RequestsDownloader
from extract import TarBallExtractor
from mongoimporter import MongoImporter
import util
from log import config_decorator


@config_decorator
def update_db_with_tests(date, _config=None, db=None, log=None):
    """
    Use the supplied date to retrieve the appropriate tests from SamKnows and import them into the database.

    Args:
        date - The date of the tests to upload.
    """

    # Download tests from Samknows.
    log.info("Downloading tests for " + str(date))
    samknows_downloader = RequestsDownloader(_config['vizmo_import']['test_url'],
                                             _config['vizmo_import']['test_username'],
                                             _config['vizmo_import']['test_password'],
                                             _config['vizmo_import']['test_dir'], date)
    samknows_downloader.download_tests()

    # Open the tarball.
    output_dir_suffix = "{:%Y%m%d}".format(date)
    log.info("Extracting the tarball for " + str(date))
    tar_extractor = TarBallExtractor(_config['vizmo_import']['test_dir'], output_dir_suffix + "-fcc-android.tar.gz",
                                     _config['vizmo_import']['test_dir'] + "/json/" + output_dir_suffix)

    # Import the tests to Mongo.
    log.info("Importing tests to mongodb for " + str(date))
    mongo_importer = MongoImporter(date,
                                   _config['vizmo_import']['test_dir'] + output_dir_suffix + '-fcc-android.tar.gz',
                                   tar_extractor.get_file_names())
    mongo_importer.import_tests()

    # Close and remove the tarball.
    tar_extractor.close()
    os.remove(_config['vizmo_import']['test_dir'] + "{:%Y%m%d}".format(date) + "-fcc-android.tar.gz")


@config_decorator
def _clear_buffer(_config=None, db=None, log=None):
    """
    Finish flushing the test buffer if the buffer status flag is False.
    """

    if not db.meta.find_one({'type': 'flags'})['buffer_transfer_complete']:
        for test in db.test.buffer.find():
            try:
                highest_test_id = db.meta.find_one({'type': 'highest_test_id'})['value']
                test.update({'test_id': highest_test_id})
                highest_test_id += 1

                db.test.buffer.remove({'_id': test['_id']})
                db.test.raw.buffer.insert(test)

                db.meta.update({'type': 'highest_test_id'}, {'$set': {'value': highest_test_id}})
            except pymongo.errors.DuplicateKeyError:
                pass

    db.meta.update({'type': 'flags'}, {'$set': {'buffer_transfer_complete': True}})


def main(argv):
    """
    Entry point for vizmo_import.py. Parses the incoming date and passes it to a decorated helper function.
    """

    date = util.parse_date(argv)
    main_wrapper(date)


@config_decorator
def main_wrapper(date, _config=None, db=None, log=None):
    """
    Helper for main.

    Import tests from Samknows into the Mongo database. If a date is supplied as a cli argument, import only that day.
    Else, import all tests up until today - one day.

    Args:
        date - The date to be imported if one was supplied.
    """

    log.info("Importing tests to mongodb!")

    first_date = datetime.date.fromordinal(int(_config['vizmo_import']['first_date']))

    # If no date is supplied to the script, sync the db with all dates currently not already in the db.
    if not date:
        _clear_buffer()
        db.test.buffer.drop()

        uploaded_dates = db.meta.find_one({'type': 'dates'})['uploaded_dates']
        today_date = datetime.date.today()
        date_diff = today_date - first_date
        for i in range(date_diff.days):
            current_date = first_date + datetime.timedelta(i)
            current_date_str = "{:%Y%m%d}".format(current_date)
            if not current_date_str in uploaded_dates:
                update_db_with_tests(current_date)
                uploaded_dates.append(current_date_str)

    # Else load the date that was supplied in the cli unless it is already in the db.
    else:
        _clear_buffer()
        db.test.buffer.drop()

        uploaded_dates = db.meta.find_one({'type': 'dates'})['uploaded_dates']
        current_date_str = "{:%Y%m%d}".format(date)
        if not current_date_str in uploaded_dates:
            update_db_with_tests(date)
            uploaded_dates.append(current_date_str)

    # Update the meta table with the most recent imported date.
    uploaded_dates = db.meta.find_one({'type': 'dates'})['uploaded_dates']
    most_recent_date = first_date
    for date in uploaded_dates:
        year = date[0:4]
        month = date[4:6]
        day = date[6:8]
        current_date = datetime.date(int(year), int(month), int(day))
        if current_date > first_date:
            most_recent_date = current_date

    db.meta.update({'type': 'dates'}, {'$set': {'latest_imported_date': "{:%Y%m%d}".format(most_recent_date)}},
                   upsert=True, multi=True)

    log.info("Finished importing tests to mongodb!")


if __name__ == "__main__":
    main(sys.argv[1:])