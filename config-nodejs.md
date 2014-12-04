Config File for NodeJS
======================

## Description

To avoid credentials exposure and to persist the cross-environment code, we are extracting the config file out of the main app folder.

## Format
NodeJS requires include to be utilized as a module exports. To keep the static information we would create a faux object in the form of the function and save it in a javascript file.
The function will be exported as a module.

Example Config File:

    var appConfig = function (){
       var self = this;
       self.ip_addr = 'localhost';
       self.appPort = '8000';
       self.mongoConn = 'zzz:zzz@mong-db:1234/db_name';
    };

    module.exports = appConfig;

Example Main App Usage:

    var appConfig = require("./appConfig");
    var configInfo = new appConfig();

    ...

    var ip_addr = configInfo.ip_addr;
    var port = configInfo.appPort;
    var conn = configInfo.mongoConn;

No need to include the extension when including the config module in the main app.

## Localhost
We can keep the config file in the root of the main app.

## ST/AT/Prod
We will place the config file outside the main app folder and correct the include prefix.

Example:

    var appConfig = require("./appConfig");
    var configInfo = new appConfig();

becomes:

    var appConfig = require("../config/appConfig");
    var configInfo = new appConfig();

In this case the path  `../config/` is not accessible through the web inteface.