import datetime
import sys
import getopt
import re
import math
from log import config_decorator


def get_carrier(carrier):
    if carrier in ('AT&T',):
        return 'att'
    if carrier in ('T-Mobile',):
        return 'tmobile'
    if carrier in ('Verizon',):
        return 'verizon'
    if carrier in ('Sprint',):
        return 'sprint'
    if carrier in ('Other',):
        return 'other'
    return ""


def is_valid(test_json):
    """
    Determine the validity of the supplied test.

    Args:
        test_json - The test to be checked.
    Returns:
        True if the test is valid, False otherwise.
    """

    try:

        # Ensure this entry has tests
        if not test_json['tests']:
            return False

        # Ensure all 3 test types are present
        else:
            test_list = []

            for test in test_json['tests']:
                test_list.append(test['type'])

            if not 'JHTTPGETMT' in test_list:
                return False

            if not 'JHTTPPOSTMT' in test_list:
                return False

            if not 'JUDPLATENCY' in test_list:
                return False

        # Ensure this entry has metrics
        if not test_json['metrics']:
            return False

        # Ensure the test has a recorded time.
        if test_json['timestamp'] is None:
            return False

        # Ensure that there is a manufacturer recorded for this entry
        for metric in test_json['metrics']:
            if metric['type'] in ("phone_identity",):
                if not "manufacturer" in metric:
                    return False
                else:
                    break

        # Ensure there is at least one location recorded for this entry
        for metric in test_json['metrics']:
            if metric['type'] == "location":
                return True

    except KeyError:
        return False

    return False


def has_valid_tests(test_json):
    """
    Determine if the supplied test has at least a valid and successful download result.

    Args:
        test_json - The test to be checked.
    Retuns:
        True if the test has a valid download result, False otherwise.
    """

    download_test = test_json['download_test']

    if not float(download_test['bytes_sec']) > 0:
        return False

    if not download_test['success']:
        return False

    return True


def get_network_type(test_json):
    """
    Retrieve the network type from the metrics list.
    """

    for metric in test_json['metrics']:
        if metric['type'] in ('network_data',):
            return metric


def get_phone_identity(test_json):
    """
    Retrieve the phone identity from the metrics list.
    """

    for metric in test_json['metrics']:
        if metric['type'] in ('phone_identity',):
            return metric


def separate_tests(test_json):
    """
    Pull out the various test results from the supplied test and place them in their own subdocuments.

    Args:
        test_json - The test to be used.
    Returns:
        A tuple with the download, upload, and latency test results.
    """

    download_test = {}
    upload_test = {}
    latency_test = {}
    for test in test_json['tests']:
        if test['type'] in ('JUDPLATENCY',):
            latency_test = test
        if test['type'] in ('JHTTPPOSTMT',):
            upload_test = test
        if test['type'] in ('JHTTPGETMT',):
            download_test = test

    download_test.update({"download_speed": float(download_test['bytes_sec']) * 0.000008})
    upload_test.update({"upload_speed": float(upload_test['bytes_sec']) * 0.000008})

    return download_test, upload_test, latency_test


