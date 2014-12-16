function()
{
    var hex_pass = true;
    if (this.carriers.length < 2)
    {
        if (this.handsets.length < 2)
        {
            hex_pass = false;
        }
    }

    if (hex_pass)
    {
        for(var x = 0; x < this.tests.length; x++)
        {
            if (this.tests[x].network_type.active_network_type === "WIFI") continue;

            var test = this.tests[x];

            var date = new Date(Number(this.tests[x].timestamp) * 1000);
            date.setHours(date.getHours() + Number(this.tests[x].timezone));

            var day_str = "";
            var month_str = "";
            day_str = day_str + date.getFullYear().toString();
            month_str = month_str + date.getFullYear().toString();

            if ((date.getMonth() + 1) < 10)
            {
                day_str = day_str + "0";
                month_str = month_str + "0";
            }
            day_str = day_str + (date.getMonth() + 1).toString();
            month_str = month_str + (date.getMonth() + 1).toString();

            if (date.getDate() < 10)
            {
                day_str = day_str + "0";
            }
            day_str = day_str + date.getDate().toString();

            var empty = {'download': [], 'upload': [], 'latency': [], 'packet_loss': []};
            var hourly = {};

            for(var index = 0; index < 24; index++)
            {
                hourly[index.toString()] = {'download': [], 'upload': [], 'latency': [], 'packet_loss': []};
            }

            var result = {'download': [], 'upload': [], 'latency': [], 'packet_loss': []};
            result.download.push(Number(test.download_test.download_speed));
            result.upload.push(Number(test.upload_test.upload_speed));
            result.latency.push(Number(test.latency_test.rtt_avg));
            result.packet_loss.push(Number(test.latency_test.lost_packets));

            var hour = date.getHours();
            hourly[hour.toString()] = {'download': result.download, 'upload': result.upload, 'latency': result.latency,
                                        'packet_loss': result.packet_loss};

            var value = {};
            value.hourly = hourly;
            value.total = result;

            var key = {};
            key.geo_id = this.geo_id;
            key.carrier_name = "Combined";
            key.carrier_id = key.carrier_name.toLowerCase();
            key.time = "Total";
            key.date = "Total";
            key.geo_type = this.geo_type;

            // Also build a key for the nation-wide aggregations
            var key_national = {};
            key_national.geo_id = "National";
            key_national.carrier_name = "Combined";
            key_national.carrier_id = key_national.carrier_name.toLowerCase();
            key_national.time = "Total";
            key_national.date = "Total";
            key_national.geo_type = this.geo_type;

            // Determine if this date was during the weekend or not
            if (date.getDay() === 0 || date.getDay() === 6)
            {
                value.weekend = result;
                value.weekday = empty;
            } else
            {
                value.weekday = result;
                value.weekend = empty;
            }

            // Determine if this date was during peak time or not
            if (((date.getHours() >= 7 && date.getHours() <= 9) || (date.getHours() >= 16 && date.getHours() <= 19)) &&
                (!(date.getDay() === 0 || date.getDay() === 6)))
            {
                value.onpeak = result;
                value.offpeak = empty;
            } else
            {
                value.offpeak = result;
                value.onpeak = empty;
            }

            // Emit the most general key-value pair for this test (carrier, time, and date all = Total)
            emit(key, value);
            emit(key_national, value);

            key.time = "Monthly";
            key_national.time = "Monthly";
            key.date = month_str;
            key_national.date = month_str;

            // Emit with the month for this test
            emit(key, value);
            emit(key_national, value);

            key.time = "Daily";
            key_national.time = "Daily";
            key.date = day_str;
            key_national.date = day_str;

            // Emit with the day for this test
            emit(key, value);
            emit(key_national, value);

            key.carrier_name = this.tests[x].network_operator;
            key_national.carrier_name = this.tests[x].network_operator;
            key.carrier_id = key.carrier_name.toLowerCase();
            key_national.carrier_id = key_national.carrier_name.toLowerCase();
            if (key.carrier_id == "at&t")
            {
                key.carrier_id = "att";
                key_national.carrier_id = "att";
            }
            if (key.carrier_id == "t-mobile")
            {
                key.carrier_id = "tmobile";
                key_national.carrier_id = "tmobile";
            }
            key.time = "Total";
            key_national.time = "Total";
            key.date = "Total";
            key_national.date = "Total";

            // Emit with the carrier for this test
            emit(key, value);
            emit(key_national, value);

            key.time = "Monthly";
            key_national.time = "Monthly";
            key.date = month_str;
            key_national.date = month_str;

            // Emit with the carrier and month for this test
            emit(key, value);
            emit(key_national, value);

            key.time = "Daily";
            key_national.time = "Daily";
            key.date = day_str;
            key_national.date = day_str;

            // Emit with the carrier and day for this test
            emit(key, value);
            emit(key_national, value);

        }
    }
}