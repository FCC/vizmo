import datetime
import math
import pymongo.errors
import pymongo.collection
from multiprocessing import Process
from multiprocessing import Manager

from privacy import _apply_rules
from privacy import insert_test
import privacy
import util
from log import config_decorator
import config


def _emit(key, value, aggregations):
    """
    Emit the key-value pair into aggregations.
    """

    aggregation = aggregations.get(key, [])
    aggregation.append(value)
    aggregations.update({key: aggregation})


def _build_key(key, key_time, date):
    """
    Build a new key with the fields from a base key and the time and date supplied.

    Args:
        key: Base key.
        key_time: Time to be inserted in the new key.
        date: Date to be inserted in the new key.
    Returns:
        A new key with updated time and date. Note this key is frozen, meaning it is an equivalent tuple. The dictionary
        may be retrieved using the unfreeze_dict function from the util module.
    """

    new_key = {'carrier': key['carrier'], 'geo_group': key['geo_group'], 'geo_id': key['geo_id'],
               'geo_type': key['geo_type'], 'geo_zoom': key['geo_zoom']}
    if 'bin' in key:
        new_key['bin'] = dict(key['bin'])
        new_key['bin'].update({'bbox': None, 'carriers': len(key['bin']['carriers']),
                               'handsets': len(key['bin']['handsets'])})

    new_key.update({'time': key_time, 'date': date})

    new_key = util.freeze_dict(new_key)

    return new_key


def _emit_carrier_wrapper(key, value, aggregations, date, timestamp):
    """
    Windows safe entry point for _emit_carrier.
    """

    _emit_carrier(key, value, aggregations, date, timestamp)


@config_decorator
def _emit_carrier(key, value, aggregations, date, timestamp, _config=None, db=None, log=None):
    """
    Emit the key-value pair for each combination of date range for this carrier into aggregations.

    Uses the base key and date to build specific keys to be emitted. Each built key contains the same fields as the base
    key except for the time field which is set to each of:
        - 'total'
        - 'monthly'
        - 'daily' (NOTE - This is temporarily removed for privacy reasons)

    Args:
        key: The base to use when building more specific permutations.
        value: The value to emit with each key.
        aggregations: The collection to emit each key-value pair into.
        date: The datetime object used to build specific time frame permutations of the base key.
        timestamp: Timestamp for the test, used to timebox the test to the date range specified in the project config.
    """

    timedelta_days = int(_config['mapreduce']['timedelta_days'])
    timedelta_years = int(_config['mapreduce']['timedelta_years'])

    month_str = "{:%Y%m}".format(date)
    day_str = "{:%Y%m%d}".format(date)

    today_day = datetime.date.today()
    test_day = datetime.date.fromtimestamp(timestamp)
    test_delta = today_day - test_day

    if test_delta.days > ((timedelta_years * 365) + timedelta_days):
        return

    if test_delta.days < 0:
        return

    hashable_key = _build_key(key, 'total', 'total')
    _emit(hashable_key, value, aggregations)

    hashable_key = _build_key(key, 'monthly', month_str)
    _emit(hashable_key, value, aggregations)

    # BUG - Daily has been temporarily removed from the non-national aggregations
    # hashable_key = _build_key(key, 'daily', day_str)
    # _emit(hashable_key, value, aggregations)


@config_decorator
def _emit_carrier_national(key, value, aggregations, date, timestamp, _config=None, db=None, log=None):
    """
    Same as emit_carrier for the national binning.
    """

    month_str = "{:%Y%m}".format(date)
    day_str = "{:%Y%m%d}".format(date)

    key.update({'timestamp': timestamp})

    key.update({'time': 'total', 'date': 'total'})
    db.geo.binned.national.insert({'id': key, 'value': value})

    key.update({'time': 'monthly', 'date': month_str})
    db.geo.binned.national.insert({'id': key, 'value': value})

    key.update({'time': 'daily', 'date': day_str})
    db.geo.binned.national.insert({'id': key, 'value': value})


