if __name__ in ('__main__',):
    import log
    log.init_new_log()


import datetime

import util
from log import config_decorator


@config_decorator
def update_bins_meta(_config=None, db=None, log=None):
    """
    Update the meta counts for the populated geo bins.
    """

    db.meta.update({'type': 'bins'}, {'$set': {'hex5k': db.geo.bins.find({'geo_type': 'hex5k'}).count(),
                                               'hex10k': db.geo.bins.find({'geo_type': 'hex10k'}).count(),
                                               'hex25k': db.geo.bins.find({'geo_type': 'hex25k'}).count(),
                                               'county': db.geo.bins.find({'geo_type': 'county'}).count(),
                                               'state': db.geo.bins.find({'geo_type': 'state'}).count(),
                                               'metro': db.geo.bins.find({'geo_type': 'metro'}).count()}},
                   upsert=True, multi=True)


@config_decorator
def update_geometries_meta(_config=None, db=None, log=None):
    """
    Update the meta counts for the raw geometries.
    """

    db.meta.update({'type': 'geometries'}, {'$set': {'hex5k': db.geo.hex5k.count(), 'hex10k': db.geo.hex10k.count(),
                                                     'hex25k': db.geo.hex25k.count(), 'county': db.geo.county.count(),
                                                     'state': db.geo.state.count(), 'metro': db.geo.metro.count()}},
                   upsert=True, multi=True)


@config_decorator
def update_tests_meta_experimental(_config=None, db=None, log=None):
    counts = {'raw': {'daily': {}, 'monthly': {}, 'total': 0}, 'valid': {'daily': {}, 'monthly': {}, 'total': 0},
              'binned': {'daily': {}, 'monthly': {}, 'total': 0}, 'type': 'tests'}
    carriers = ['AT&T', 'Other', 'Sprint', 'T-Mobile', 'Verizon']
    geo_types = ('hex5k', 'hex10k', 'hex25k')

    dates = [date for date in db.test.raw.distinct('date') if date]
    months = [month for month in db.test.raw.distinct('month') if month]

    for date in dates:
        counts['raw']['daily'].update({date: db.test.raw.find({'date': date}).count()})

    for month in months:
        counts['raw']['monthly'].update({month: db.test.raw.find({'month': month}).count()})
    counts['raw'].update({'total': db.test.raw.find().count()})

    dates = [date for date in db.test.valid.distinct('date') if date]
    months = [month for month in db.test.valid.distinct('month') if month]

    for date in dates:
        counts['valid']['daily'].update({date: {'total': db.test.valid.find({'date': date}).count()}})
        for carrier in carriers:
            counts['valid']['daily'][date].update({util.get_carrier(carrier):
                                                  db.test.valid.find({'date': date,
                                                                      'network_operator': carrier}).count()})
    for month in months:
        counts['valid']['monthly'].update({month: {'total': db.test.valid.find({'month': month}).count()}})
        for carrier in carriers:
            counts['valid']['monthly'][month].update({util.get_carrier(carrier):
                                                      db.test.valid.find({'month': month,
                                                                          'network_operator': carrier}).count()})
    counts['valid'].update({'total': db.test.valid.find().count()})

    # dates = db.geo.binned.distinct('date')
    dates = [date for date in db.geo.binned.distinct('date') if date]
    months = [month for month in db.geo.binned.distinct('month') if month]

    for date in dates:
        counts['binned']['daily'].update({date: {'total': {'combined': db.geo.binned.find({'date': date}).count()}}})
        counts['binned']['daily'][date].update({'geo': {}})
        for geo_type in geo_types:
            counts['binned']['daily'][date]['geo'].update({geo_type: {}})
            counts['binned']['daily'][date]['geo'][geo_type].update({'combined':
                                                                    db.geo.binned.find({'date': date,
                                                                                        'bin.geo_type':
                                                                                            geo_type}).count()})

        for carrier in carriers:
            counts['binned']['daily'][date]['total'].update({util.get_carrier(carrier):
                                                            db.geo.binned.find({'date': date,
                                                                                'network_operator': carrier}).count()})
            for geo_type in geo_types:
                counts['binned']['daily'][date]['geo'][geo_type].update({util.get_carrier(carrier):
                                                                        db.geo.binned.find({'date': date,
                                                                                            'network_operator': carrier,
                                                                                            'bin.geo_type':
                                                                                                geo_type}).count()})

    for month in months:
        counts['binned']['monthly'].update({month: {'total': {'combined':
                                                              db.geo.binned.find({'month': month}).count()}}})
        counts['binned']['monthly'][month].update({'geo': {}})
        for geo_type in geo_types:
            counts['binned']['monthly'][month]['geo'].update({geo_type: {}})
            counts['binned']['monthly'][month]['geo'][geo_type].update({'combined':
                                                                    db.geo.binned.find({'month': month,
                                                                                        'bin.geo_type':
                                                                                            geo_type}).count()})

        for carrier in carriers:
            counts['binned']['monthly'][month]['total'].update({util.get_carrier(carrier):
                                                            db.geo.binned.find({'month': month,
                                                                                'network_operator': carrier}).count()})
            for geo_type in geo_types:
                counts['binned']['monthly'][month]['geo'][geo_type].update({util.get_carrier(carrier):
                                                                        db.geo.binned.find({'month': month,
                                                                                            'network_operator': carrier,
                                                                                            'bin.geo_type':
                                                                                                geo_type}).count()})

    counts['binned'].update({'total': db.geo.binned.find().count()})

    db.meta.remove({'type': 'tests'})
    db.meta.insert(counts)


