/*

    test.js
    - node version
    - required modules installed
    - connection to mongodb
    - checks if PM2 is installed

*/

    console.log('\n\n');

//  check the node version
    var nodev = process.versions['node'];
    var reqNodeV = ['0', '10', '28'];
    var nv = nodev.split(".");

    if (nv[0] == reqNodeV[0] && nv[1] == reqNodeV[1] && nv[2] >= reqNodeV[2])
    {
        console.log(" OK · Node version confirmed.");
    } else {
        console.log(" Node version incorrect");
        console.log(" Version required => " + reqNodeV[0] + '.' + reqNodeV[1] + '.' + reqNodeV[2]);
        console.log(" Version found: " + nodev + '\n');
    }

//  read the package.json and get the modules list. check if they are installed
    var fs = require('fs');
    var obj1 = JSON.parse(fs.readFileSync('package.json', 'utf8'));
    var modules = obj1['dependencies'];
    var noModules = Object.keys(modules).length; // expected number of modules
    var missingModules = 0;
    var b;

    Object.keys(modules).forEach(function(key) {
        var val = modules[key];

        try {
            console.log(' OK · ' + key + ' found in: ' + require.resolve(key));
        } catch(e) {
            console.error(' FAIL · ' + key + ' is missing.');
            missingModules++;
            //process.exit(e.code);
        }

    });


//  check if we can connect the mongodb ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    var mongojs = require('mongojs');
    var appConfig = require("./appConfig");
    var configInfo = new appConfig();

    var conn = configInfo.mongoConn;

    try {
        var db = mongojs(conn, ['db_mmba']);
        //console.log(db);
        if (db['_name'].length > 0)
        {
            console.log(' OK · MongoDB connection confirmed');
        }
    } catch(e) {
        console.error(" FAIL · Error with MongoDB connection:\n" + e);
    }

// all done
    console.log('\n\n');

    if (missingModules > 0)
    {
        console.log('Modules missing !!!\nRun npm install !!!');
        console.log('\n\n');
    }