@config_decorator
def map(L, bin, emit_func, _config=None, db=None, log=None):
    """
    For each test, map its result into specific aggregations.

    Aggregations are created by building compound keys containing each category to group by. For example, the key
        {
            geo_id: 5124
            geo_type: hex10k
            geo_group: hex
            geo_zoom: 10
            carrier: combined
            date: 20131211
            time: daily
        }
    will contain all the tests that landed in the 10k hex with id 5124 for any carrier for the specific date December
    10, 2013.

    Args:
        L: An iterable which contains each test. All tests will be for the same bin.
        bin: The bin whose tests are in L.
        emit_func: Function that will emit this test.
    Returns:
        count: The number of tests mapped.
        aggregations: Dictionary with the mapped tests.
    """

    bins_mongo_from = _config['vizmo_python']['bins_mongo_from']

    count = 0
    aggregations = {}

    try:
        bin_meta = db[bins_mongo_from].find_one({'geo_id': bin['geo_id'], 'geo_type': bin['geo_type']})
        bin_geo = db.geo[bin_meta['geo_type']].find_one({'geo_id': bin_meta['geo_id']})
    except TypeError:
        bin_geo = None

    if bin_geo:

        bin_global = {'geo_id': bin['geo_id'], 'geo_type': bin['geo_type'], 'geo_group': bin_meta['geo_group'],
                      'geo_zoom': bin_meta['geo_zoom'], 'bbox': bin_geo['bbox'],
                      'properties': bin_geo['properties'], 'type': bin_geo['type'], 'handsets': bin_meta['handsets'],
                      'carriers': bin_meta['carriers'], 'participation': bin_meta['participation']}

        for entry in L:
            key = {}

            try:
                if bin_global:
                    map_test(entry, bin_global, aggregations, emit_func)

                    count += 1

            except pymongo.errors.OperationFailure:
                continue
                # pass

    return count, aggregations


def map_test(test, bin, aggregations, emit_func):
    """
    Map the given test to aggregations using emit_func.

    Args:
        test: Test to be mapped.
        bin: Bin for this test
        aggregations: Aggregations structure to emit this test to.
        emit_func: Function pointer for a function that will emit this test.
    """

    key = {}
    key.update({'geo_id': bin['geo_id'], 'geo_type': bin['geo_type'],
                'geo_group': bin['geo_group'], 'geo_zoom': bin['geo_zoom']})

    key.update({'bin': bin, 'carrier': 'combined'})

    value = {}
    result = {'download': None, 'upload': None, 'latency': None, 'packet_loss': None}
    empty = {'download': None, 'upload': None, 'latency': None, 'packet_loss': None}

    weekend, weekday, offpeak, onpeak = empty, empty, empty, empty

    # value.update(dict.fromkeys(["hour_" + str(k) for k in range(24)], empty))

    # Append test results to value
    if test.get('download_test', {}).get('success', False):
        if test.get('download_test', {}).get('download_speed', 0):
            result['download'] = float(test['download_test']['download_speed'])

    if test.get('upload_test', {}).get('success', False):
        if test.get('upload_test', {}).get('upload_speed', 0):
            result['upload'] = float(test['upload_test']['upload_speed'])

    if test.get('latency_test', {}).get('success', False):
        if int(test.get('latency_test', {}).get('rtt_avg', 0)) > 0:
            result['latency'] = float(test['latency_test']['rtt_avg'])

        total_packets = int(test['latency_test']['lost_packets'])
        total_packets += int(test['latency_test']['received_packets'])
        packet_loss = int(test['latency_test']['lost_packets']) / total_packets
        packet_loss *= 100
        result['packet_loss'] = packet_loss

    privacy.apply_version_rules(result, test)

    total = result

    test_date = datetime.datetime.utcfromtimestamp(int(test['timestamp']))
    test_date += datetime.timedelta(hours=int(test['timezone']))

    # hour = "hour_" + str(test_date.hour)
    month_str = "{:%Y%m}".format(test_date)
    day_str = "{:%Y%m%d}".format(test_date)

    # value.update({hour: result})

    if test_date.weekday() > 4:
        weekend, offpeak = result, result
    else:
        weekday = result
        if (test_date.hour >= 7 and test_date.hour <= 9) or (test_date.hour >= 16 and test_date.hour <=19):
            onpeak = result
        else:
            offpeak = result

    value.update({'total': total, 'weekday': weekday, 'weekend': weekend, 'onpeak': onpeak,
                  'offpeak': offpeak})

    # Emit the most general key
    emit_func(key, value, aggregations, test_date, int(test['timestamp']))

    key.update({'geo_id': bin['geo_id'], 'bin': bin})

    carrier = util.get_carrier(test['network_operator'])

    key['carrier'] = carrier

    # Emit the carrier specific key
    emit_func(key, value, aggregations, test_date, int(test['timestamp']))