@config_decorator
def update_tests_meta(_config=None, db=None, log=None):
    """
    Update the meta counts for the raw, valid, and binned tests.
    """

    # Update the raw test counts
    aggregation = db.test.raw.aggregate([{'$group': {'_id': {'date': '$date'},
                                                     'count': {'$sum': 1}}}], allowDiskUse=True)
    for entry in aggregation['result']:
        update_str = 'raw.daily.' + str(entry['_id']['date'])
        db.meta.update({'type': 'tests'},
                       {'$set': {update_str: entry['count']}},
                       upsert=True, multi=True)

    aggregation = db.test.raw.aggregate([{'$group': {'_id': {'month': '$month'},
                                                     'count': {'$sum': 1}}}], allowDiskUse=True)
    for entry in aggregation['result']:
        update_str = 'raw.monthly.' + str(entry['_id']['month'])
        db.meta.update({'type': 'tests'},
                       {'$set': {update_str: entry['count']}},
                       upsert=True, multi=True)

    aggregation = db.test.raw.aggregate([{'$group': {'_id': {}, 'count': {'$sum': 1}}}], allowDiskUse=True)
    for entry in aggregation['result']:
        db.meta.update({'type': 'tests'}, {'$set': {'raw.total': entry['count']}}, upsert=True, multi=True)

    # Update the valid test counts
    aggregation = db.test.valid.aggregate([{'$group': {'_id': {'date': '$date'},
                                                       'count': {'$sum': 1}}}], allowDiskUse=True)
    for entry in aggregation['result']:
        update_str = 'valid.daily.' + str(entry['_id']['date'])
        db.meta.update({'type': 'tests'},
                       {'$set': {update_str: entry['count']}},
                       upsert=True, multi=True)

    aggregation = db.test.valid.aggregate([{'$group': {'_id': {'month': '$month'}, 'count': {'$sum': 1}}}],
                                          allowDiskUse=True)
    for entry in aggregation['result']:
        update_str = 'valid.monthly.' + str(entry['_id']['month'])
        db.meta.update({'type': 'tests'},
                       {'$set': {update_str: entry['count']}},
                       upsert=True, multi=True)

    aggregation = db.test.valid.aggregate([{'$group': {'_id': {}, 'count': {'$sum': 1}}}], allowDiskUse=True)
    for entry in aggregation['result']:
        db.meta.update({'type': 'tests'}, {'$set': {'valid.total': entry['count']}}, upsert=True, multi=True)

    # Update the binned test counts
    db.geo.binned.aggregate([{'$group': {'_id': {'date': '$date', 'month': '$month',
                                                 'geo_type': '$bin.geo_type', 'geo_id': '$bin.geo_id'},
                                         'count': {'$sum': 1}}},
                             {'$out': 'temp.meta'}], allowDiskUse=True)

    update_tests_meta_help(db.temp.meta, db.meta, {'_id': {'date': '$_id.date'}}, ['time', 'daily'])
    update_tests_meta_help(db.temp.meta, db.meta, {'_id': {'month': '$_id.month'}}, ['time', 'monthly'])
    update_tests_meta_help(db.temp.meta, db.meta, {'_id': {}}, ['total'])
    update_tests_meta_help(db.temp.meta, db.meta, {'_id': {'geo_type': '$_id.geo_type'}}, ['geo', 'total'])
    update_tests_meta_help(db.temp.meta, db.meta, {'_id': {'geo_type': '$_id.geo_type', 'geo_id': '$_id.geo_id'}},
                           ['geo', 'geo id', 'total'])
    update_tests_meta_help(db.temp.meta, db.meta, {'_id': {'geo_type': '$_id.geo_type', 'geo_id': '$_id.geo_id',
                                                           'date': '$_id.date'}}, ['geo', 'time', 'geo id', 'daily'])
    update_tests_meta_help(db.temp.meta, db.meta, {'_id': {'geo_type': '$_id.geo_type', 'date': '$_id.date'}},
                           ['geo', 'time', 'geo id', 'daily', 'total'])
    update_tests_meta_help(db.temp.meta, db.meta, {'_id': {'geo_type': '$_id.geo_type', 'geo_id': '$_id.geo_id',
                                                           'month': '$_id.month'}},
                           ['geo', 'time', 'geo id', 'monthly'])
    update_tests_meta_help(db.temp.meta, db.meta, {'_id': {'geo_type': '$_id.geo_type', 'month': '$_id.month'}},
                           ['geo', 'time', 'geo id', 'monthly', 'total'],)


