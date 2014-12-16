from log import config_decorator


# Implements the geometry pass-fail rule based on number of handsets and carriers in this geometry
def geo_pass(key):
    """
    Implement the geometry pass-fail rule.

    The geometry will pass the test if there is more than one carrier in the geometry, or there is more than 1 handset.

    Args:
        key - The key emitted during mapping phase.
    Returns:
        True if the geometry passes, False otherwise.
    """

    if key['geo_id'] == "national":
        return True

    bin = key['bin']

    if bin:
        handsets = bin['handsets']
        carriers = bin['carriers']
        if carriers < 2:
            if handsets < 2:
                return False

    return True


def apply_version_rules(results, test):
    """
    Remove the upload result from results if the app version for the test is 1.116 or 1.118.
    """

    if test['app_version_name'] in ('1.116', '1.118',):
        results.update({'upload': None})


@config_decorator
def _apply_rules(aggregation, key, _config=None, db=None, log=None):
    """
    Apply the various aggregation rules to this aggregation.

    Entry point for all the privacy routines during map-reduce.

    Args:
        aggregation - The aggregation to apply the privacy rules to.
        key - The key emitted for this aggregation during the mapping phase.
    Returns:
        The original aggregation if the geometry passes, the aggregation with all metrics except for participation
        blanked out otherwise.
    """

    if 'bin' in key:
        participation = key['bin']['participation'][key['carrier']]

        if not geo_pass(key) or \
                aggregation['total']['download']['participation'] < int(_config['privacy']['size_a']):
            return None

        aggregation = _blank_results([time_frame for time_frame in aggregation], aggregation)

    return aggregation


@config_decorator
def _blank_results(time_frames, aggregation, _config=None, db=None, log=None):
    """
    Blank out all metrics for this aggregation except for participation.

    Returns:
        The aggregation with blanked out metrics.
    """

    for time_frame in time_frames:
        for metric in ('download', 'upload', 'latency', 'packet_loss',):
            if aggregation[time_frame][metric]['participation'] < int(_config['privacy']['size_b']):
                aggregation[time_frame][metric].update({'min': None})
                aggregation[time_frame][metric].update({'max': None})
                aggregation[time_frame][metric].update({'average': None})
                aggregation[time_frame][metric].update({'median': None})
                if aggregation[time_frame][metric]['participation'] < int(_config['privacy']['size_a']):
                    aggregation[time_frame][metric].update({'participation': 0})

    return aggregation


@config_decorator
def insert_test(aggregation, key, _config=None, db=None, log=None):
    """
    Insert the aggregation and key into the database.
    """

    if aggregation:
        id = key
        if 'bin' in id:
            bin = id['bin']
            geo = db.geo[bin['geo_type']].find_one({'geo_id': bin['geo_id']})
            try:

                bin.update({'geometry': geo['geometry']})
            except KeyError:
                bin.update({'geometry': None})
            del id['bin']

            db[_config['vizmo_python']['aggregations_mongo_from']].insert({'id': id, 'value': aggregation,
                                                                           'bbox': geo['bbox'],
                                                                           'geometry': bin['geometry'],
                                                                           'properties': bin['properties'],
                                                                           'type': bin['type']})

        # The national bin will be missing some fields and must be formatted separately.
        else:
            db[_config['vizmo_python']['aggregations_mongo_from']].insert({'id': id, 'value': aggregation})