def _map_process_wrapper(bin_queue, reduce_queue, emit_func):
    """
    Windows compatible entry point for the map process.
    """

    _map_process(bin_queue, reduce_queue, emit_func)


@config_decorator
def _map_process(bin_queue, reduce_queue, emit_func, _config=None, db=None, log=None):
    """
    Process for mapping tests into aggregations.

    This is a producer which produces mapped aggregation buckets for the reduce process.

    Args:
        bin_queue: Queue of bins to be mapped.
        reduce_queue: Queue of aggregation buckets to be reduced.
        emit_func: Function to be used when emitting tests.
    """

    while True:
        bin = bin_queue.get()
        if bin is None:
            bin_queue.task_done()
            break
        else:
            print('** ' + str(datetime.datetime.now()) + ' ** ' +
                  str({'geo_id': bin['geo_id'], 'geo_type': bin['geo_type'], 'count': bin['count']}))
            cursor = db.geo.binned.find({'bin.geo_id': bin['geo_id']})

            new_count, new_aggregations = map(cursor, bin, emit_func)
            cursor.close()
            for item in new_aggregations.items():
                reduce_queue.put(item)

            bin_queue.task_done()


def _reduce_process(reduce_queue):
    """
    Process for reducing aggregation buckets into final aggregated statistics.

    This is a consumer which consumes the aggregation buckets from the map process and produces statistics from them
    which go directly back to mongo.

    Args:
        reduce_queue: Queue of aggregation buckets to be reduced.
    """

    while True:
        aggregation = reduce_queue.get()
        if aggregation is None:
            reduce_queue.task_done()
            return
        else:
            reduce(aggregation)
            reduce_queue.task_done()


@config_decorator
def map_queue(limit=None, _config=None, db=None, log=None):
    """
    Perform the map-reduce aggregation for non-national data.

    Args:
        limit (optional) - Limit the number of bins to be aggregated.
    """

    parser = config.Config()

    map_process_count = int(_config['mapreduce']['map_process_count'])
    reduce_process_count = int(parser['mapreduce']['reduce_process_count'])

    bins_mongo_from = parser['vizmo_python']['bins_mongo_from']

    map_processes = []
    reduce_processes = []
    reduce_queue = Manager().JoinableQueue()
    bin_queue = Manager().JoinableQueue()

    for i in range(map_process_count):
        process = Process(target=_map_process_wrapper, args=(bin_queue, reduce_queue, _emit_carrier_wrapper))
        map_processes.append(process)
        process.start()

    for i in range(reduce_process_count):
        process = Process(target=_reduce_process, args=(reduce_queue,))
        reduce_processes.append(process)
        process.start()

    count = 0
    if limit:
        for bin in db[bins_mongo_from].find({'geo_group': 'hex'}).limit(limit):
            bin.update({'count': count})
            bin_queue.put(bin)
            count += 1
    else:
        for bin in db[bins_mongo_from].find({'geo_group': 'hex'}):
            bin.update({'count': count})
            bin_queue.put(bin)
            count += 1

    # Place poison pills at the end of the bin_queue to end the map processes.
    for process in map_processes:
        bin_queue.put(None)

    for process in map_processes:
        process.join()

    # Place poison pills at the end of the reduce_queue to end the reduce processes.
    for process in reduce_processes:
        reduce_queue.put(None)

    for process in reduce_processes:
        process.join()


@config_decorator
def _aggregation_process(aggregation_queue, _config=None, db=None, log=None):
    """
    Worker process which pulls aggregation "buckets" from a queue and queries Mongo for the data and then reduces the
    bucket using the reduce method.
    """

    timedelta_days = int(_config['mapreduce']['timedelta_days'])
    timedelta_years = int(_config['mapreduce']['timedelta_years'])

    test_delta = datetime.timedelta(days=(timedelta_years * 365) + timedelta_days)
    today_day = datetime.date.today()
    test_day = today_day - test_delta
    test_day_str = "{:%Y%m%d}".format(test_day)
    timestamp = datetime.datetime(year=test_day.year, month=test_day.month, day=test_day.day).timestamp()

    while True:
        aggregation = aggregation_queue.get()
        if aggregation is None:
            aggregation_queue.task_done()
            break
        else:
            id = {'geo_id': 'national', 'geo_type': 'hex5k', 'geo_group': 'hex', 'geo_zoom': 12}
            date = aggregation[0]
            carrier = aggregation[1]

            if date < test_day_str:
                continue

            if date in ('total',):
                time = 'total'
            elif len(date) in (6,):
                time = 'monthly'
            else:
                time = 'daily'

            id.update({'date': date})
            id.update({'carrier': carrier})
            id.update({'time': time})

            flat_id = util.freeze_dict(id)
            tests = []

            for test in db.geo.binned.national.find({'id.date': date, 'id.time': time, 'id.carrier': carrier,
                                                     'id.timestamp': {'$gt': timestamp}}):
                tests.append(test['value'])

            if len(tests) >= 10:
                aggregation = (flat_id, tests,)
                print(id)
                reduce(aggregation)