def reformat_test(test_json):
    """
    Restructure the given test.

    Pulls information originally contained in arrays out into separate subdocuments.

    Args:
        test_json - The test to be restructured.
    Returns:
        The modified test.
    """

    test_coords = get_coordinates(test_json)
    test_geo = {'geometry': {'type': 'Point', 'coordinates': test_coords}}

    test_json.update({'geometry': test_geo})

    download_test, upload_test, latency_test = separate_tests(test_json)
    del test_json['tests']
    test_json.update({'download_test': download_test})
    test_json.update({'upload_test': upload_test})
    test_json.update({'latency_test': latency_test})

    network_type = get_network_type(test_json)
    test_json.update({'network_type': network_type})

    phone_identity = get_phone_identity(test_json)
    if not phone_identity:
        return None
    test_json.update({'phone_identity': phone_identity})

    network_gen = retrieve_network_gen(test_json)
    test_json.update({"network_gen": network_gen})

    if phone_identity["manufacturer"] in ("Apple",):
        if network_type['sim_operator_code'] in ('310410', ):
            network_operator = "AT&T"
        elif network_type['sim_operator_code'] in (
                '310160', '310200', '310260', '310270', '310310', '310580', '310660', '310800', '310490'):
            network_operator = "T-Mobile"
        elif network_type['sim_operator_code'] in ('311480', '311489', '31128X', '310VZW'):
            network_operator = "Verizon"
        elif network_type['sim_operator_code'] in ('310120', '311490', '311940', '311870', '310SPR'):
            network_operator = "Sprint"
        else:
            network_operator = "Other"
    else:
        if network_type['network_operator_code'] in ('310410', ):
            network_operator = "AT&T"
        elif network_type['network_operator_code'] in (
                '310160', '310200', '310260', '310270', '310310', '310580', '310660', '310800', '310490'):
            network_operator = "T-Mobile"
        elif network_type['network_operator_code'] in ('311480', '311489', '31128X'):
            network_operator = "Verizon"
        elif network_type['network_operator_code'] in ('310120', '311490', '311940', '311870'):
            network_operator = "Sprint"
        else:
            network_operator = "Other"

    test_json.update({"network_operator": network_operator})
    return test_json


@config_decorator
def retrieve_network_gen(test_json, _config=None, db=None, log=None):
    """
    Match the network type information to 3G or 4G using a set of regexes.

    Args:
        test_json - The test to be matched to network generation.
    Returns:
        '3G', '4G', or None if there is no match.
    """

    regex_dir = _config['util']['regex_dir']

    regexes = open(regex_dir + "3G", "r")
    for regex in regexes:
        regex = regex[0:len(regex) - 1]
        if re.search(regex, test_json['network_type']['network_type']):
            return "3G"

    regexes = open(regex_dir + "4G", "r")
    for regex in regexes:
        regex = regex[0:len(regex) - 1]
        if re.search(regex, test_json['network_type']['network_type']):
            return "4G"


def parse_date(argv):
    """
    Take the input date from the command line and parse it into a datetime object.
    """

    try:
        opts, args = getopt.getopt(argv, "h", [])
    except getopt.GetoptError:
        print("Usage: vizmo_import.py [date](optional) ** Format: YYYYmmdd **")
        sys.exit()

    for opt, arg in opts:
        if opt == "-h":
            print("Usage: vizmo_import.py [date](optional) ** Format: YYYYmmdd **")
            sys.exit()

    if args:
        year = args[0][0:4]
        month = args[0][4:6]
        day = args[0][6:8]
        if not year or not month or not day:
            print("Invalid input date! Please enter a date with the format YYYYmmdd")
            sys.exit()

        try:
            date = datetime.date(int(year), int(month), int(day))

        except ValueError:
            print("Invalid input date! Please enter a date with the format YYYYmmdd")
            sys.exit()

        except TypeError:
            print("Invalid input date! Please enter a date with the format YYYYmmdd")
            sys.exit()

    else:
        date = None

    return date


def get_coordinates(test_json):
    """
    Retrieve the coordinate pair from the metrics list.
    """

    coordinates = []

    for metric in test_json['metrics']:
        if metric['type'] in ('location',):
            coordinates.append(float(str(metric['longitude'])))
            coordinates.append(float(str(metric['latitude'])))
            break

    return coordinates


@config_decorator
def is_domestic_test(test_json, _config=None, db=None, log=None):
    """
    Determine if the input test is a valid domestic test.

    Scans the network_operator_code or sim_operator_code and looks for a specific format, which is specified by a regex.

    Args:
        test_json - The test to scan
    Returns:
        True if the test is from the US, False otherwise.
    """

    regex_dir = _config['util']['regex_dir']

    regexes = open(regex_dir + "US", "r")

    for regex in regexes:
        regex = regex[0:len(regex) - 1]

        if test_json['phone_identity']["manufacturer"] in ('Apple',):
            if not re.search(regex, test_json['network_type']['sim_operator_code']):
                return False
        else:
            if not re.search(regex, test_json['network_type']['network_operator_code']):
                return False

    return True