def update_tests_meta_help(temp_meta, meta, query, category):
    """
    Use the supplied handles to the meta collections as well as the query and category to complete specific counts
    and push the result back to the db.

    Query is used to perform a specific grouping of counts within the temp meta collection, while category is used to
    restructure the result that makes it back to the database.

    args:
        temp_meta - Handle to the temporary meta collection where the most general counts are located.
        meta - Handle to the meta collection to be written back to when finished.
        query - Query used to perform a final specific grouping of counts.
        category - List used to restructure the results.
    """

    query.update({'count': {'$sum': '$count'}})
    aggregation = temp_meta.aggregate([{'$group': query}], allowDiskUse=True)
    update_str = ""
    for entry in aggregation['result']:
        if category in (['time', 'daily'],):
            update_str = 'binned.time.daily.' + str(entry['_id']['date'])
        if category in (['time', 'monthly'],):
            update_str = 'binned.time.monthly.' + str(entry['_id']['month'])
        if category in (['total'],):
            update_str = 'binned.total'
        if category in (['geo', 'total'],):
            update_str = 'binned.geo.' + str(entry['_id']['geo_type']) + '.total.total'
        if category in (['geo', 'geo id', 'total'],):
            update_str = 'binned.geo.' + str(entry['_id']['geo_type']) + '.total.' + str(entry['_id']['geo_id'])
        if category in (['geo', 'time', 'geo id', 'daily'],):
            update_str = 'binned.geo.' + str(entry['_id']['geo_type']) + '.time.daily.' + str(entry['_id']['date']) + \
                         '.' + str(entry['_id']['geo_id'])
        if category in (['geo', 'time', 'geo id', 'daily', 'total'],):
            update_str = 'binned.geo.' + str(entry['_id']['geo_type']) + '.time.daily.' + str(entry['_id']['date']) + \
                         '.total'
        if category in (['geo', 'time', 'geo id', 'monthly'],):
            update_str = 'binned.geo.' + str(entry['_id']['geo_type']) + '.time.monthly.' + str(entry['_id']['month']) \
                         + '.' + str(entry['_id']['geo_id'])
        if category in (['geo', 'time', 'geo id', 'monthly', 'total'],):
            update_str = 'binned.geo.' + str(entry['_id']['geo_type']) + '.time.monthly.' + str(entry['_id']['month']) \
                         + '.total'

        meta.update({'type': 'tests'}, {'$set': {update_str: entry['count']}}, upsert=True, multi=True)