def _aggregation_process_wrapper(aggregation_queue):
    """
    Windows compatible entry point for the national aggregation process.
    """

    _aggregation_process(aggregation_queue)


@config_decorator
def aggregation_national(_config=None, db=None, log=None):
    """
    Compute the national aggregations using geo.binned.national. This works similarly to the non-national aggregations,
    the primary difference is that it uses pre-mapped entries stored in Mongo rather than mapping each test directly in
    memory.
    """

    aggregation_queue = Manager().JoinableQueue()

    carriers = ['att', 'combined', 'other', 'sprint', 'tmobile', 'verizon']

    for carrier in carriers:
        processes = []
        for i in range(int(_config['mapreduce']['aggregation_process_count'])):
            process = Process(target=_aggregation_process_wrapper, args=(aggregation_queue,))
            processes.append(process)
            process.start()

        dates = db.geo.binned.national.find({'id.carrier': carrier}).distinct('id.date')
        for date in dates:
            aggregation_queue.put((date, carrier,))

        for process in processes:
            aggregation_queue.put(None)

        for process in processes:
            process.join()


@config_decorator
def _rebin_national(_config=None, db=None, log=None):
    """
    Recreate the geo.binned.national collection from scratch using existing geo.binned collection.
    """

    db.geo.binned.national.drop()
    db.geo.binned.national.create_index([('id.carrier', pymongo.ASCENDING), ('id.time', pymongo.ASCENDING),
                                         ('id.date', pymongo.ASCENDING), ('id.timestamp', pymongo.ASCENDING)])

    for test in db.geo.binned.find():
        if test['bin']['geo_type'] in (_config['mapreduce']['bins_mongo_from'],):
            bin = db[_config['vizmo_python']['bins_mongo_from']].find_one({'geo_id': test['bin']['geo_id']})
            if bin:
                map_test(test, bin, {}, _emit_carrier_national)


def reduce(L):
    """
    Reduce the list of results for each aggregation down into average, median, min, and max for each metric type.

    Note this function is run in a multiprocessing pool.

    Args:
        L: A tuple containing one key: values pair from the output of map.
    Returns:
        None. Each completed aggregation is pushed directly back to the database.
    """

    key = util.unfreeze_dict(L[0])
    aggregation = L[1]

    try:
        aggregation = _array_reduce(_array_fold, aggregation)
        aggregation = _metric_reduce(_metric_fold, [aggregation])
        if not key['geo_id'] in ('national',):
            aggregation = _apply_rules(aggregation, key)

        if aggregation:
            insert_test(aggregation, key)

    except KeyError:
        return None

    return None


def _array_reduce(function, iterable):
    """
    Reduce the list of results into lists of results for each specific time-frame and metric.

    Calls function for each entry in iterable. This function iteratively folds each metric from the current result into
    the metric lists.

    Args:
        function: The function to be used for folding over each metric.
        iterable: An iterable over the data in the results list.
    Returns:
        A dictionary with a metric list for each metric type.
    """

    it = iter(iterable)

    aggregations = {}
    for key in iterable[0].keys():
        aggregations.update({key: {'download': [], 'upload': [], 'latency': [], 'packet_loss': []}})

    # For each result in the results list, call array_fold for each time-frame aggregation.
    for x in it:
        for key in x.keys():
            aggregations[key] = function(aggregations[key], x[key])

    return aggregations