FROZEN_TAG = "__a__"
FROZEN_LIST = "__b__"


def freeze_dict(obj):
    """
    Flatten the input dictionary into a tuple.

    Args:
        obj - The dictionary to be flattened.
    Returns:
        A tuple representation of obj.
    """

    if isinstance(obj, dict):
        dict_items = list(obj.items())
        dict_items.append((FROZEN_TAG, True))
        return tuple([(k, freeze_dict(v)) for k, v in dict_items])
    if isinstance(obj, list):
        obj.append((FROZEN_LIST, True))
        return tuple([freeze_dict(k) for k in obj])
    return obj


def unfreeze_dict(obj):
    """
    Convert the input tuple back into a dictionary.

    Args:
        obj - The tuple to be unflattened.
    Returns:
        A dictionary representation of obj.
    """

    if isinstance(obj, tuple):
        if (FROZEN_TAG, True) in obj:
            out = dict((k, unfreeze_dict(v)) for k, v in obj)
            del out[FROZEN_TAG]
            return out
        if (FROZEN_LIST, True) in obj:
            out = list(unfreeze_dict(k) for k in obj)
            while (FROZEN_LIST, True) in out:
                out.remove((FROZEN_LIST, True))
            return out
    return obj


def get_mean(l):
    """
    Calculate the mean of a list of numbers.

    Args:

        l: A list of integers and/or floats
    """

    num = len(l)
    if num == 0:
        return None
    else:

        return 1.0*sum(l)/num


def get_median(l):
    """
    Calculate the median of a list of numbers.

    Args:

        l: A list of integers and/or floats
    """

    num = len(l)
    l = sorted(l)

    if num == 0:
        return None
    else:
        if num % 2 == 0:
            n1 = int(num/2)
            n2 = int(n1 - 1)
            median = (l[n1] + l[n2]) / 2.0
        else:
            n = int((num - 1)/2)
            median = l[n]

        return median


def get_std(l):
    """
    Calculate the standard deviation of a list of numbers

    Args:
        l: A list of integers and/or floats.
    """

    num = len(l)

    if num <= 1:
        return None
    else:
        mean = 1.0*sum(l)/num
        sq_sum = 0
        for n in l:
            sq_sum = sq_sum + n*n

        var = (sq_sum/num - mean*mean)*num/(num - 1)
        std = math.sqrt(var)

        return std


def get_error_for_mean(l):
    """
    Calculate the error associated with the estimate of mean value.

    Args:
        l: A list of integers and/or floats.
    """

    num = len(l)

    if num <= 1:
        return None
    else:
        mean = 1.0*sum(l)/len(l)
        sq_sum = 0
        for n in l:
            sq_sum = sq_sum + n*n

        var = (sq_sum/num - mean*mean)/(num - 1)
        std = math.sqrt(var)
        error = std / math.sqrt(num)

        return error


def get_percentile(l, alpha):
    """
    Calculate the percentile value of a list of numbers.

    Args:

        l: A list of integers and/or floats.
        alpha: Percentile (a number from 0 to 100).

    This algorithm is valid only for samples with large enough sizes.
    """

    num = len(l)

    if num == 0:
        return None

    l_sorted = sorted(l)

    i = num*alpha/100.0 - 0.5

    if i < 0:
        n = 0
        x = l_sorted[n]
    elif i == int(i):
        n = int(i)
        x = l_sorted[n]
    else:
        k = int(i)
        if k > num-2:
            k = num - 2
        f = i - k
        x = (1-f)*l_sorted[k] + f*l_sorted[k+1]

    return x