@config_decorator
def update_aggregations_meta(_config=None, db=None, log=None):
    """
    Update the meta counts for the aggregations.
    """

    db[_config['vizmo_tilemill']['aggregations_mongo_to']].aggregate([{'$group':
                                                                      {'_id': {'date': '$id.date',
                                                                               'time': '$id.time',
                                                                               'carrier': '$id.carrier',
                                                                               'geo_type': '$id.geo_type',
                                                                               'geo_id': '$id.geo_id'},
                                                                       'count': {'$sum': 1}}},
                                                                     {'$out': 'temp.meta'}], allowDiskUse=True)

    update_aggregations_meta_help(db.temp.meta, db.meta, {'$match': {'_id.time': 'daily'}},
                                  {'_id': {'date': '$_id.date'}}, ['time', 'daily', None])

    update_aggregations_meta_help(db.temp.meta, db.meta, {'$match': {'_id.time': 'daily'}}, {'_id': {}},
                                  ['time', 'daily', 'total'])

    update_aggregations_meta_help(db.temp.meta, db.meta, {'$match': {'_id.time': 'monthly'}},
                                  {'_id': {'date': '$_id.date'}}, ['time', 'monthly', None])

    update_aggregations_meta_help(db.temp.meta, db.meta, {'$match': {'_id.time': 'monthly'}}, {'_id': {}},
                                  ['time', 'monthly', 'total'])

    update_aggregations_meta_help(db.temp.meta, db.meta, {'$match': {'_id.time': 'total'}}, {'_id': {}},
                                  ['time', 'total', None])

    update_aggregations_meta_help(db.temp.meta, db.meta, None, {'_id': {'geo_type': '$_id.geo_type'}},
                                  ['geo', 'total', None])

    update_aggregations_meta_help(db.temp.meta, db.meta, {'$match': {'_id.time': 'daily'}},
                                  {'_id': {'geo_type': '$_id.geo_type', 'date': '$_id.date'}},
                                  ['geo', 'time', 'daily', None])

    update_aggregations_meta_help(db.temp.meta, db.meta, {'$match': {'_id.time': 'daily'}},
                                  {'_id': {'geo_type': '$_id.geo_type'}}, ['geo', 'time', 'daily', 'total'])

    update_aggregations_meta_help(db.temp.meta, db.meta, {'$match': {'_id.time': 'monthly'}},
                                  {'_id': {'geo_type': '$_id.geo_type', 'date': '$_id.date'}},
                                  ['geo', 'time', 'monthly', None])

    update_aggregations_meta_help(db.temp.meta, db.meta, {'$match': {'_id.time': 'monthly'}},
                                  {'_id': {'geo_type': '$_id.geo_type'}}, ['geo', 'time', 'monthly', 'total'])

    update_aggregations_meta_help(db.temp.meta, db.meta, {'$match': {'_id.time': 'total'}},
                                  {'_id': {'geo_type': '$_id.geo_type', 'date': '$_id.date'}},
                                  ['geo', 'time', 'total', 'total'])

    update_aggregations_meta_help(db.temp.meta, db.meta, None, {'_id': {}}, ['total'])