def _array_fold(aggregation, results):
    """
    Fold the results into aggregation.

    Args:
        aggregation: A dictionary containing a specific time-frame (total, onpeak, etc) and the list of results for that
                     time-frame.
        results: download, upload, latency, and packet loss results to be folded.
    Returns:
        The updated aggregation dictionary.
    """

    for key in results.keys():
        try:
            results_list = aggregation[key]

            if results[key] is None:
                continue
            result = float(results[key])

            results_list.append(result)

            aggregation[key] = results_list
        except AttributeError:
            pass

    return aggregation


def _metric_reduce(function, iterable):
    """
    Reduce the results for each time-frame and metric into compiled statistics.

    Uses the list stored for each metric for each time-frame to compute the average, median, min, and max.

    Args:
        function: The function to be called to compile the statistics.
        iterable: An iterable over the results list. Note that by this point there will only be one result.
    Returns:
        A dictionary containing the compiled statistics.
    """

    it = iter(iterable)

    aggregations = {}
    for key in iterable[0].keys():
        aggregations.update({key: {'download': None, 'upload': None, 'latency': None, 'packet_loss': None}})

    for x in it:
        for key in x.keys():
            aggregation = aggregations[key]
            function(aggregation, x[key])

    return aggregations


def _metric_fold(aggregation, results):
    """
    Reduce the array of results into average, median, min, and max.

    Args:
        aggregation: A dictionary containing the array of metrics for a specific time-frame (total, onpeak, etc).
        results: download, upload, latency, and packet loss arrays.
    Returns:
        A dictionary with the time-frame and compiled statistics for that time-frame.
    """

    for key in results.keys():
        try:
            minimum, maximum, median, average, participation, std, percentile = compute_stats(results[str(key)])

            results_dict = {'average': average, 'median': median, 'min': minimum, 'max': maximum,
                            'participation': participation, 'percentile': percentile}

            aggregation[str(key)] = results_dict

        except AttributeError:
            pass
        except KeyError:
            pass

    return aggregation


def compute_stats(results):
    """
    Produce aggregate statistics for the given result set.

    Args:
        results - List of results to produce statistics for.
    Returns:
        minimum - Minimum value from the results.
        maximum - Maximum value from the results.
        median - Median value for the results.
        average - Mean value for the results.
        participation - Number of values in the results. Defaults to 0.
        std - Currently unused, will always be None.
        percentile - Dictionary containing the 0, 10, 25, 50, 75, 90, and 100 percentile for the results.
    """

    empty_percentile = {'percentile_0': None, 'percentile_10': None, 'percentile_25': None, 'percentile_50': None,
                        'percentile_75': None, 'percentile_90': None, 'percentile_100': None}

    minimum, maximum, median, average, participation, std, percentile = None, None, None, None, 0, None, \
                                                                        empty_percentile
    if len(results):
        results_list = sorted(results)
        if len(results) % 2 in (0,):
            median = (results_list[int(math.floor((len(results_list) - 1) / 2))] +
                      results_list[int(math.ceil((len(results_list) - 1) / 2))]) / 2
        else:
            median = results_list[int(math.floor((len(results_list) - 1) / 2))]
        average = sum(results_list) / len(results_list)
        minimum = results_list[0]
        maximum = results_list[len(results_list) - 1]
        participation = len(results_list)
        if len(results_list) >= 10:
            std = util.get_std(results_list)
            percentile.update({'percentile_0': minimum})
            percentile.update({'percentile_10': util.get_percentile(results_list, 10)})
            percentile.update({'percentile_25': util.get_percentile(results_list, 25)})
            percentile.update({'percentile_50': median})
            percentile.update({'percentile_75': util.get_percentile(results_list, 75)})
            percentile.update({'percentile_90': util.get_percentile(results_list, 90)})
            percentile.update({'percentile_100': maximum})

    return minimum, maximum, median, average, participation, std, percentile


@config_decorator
def mapreduce(_config=None, db=None, log=None):
    """
    Entry point for the mapreduce procedure.
    """

    log.info("Mapping tests into aggregations.")

    db[_config['vizmo_python']['aggregations_mongo_from']].drop()
    db[_config['vizmo_python']['aggregations_mongo_from']].create_index([('id.geo_id', pymongo.ASCENDING),
                                                                         ('id.geo_type', pymongo.ASCENDING)],
                                                                        background=True)

    map_queue()
    aggregation_national()

    log.info("Finished calculating the aggregations!")


# TODO Remove this debug code!
# mapreduce()

# _aggregation_national_experimental()
# _map_queue()
# _map_queue_experimental_national()
# _aggregation_national_experimental()