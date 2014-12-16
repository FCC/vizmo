from pymongo.errors import OperationFailure

import database
import util


def bin_decorator(func, geo_type):
    """
    Create a bin function that bins to a specific geo type and database.

    Args:
        func: The base bin function.
        geo_type: The geo type for the function to bin to.
        db: The database pointer to use.
    Returns:
        The decorated bin function with geometry type and database pointer set.
    """

    def call_func(*args, **kwargs):
        kwargs.update({"geo_type": geo_type})
        kwargs.update({"db": database.Connection('private')})
        return func(*args, **kwargs)
    return call_func


def find_bin_func(test_json, geo_type="", db=database.Connection('private')):
    """
    Find the appropriate bin for this test.

    Args:
        test_json: Input test to be binned.
        test_geo: Geometry of test_json.
        geo_type: Type of geometry this test will be binned to.
        db: Pointer to the database.
    Returns:
        The bin for the test or None if binning failed.
    """

    try:
        test_geo = test_json['geometry']

        if test_json['network_type']['active_network_type'] in ('WIFI',):
            return None

        if not test_json['network_gen'] in ('3G', '4G'):
            return None

        if not util.is_domestic_test(test_json):
            return None

        geo_result = db['geo.' + str(geo_type)].find_one(
            {'geometry': {'$geoIntersects': {'$geometry': test_geo['geometry']}}})
        if geo_result is not None:
            return geo_result

    except OperationFailure:
        print("Warning: Geo binning failed for " + str(test_geo))
        return None

    except KeyError:
        return None
