function(key, value)
{
    var results = {};
    var undef = {"download": {"median": undefined, "average": undefined, "min": undefined, "max": undefined,
                 "participation": 0},
                 "upload": {"median": undefined, "average": undefined, "min": undefined, "max": undefined,
                 "participation": 0},
                 "latency": {"median": undefined, "average": undefined, "min": undefined, "max": undefined,
                 "participation": 0},
                 "packet_loss": {"median": undefined, "average": undefined, "min": undefined, "max": undefined,
                 "participation": 0}};
    results.total = undef;
    results.weekend = undef;
    results.weekday = undef;
    results.onpeak = undef;
    results.offpeak = undef;
    results.hourly = {};

    for (var i = 0; i < 23; i++)
    {
        results.hourly[i.toString()] = {"download": undefined, "upload": undefined, "latency": undefined,
                                        "packet_loss": undefined};
    }

    if (value.test_results !== null && value.test_results !== undefined)
    {
        results.total = value.test_results.total;
        results.weekend = value.test_results.weekend;
        results.weekday = value.test_results.weekday;
        results.onpeak = value.test_results.onpeak;
        results.offpeak = value.test_results.offpeak;

        // For this aggregation and test category (download, upload, etc) return an object with the median, average,
        // min, and max values. If hour is specified, store this as an hourly aggregation.
        var set_results_help = function(aggregation, test, hour, size_a, size_b)
        {
            var new_results = {};
            var test_results_list;
            if (hour !== undefined)
            {
                test_results_list = value.test_results[aggregation][hour][test];
            } else
            {
                test_results_list = results[aggregation][test];
            }
            test_results_list.sort(function(a, b){ return a - b; });

            if (test_results_list.length < size_a)
            {
                new_results.median = undefined;
                new_results.average = undefined;
                new_results.min = undefined;
                new_results.max = undefined;
                new_results.participation = test_results_list.length;

            } else if (test_results_list.length < size_b)
            {
                new_results.median = -1;
                new_results.average = -1;
                new_results.min = -1;
                new_results.max = -1;
                new_results.participation = test_results_list.length;
            } else
            {
                new_results.median = test_results_list[Math.round(test_results_list.length / 2) - 1];

                var sum = 0;
                for (var i = 0; i < test_results_list.length; i++)
                {
                    sum += test_results_list[i];
                }
                new_results.average = sum / test_results_list.length;

                new_results.min = test_results_list[0];
                new_results.max = test_results_list[test_results_list.length - 1];

                new_results.participation = test_results_list.length;
            }
            return new_results;
        };

        var set_results_func = function(aggregation, size_a, size_b)
        {
            results[aggregation].download = set_results_help(aggregation, "download", undefined, size_a, size_b);
            results[aggregation].upload = set_results_help(aggregation, "upload", undefined, size_a, size_b);
            results[aggregation].latency = set_results_help(aggregation, "latency", undefined, size_a, size_b);
            results[aggregation].packet_loss = set_results_help(aggregation, "packet_loss", undefined, size_a, size_b);
        };

        var size_a = 2;
        var size_b = 10;
        if (key.carrier === "Total" || key.carrier === null)
        {
            size_b = 2;
        }
        if (key.time !== "Total")
        {
            size_a = 1;
            size_b = 1;
        }

        set_results_func("total", size_a, size_b);
        set_results_func("weekend", size_a, size_b);
        set_results_func("weekday", size_a, size_b);
        set_results_func("onpeak", size_a, size_b);
        set_results_func("offpeak", size_a, size_b);

        for (var x = 0; x < 23; x++) {
            if (value.test_results.hourly[x.toString()].download.length > 0)
            {
                results["hourly"][x.toString()].download = set_results_help("hourly", "download", x.toString(), 1, 1);
            }
            if (value.test_results.hourly[x.toString()].upload.length > 0)
            {
                results["hourly"][x.toString()].upload = set_results_help("hourly", "upload", x.toString(), 1, 1);
            }
            if (value.test_results.hourly[x.toString()].latency.length > 0)
            {
                results["hourly"][x.toString()].latency = set_results_help("hourly", "latency", x.toString(), 1, 1);
            }
            if (value.test_results.hourly[x.toString()].packet_loss.length > 0)
            {
                results["hourly"][x.toString()].packet_loss = set_results_help("hourly", "packet_loss", x.toString(), 1, 1);
            }
        }
    } 

    return {"total": results.total, "weekend": results.weekend, "weekday": results.weekday, "onpeak": results.onpeak,
            "offpeak": results.offpeak, "hourly": results.hourly};
}