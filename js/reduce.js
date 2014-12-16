function(key, values)
{
    var results = {};
    results.total = {"download": [], "upload": [], "latency": [], "packet_loss": []};
    results.weekend = {"download": [], "upload": [], "latency": [], "packet_loss": []};
    results.weekday  = {"download": [], "upload": [], "latency": [], "packet_loss": []};
    results.onpeak = {"download": [], "upload": [], "latency": [], "packet_loss": []};
    results.offpeak = {"download": [], "upload": [], "latency": [], "packet_loss": []};

    var hourly = {};
    for (var x = 0; x < 24; x++)
    {
        hourly[x.toString()] = {};
        hourly[x.toString()].download = [];
        hourly[x.toString()].upload = [];
        hourly[x.toString()].latency = [];
        hourly[x.toString()].packet_loss = [];
    }

    var set_values_func = function(aggregation)
    {
        if (values[i][aggregation].download.length > 0)
        {
            for(var index = 0; index < values[i][aggregation].download.length; index++)
            {
                results[aggregation].download.push(values[i][aggregation].download[index]);
            }
        }
        if (values[i][aggregation].upload.length > 0)
        {
            for(var index = 0; index < values[i][aggregation].upload.length; index++)
            {
                results[aggregation].upload.push(values[i][aggregation].upload[index]);
            }
        }
        if (values[i][aggregation].latency.length > 0)
        {
            for(var index = 0; index < values[i][aggregation].latency.length; index++)
            {
                results[aggregation].latency.push(values[i][aggregation].latency[index]);
            }
        }
        if (values[i][aggregation].packet_loss.length > 0)
        {
            for(var index = 0; index < values[i][aggregation].packet_loss.length; index++)
            {
                results[aggregation].packet_loss.push(values[i][aggregation].packet_loss[index]);
            }
        }
    };

    for (var i = 0; i < values.length; i++)
    {
        set_values_func("total");
        set_values_func("weekend");
        set_values_func("weekday");
        set_values_func("onpeak");
        set_values_func("offpeak");
        for (var index = 0; index < 24; index++)
        {
            for (var x = 0; x < values[i]["hourly"][index.toString()]['download'].length; x++)
            {
                hourly[index.toString()].download.push(Number(values[i]["hourly"][index.toString()]["download"][x]));
            }
            for (var x = 0; x < values[i]["hourly"][index.toString()]['upload'].length; x++)
            {
                hourly[index.toString()].upload.push(Number(values[i]["hourly"][index.toString()]["upload"][x]));
            }
            for (var x = 0; x < values[i]["hourly"][index.toString()]['latency'].length; x++)
            {
                hourly[index.toString()].latency.push(Number(values[i]["hourly"][index.toString()]["latency"][x]));
            }
            for (var x = 0; x < values[i]["hourly"][index.toString()]['packet_loss'].length; x++)
            {
                hourly[index.toString()].packet_loss.push(Number(values[i]["hourly"][index.toString()]["packet_loss"][x]));
            }
        }
    }

    return {"total": results.total, "weekend": results.weekend, "weekday": results.weekday,
            "onpeak": results.onpeak, "offpeak": results.offpeak, "hourly": hourly};
}