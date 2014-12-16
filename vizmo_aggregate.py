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


import pymongo
import pymongo.errors
import sys
import datetime
import getopt
from multiprocessing import Manager, Process
import time

import util
from bin import bin_decorator, find_bin_func
import mapreduce
from log import config_decorator


@config_decorator
def build_bin_meta(_config=None, db=None, log=None):
    """
    Build the bin meta collection with the set of unique handsets and carriers for that bin as well as participation
    counts divided by carrier.
    """

    # db = database.Connection('private')

    db[_config['vizmo_python']['bins_mongo_from']].drop()
    db[_config['vizmo_python']['bins_mongo_from']].create_index([('geo_id', pymongo.ASCENDING)])
    db[_config['vizmo_python']['bins_mongo_from']].create_index([('geometry', pymongo.GEOSPHERE)])

    count = 0
    size = db.geo.binned.count()

    while count < size:

        group_query = {'$group': {'_id': {'geo_type': '$bin.geo_type',
                                          'geo_id': '$bin.geo_id'},
                                  'verizon': {'$sum': {'$cond': {'if': {'$eq': ['$network_operator', 'Verizon']},
                                                                 'then': 1, 'else': 0}}},
                                  'att': {'$sum': {'$cond': {'if': {'$eq': ['$network_operator', 'AT&T']},
                                                             'then': 1, 'else': 0}}},
                                  'tmobile': {'$sum': {'$cond': {'if': {'$eq': ['$network_operator', 'T-Mobile']},
                                                                 'then': 1, 'else': 0}}},
                                  'sprint': {'$sum': {'$cond': {'if': {'$eq': ['$network_operator', 'Sprint']},
                                                                'then': 1, 'else': 0}}},
                                  'other': {'$sum': {'$cond': {'if': {'$eq': ['$network_operator', 'Other']},
                                                               'then': 1, 'else': 0}}},
                                  'combined': {'$sum': 1},
                                  'handsets': {'$addToSet': '$phone_identity.model'},
                                  'carriers': {'$addToSet': '$network_operator'}}}

        aggregation = db.geo.binned.aggregate([{'$skip': count},
                                               {'$limit': 1000000},
                                               group_query])

        for entry in aggregation['result']:
            geo = db.geo[str(entry['_id']['geo_type'])].find_one({'geo_id': entry['_id']['geo_id']})

            if geo:
                for carrier in ('att', 'combined', 'other', 'sprint', 'tmobile', 'verizon',):
                    db[_config['vizmo_python']['bins_mongo_from']].update({'geo_id': entry['_id']['geo_id']},
                                                                          {'$inc': {'participation.'
                                                                                    + carrier: entry[carrier]}},
                                                                          upsert=True, multi=True)

                for handset in entry['handsets']:
                    db[_config['vizmo_python']['bins_mongo_from']].update({'geo_id': entry['_id']['geo_id']},
                                                                          {'$addToSet': {'handsets': handset}},
                                                                          upsert=True, multi=True)

                for carrier in entry['carriers']:
                    db[_config['vizmo_python']['bins_mongo_from']].update({'geo_id': entry['_id']['geo_id']},
                                                                          {'$addToSet': {'carriers': carrier}},
                                                                          upsert=True, multi=True)

                db[_config['vizmo_python']['bins_mongo_from']].update({'geo_id': entry['_id']['geo_id']},
                                                                      {'$set': {'geometry': geo['geometry'],
                                                                                'geo_type': geo['geo_type'],
                                                                                'geo_zoom': geo['geo_zoom'],
                                                                                'geo_group': geo['geo_group']}},
                                                                      upsert=True, multi=True)

        count += 1000000


