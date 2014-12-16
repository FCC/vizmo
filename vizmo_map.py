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


import os
import sys
import re

from log import config_decorator
import database


def _single_quote_repl(matchobj):
    """
    Use re.sub to replace single quotes in the output with double quotes.
    """

    if matchobj.group(0) == '\'':
        return '\"'
    else:
        return ""


# Function used with re.sub to replace None outputs with -2 because Tilemill's json backend does not understand None.
def _none_repl(matchobj):
    """
    Use re.sub to replace 'None' with '-2'.
    """

    if matchobj.group(0) == "None":
        return "-2"
    else:
        return ""


@config_decorator
def main(argv, _config=None, db=None, log=None):
    """
    Create new geojson layers for Tilemill using the aggregations in the public database.
    """

    db = database.Connection('public')

    hexes = {}
    hexes.update({"verizon": [], "att": [], "tmobile": [], "sprint": [], "other": [], "combined": []})

    # Remove existing layer files to ensure the data is fully up to date.
    for carrier in hexes.keys():
        try:
            os.remove(_config['vizmo_map']['layers_dir'] + carrier.lower() + ".hex.geojson")
        except IOError:
            pass

    # Add each hex that has results to the hexes dictionary with relevant results attached.
    for results in db[_config['vizmo_python']['aggregations_mongo_to']].find({'id.time': 'total',
                                                                              'id.geo_id': {'$ne': 'national'}}):

        if results['id']['geo_type'] in ('hex5k', 'hex10k', 'hex25k'):

            carrier = results['id']['carrier']
            hex_list = hexes[carrier]

            for time in ('total', 'onpeak', 'offpeak',):
                if int(results['value'][time]['download']['participation']) < int(_config['privacy']['size_a']):
                    results['value'][time]['download']['median'] = -2
                elif int(results['value'][time]['download']['participation']) < int(_config['privacy']['size_b']):
                    results['value'][time]['download']['median'] = -1
                elif not results['value'][time]['download']['median']:
                    results['value'][time]['download']['median'] = -1

            result_set = {}

            result_set.update({'total': results['value']['total']})
            result_set.update({'onpeak': results['value']['onpeak']})
            result_set.update({'offpeak': results['value']['offpeak']})

            if not result_set['total']['download']['median'] and not result_set['onpeak']['download']['median'] and \
                    not result_set['offpeak']['download']['median']:
                continue

            hex = {}
            hex.update({'bbox': results['bbox'], 'geometry': results['geometry'], 'type': results['type'],
                        'properties': results['properties'], 'geo_id': results['id']['geo_id'],
                        'geo_type': results['id']['geo_type']})

            hex['results'] = result_set
            hex_list.append(hex)
            hexes[carrier] = hex_list

    # Create the actual geojson layer files for tilemill.
    for carrier in hexes.keys():
        file = open(_config['vizmo_map']['layers_dir'] + carrier.lower() + ".hex.geojson", "w")
        file.write("{\n")
        file.write("\"type\": \"FeatureCollection\",\n")
        file.write("\"crs\": {\"type\": \"name\", \"properties\": {\"name\": \"urn:ogc:def:crs:OGC:1.3:CRS84\"}},\n")
        file.write("\"features\": [\n")
        try:
            first_hex = hexes[carrier][0]
            hexes[carrier].remove(first_hex)

            first_hex_str = '\"download_total\": {}, \"download_on_peak\": {}, \"download_off_peak\": {}, ' \
                            '\"participation_total\": {}, \"participation_on_peak\": {}, \"participation_off_peak\": ' \
                            '{}' \
                            .format(first_hex['results']['total']['download']['median'],
                                    str(first_hex['results']['onpeak']['download']['median']),
                                    str(first_hex['results']['offpeak']['download']['median']),
                                    str(first_hex['results']['total']['download']['participation']),
                                    str(first_hex['results']['onpeak']['download']['participation']),
                                    str(first_hex['results']['offpeak']['download']['participation']))

            first_hex_str = re.sub(r'\'', _single_quote_repl, first_hex_str)
            first_hex_str = re.sub(r'None', _none_repl, first_hex_str)
            file.write("{\"geo_id\": " + str(first_hex['geo_id']) + ", \"properties\": {" + first_hex_str +
                       ", \"geo_type\": \"" + str(first_hex['geo_type']) + "\"}")
            file.write(", \"geometry\": {\"type\": \"Polygon\", \"coordinates\": " +
                       str(first_hex['geometry']['coordinates']) + "}}")

            for hex in hexes[carrier]:
                hex_str = '\"download_total\": {}, \"download_on_peak\": {}, \"download_off_peak\": {}, ' \
                          '\"participation_total\": {}, \"participation_on_peak\": {}, \"participation_off_peak\": {}' \
                          .format(hex['results']['total']['download']['median'],
                                  str(hex['results']['onpeak']['download']['median']),
                                  str(hex['results']['offpeak']['download']['median']),
                                  str(hex['results']['total']['download']['participation']),
                                  str(hex['results']['onpeak']['download']['participation']),
                                  str(hex['results']['offpeak']['download']['participation']))

                hex_str = re.sub(r'\'', _single_quote_repl, hex_str)
                hex_str = re.sub(r'None', _none_repl, hex_str)
                file.write(",\n" "{\"geo_id\": " + str(hex['geo_id']) + ", \"properties\": {" +
                           hex_str + ", \"geo_type\": \"" + str(hex['geo_type']) + "\"}")
                file.write(", \"geometry\": {\"type\": \"Polygon\", \"coordinates\": " +
                           str(hex['geometry']['coordinates']) + "}}")
        except IndexError:
            pass
        file.write("]}")

if __name__ == "__main__":
    main(sys.argv[1:])