def update_aggregations_meta_help(temp_meta, meta, match, query, category):
    """
    Use the supplied handles to the meta collections and the match and query and category to complete counts and push
    the results back to the db.

    Match and query are used perform a specific grouping of counts in the temp meta collection, while category is used
    to restructure the result and meta is used to push back to the database.

    Args:
        temp_meta - Handle to the temporary meta collection where the most general counts are located.
        meta - Handle to the meta collection to be written back to when finished.
        match - Used in the aggregation pipeline to trim the results passed to query.
        query - Query used to perform a final specific grouping of counts.
        category - List used to restructure the results.
    """

    query.update({'verizon': {'$sum': {'$cond': {'if': {'$eq': ['$_id.carrier', 'verizon']},
                                                 'then': '$count', 'else': 0}}},
                  'att': {'$sum': {'$cond': {'if': {'$eq': ['$_id.carrier', 'att']},
                                             'then': '$count', 'else': 0}}},
                  'tmobile': {'$sum': {'$cond': {'if': {'$eq': ['$_id.carrier', 'tmobile']},
                                                 'then': '$count', 'else': 0}}},
                  'sprint': {'$sum': {'$cond': {'if': {'$eq': ['$_id.carrier', 'sprint']},
                                                'then': '$count', 'else': 0}}},
                  'other': {'$sum': {'$cond': {'if': {'$eq': ['$_id.carrier', 'other']},
                                               'then': '$count', 'else': 0}}},
                  'combined': {'$sum': {'$cond': {'if': {'$eq': ['$_id.carrier', 'combined']},
                                                  'then': '$count', 'else': 0}}},
                  'total': {'$sum': '$count'}})
    if match:
        aggregation = temp_meta.aggregate([match,
                                           {'$group': query}])
    else:
        aggregation = temp_meta.aggregate([{'$group': query}])

    for entry in aggregation['result']:
        update_str = build_update_str(entry, category)

        meta.update({'type': 'aggregations'},
                    {'$set': {update_str: {'verizon': entry['verizon'], 'att': entry['att'],
                                           'tmobile': entry['tmobile'], 'sprint': entry['sprint'],
                                           'other': entry['other'], 'combined': entry['combined'],
                                           'total': entry['total']}}}, upsert=True, multi=True)


def build_update_str(entry, category):
    if category[0] in ('total',):
        return 'total'
    if category[0] in ('time',):
        if category[1] not in ('daily', 'monthly',):
            return 'time.total'
        elif category[2] in ('total',):
            return 'time.' + category[1] + '.total'
        else:
            return 'time.' + category[1] + '.' + entry['_id']['date']
    if category[0] in ('geo',):
        if category[1] in ('total',):
            return 'geo.' + entry['_id']['geo_type'] + '.total'
        elif category[3] in ('total',):
            if not category[2] in ('daily', 'monthly',):
                return 'geo.' + entry['_id']['geo_type'] + '.time.total'
            else:
                return 'geo.' + entry['_id']['geo_type'] + '.time.' + category[2] + '.total'
        else:
            return 'geo.' + entry['_id']['geo_type'] + '.time.' + category[2] + '.' + entry['_id']['date']


@config_decorator
def update_meta(_config=None, db=None, log=None):
    """
    Update the meta counts for all different types.
    """

    log.info("Updating advanced meta!")

    update_aggregations_meta()
    log.info("Finished updating aggregation meta!")

    update_geometries_meta()
    log.info("Finished updating geometries meta!")

    update_bins_meta()
    log.info("Finished updating bins meta!")

    # update_tests_meta()
    # update_tests_meta_experimental()
    # log.info("Finished updating tests meta!")

    db.temp.meta.drop()

    log.info("Finished updating advanced meta!")


def main(argv):
    update_meta()


if __name__ in ('__main__',):
    main([])
    # update_tests_meta_experimental()