@config_decorator
def _bin_test(test, binners, _config=None, db=None, log=None):
    """
    Add this test to the appropriate bins (if any).
    """

    for binner in binners:
        try:
            bin = binner(test)
            if bin:
                test.update({'bin': {'geo_id': bin['geo_id'], 'geo_type': bin['geo_type']}})
                del test['_id']
                db.geo.binned.insert(test)

                handset = test['phone_identity']['model']
                network_operator = test['network_operator']
                carrier = network_operator.lower()

                if carrier in ('at&t',):
                    carrier = 'att'
                if carrier in ('t-mobile',):
                    carrier = 'tmobile'

                inc_fields = {}
                for carrier_str in ('att', 'combined', 'other', 'sprint', 'tmobile', 'verizon',):
                    inc_fields.update({'participation.' + carrier_str: 0})

                inc_fields.update({'participation.combined': 1})
                inc_fields.update({'participation.' + str(carrier): 1})

                try:
                    db[_config['vizmo_python']['bins_mongo_from']].update({'geo_id': bin['geo_id']},
                                                                          {'$addToSet': {'handsets': handset,
                                                                                         'carriers': network_operator},
                                                                           '$inc': inc_fields,
                                                                           '$set': {'geometry': bin['geometry'],
                                                                                    'geo_type': bin['geo_type'],
                                                                                    'geo_group': bin['geo_group'],
                                                                                    'geo_zoom': bin['geo_zoom']}},
                                                                          upsert=True, multi=True)
                except pymongo.errors.DuplicateKeyError:
                    db[_config['vizmo_python']['bins_mongo_from']].update({'geo_id': bin['geo_id']},
                                                                          {'$addToSet': {'handsets': handset,
                                                                                         'carriers': network_operator},
                                                                           '$inc': inc_fields,
                                                                           '$set': {'geometry': bin['geometry'],
                                                                                    'geo_type': bin['geo_type'],
                                                                                    'geo_group': bin['geo_group'],
                                                                                    'geo_zoom': bin['geo_zoom']}},
                                                                          upsert=True, multi=True)

                if bin['geo_type'] in (_config['mapreduce']['geo_type'],):
                    mapreduce.map_test(test, bin, {}, mapreduce._emit_carrier_national)
        except KeyError:
            continue


@config_decorator
def _validate_test(test, binners, _config=None, db=None, log=None):
    """
    Validate this test and add it to test.valid if necessary.
    """

    testid = test['_id']

    if db.test.raw.buffer.remove({'_id': testid})['n'] in (0, ):
        return

    try:
        date = datetime.datetime.utcfromtimestamp(int(test['timestamp']))
        date += datetime.timedelta(hours=int(test['timezone']))
        date_str = "{:%Y%m%d}".format(date)
        month_str = "{:%Y%m}".format(date)
        test.update({'date': date_str, 'month': month_str})

    except KeyError:
        pass
    except ValueError:
        pass
    except OverflowError:
        pass

    try:
        db.test.raw.insert(test)
    except pymongo.errors.DuplicateKeyError:
        return

    if util.is_valid(test):
        test = util.reformat_test(test)

        # Ensure the formatted test is not None (this can happen with an invalid phone identity).
        if test:
            try:
                db.test.valid.insert(test)
            except pymongo.errors.DuplicateKeyError:
                return

            _bin_test(test, binners)


def _bin_test_process_wrapper(bin_queue):
    """
    Windows compatible entry point for the bin test process.
    """

    _bin_test_process(bin_queue)


@config_decorator
def _bin_test_process(bin_queue, _config=None, db=None, log=None):
    """
    Bin the tests in the bin_queue.

    This is a worker process that pulls tests placed on the bin_queue and bins them according to the active bin
    geometries in the project config.
    """

    binners = []

    for geo_type in _config['vizmo_aggregate']:
        # Use the bin decorator to build the appropriate bin method.
        bin_test_func = bin_decorator(find_bin_func, geo_type)
        binners.append(bin_test_func)

    while True:
        test = bin_queue.get()
        if test is None:
            bin_queue.task_done()
            return
        else:
            _validate_test(test, binners)
            bin_queue.task_done()


@config_decorator
def bin_tests(_config=None, db=None, log=None):
    """
    Perform basic validation of incoming raw tests from test.raw.buffer. Insert raw tests into test.raw and insert valid
    tests into test.valid and bin them to geo.binned for various geometries. Once binned, compute final aggregations
    with a call to mapreduce.
    """

    # db = database.Connection('private')

    start_raw = db.test.raw.count()
    start_valid = db.test.valid.count()

    bin_processes = []
    bin_queue = Manager().JoinableQueue()

    for i in range(16):
        process = Process(target=_bin_test_process_wrapper, args=(bin_queue,))
        bin_processes.append(process)
        process.start()

    while db.test.raw.buffer.count() > 0:
        try:
            cursor = db.test.raw.buffer.find().limit(50000)
            for test in cursor:
                bin_queue.put(test)
            while not bin_queue.empty():
                time.sleep(.05)
        except pymongo.errors.CursorNotFound:
            continue

    for process in bin_processes:
        bin_queue.put(None)

    for process in bin_processes:
        process.join()

    latest_uploaded_date = db.meta.find_one({'type': 'dates'})['latest_imported_date']
    db.meta.update({'type': 'dates'}, {'$set': {'latest_binned_date': latest_uploaded_date}}, upsert=True, multi=True)

    end_raw = db.test.raw.count()
    end_valid = db.test.valid.count()

    log.info("" + str(end_raw - start_raw) + " tests added to test.raw!")
    log.info("" + str(end_valid - start_valid) +
             " tests added to test.valid!")

    log.info("Starting aggregation.")

    mapreduce.mapreduce()

    # db.meta.update({'type': 'dates'}, {'$set': {'latest_aggregated_date': latest_uploaded_date}},
    #                upsert=True, multi=True)


def _rebin_test_process_wrapper(bin_queue):
    """
    Windows compatible entry point for the rebin test process.
    """

    _rebin_test_process(bin_queue)


@config_decorator
def _rebin_test_process(bin_queue, _config=None, db=None, log=None):
    """
    Rebin the tests in the bin_queue.

    This is a worker process which pulls the tests placed on the bin_queue and bins them according to the active bin
    geometries in the project config. Because in this scenario the tests have already been validated, this process
    skips the validation step and skips directly to binning.
    """

    binners = []

    for geo_type in _config['vizmo_aggregate']:
        # Use the bin decorator to build the appropriate bin method.
        bin_test_func = bin_decorator(find_bin_func, geo_type)
        binners.append(bin_test_func)

    while True:
        test = bin_queue.get()
        if test is None:
            bin_queue.task_done()
            return
        else:
            _bin_test(test, binners)
            bin_queue.task_done()


@config_decorator
def rebin_tests(_config=None, db=None, log=None):
    """
    Same as bin_tests but rebins the tests contained in test.valid so validation is skipped.
    """

    db.geo.binned.drop()
    db.geo.binned.create_index([('bin.geo_id', pymongo.ASCENDING)])

    db[_config['vizmo_python']['bins_mongo_from']].drop()
    db[_config['vizmo_python']['bins_mongo_from']].create_index([('geo_id', pymongo.ASCENDING)], unique=True)
    db[_config['vizmo_python']['bins_mongo_from']].create_index([('geometry', pymongo.GEOSPHERE)])

    db.geo.binned.national.drop()
    db.geo.binned.national.create_index([('id.carrier', pymongo.ASCENDING), ('id.time', pymongo.ASCENDING),
                                         ('id.date', pymongo.ASCENDING), ('id.timestamp', pymongo.ASCENDING)])

    size = db.test.valid.count()
    current = 0

    bin_processes = []
    bin_queue = Manager().JoinableQueue()

    for i in range(16):
        process = Process(target=_rebin_test_process_wrapper, args=(bin_queue,))
        bin_processes.append(process)
        process.start()

    while current < size:
        try:
            cursor = db.test.valid.find().skip(current).limit(50000)
            for test in cursor:
                current += 1
                bin_queue.put(test)
            while not bin_queue.empty():
                time.sleep(.05)
        except pymongo.errors.CursorNotFound:
            continue

    for process in bin_processes:
        bin_queue.put(None)

    for process in bin_processes:
        process.join()

    latest_uploaded_date = db.meta.find_one({'type': 'dates'})['latest_imported_date']
    db.meta.update({'type': 'dates'}, {'$set': {'latest_binned_date': latest_uploaded_date}}, upsert=True, multi=True)

    log.info("" + str(db.geo.binned.count()) +
             " tests added to the hex bins!")

    mapreduce.mapreduce()


@config_decorator
def main(argv, _config=None, db=None, log=None):
    """
    Bin and aggregate the new tests from Mongo. If rebin is supplied as the option when invoked, rebin and reaggregate
    the tests from test.valid instead.
    """

    try:
        opts, args = getopt.getopt(argv, "", [])
    except getopt.GetoptError:
        print("Usage: vizmo_aggregate.py rebin(optional)")
        sys.exit()

    for opt, arg in opts:
        if opt == "-h":
            print("Usage: vizmo_aggregate.py rebin(optional)")
            sys.exit()

    if args != [] and args != ['rebin']:
        print("Usage: vizmo_aggregate.py rebin(optional)")
        sys.exit()

    log.info("Adding tests to the bins")

    if args == ['rebin']:
        rebin_tests()
    else:
        bin_tests()

    log.info("Finished adding tests to the bins!")


if __name__ == "__main__":
    main(sys.argv[1:])