Package.json
============

## Description
Starting from `npm` version 1.0 `package.json` is used for *Dependency management*.
Aside from the basic name/description, this file contains neccessary information to identify and ensure the applicaiton module dependency.
It also keeps the modules inside the application folder vs using the global ones.

*Why is this important?*

We need to make sure that the accidental or purpesful update of the modules does not break the app.

[nodejitsu's visual guide](http://browsenpm.org/package.json)

## Module versioning
The following prefixes are used to ensure the level of module upgrades.

    1.0.0 - Exact version is required
    ~1.0.0 - Allows upgrades from v1.0.0 - v1.0.99
    ^1.0.0 - Allows upgrades from v1.0.0 - v1.99.99
    =>1.0.0 - Will upgrade to latest

## Usage
Instead of running `npm install [module]` for earch module the app requires, from 1.0 setting up the localhost modules is done by running:

    npm install

This will install all modules and sub-module dependencies.

Example output:

![example](images/package-json-install.png)

## Vizmo package.json

    {
      "name": "vizmo",
      "version": "0.1.0",
      "description": "Visualizing Mobile Broadband - Results from the FCC Speed Test",
      "main": "rest.js",
      "scripts": {
        "test": "echo \"Error: no test specified\" && exit 1"
      },
      "repository": {
        "type": "git",
        "url": "git://github.com/FCC/vizmo.git"
      },
      "keywords": [
        "mobile",
        "speedtest",
        "broadband",
        "visualization"
      ],
      "author": "FCC",
      "license": "-",
      "bugs": {
        "url": "https://github.com/FCC/vizmo/issues"
      },
      "homepage": "http://vizmo.fcc.gov/",
      "dependencies": {
        "js2xmlparser": "~0.1.3",
        "mongodb": "~1.4.7",
        "mongojs": "~0.13.0",
        "restify": "^2.8.1"
      }
    }

## Links

- [npm's package.json main page](https://www.npmjs.org/doc/files/package.json.html)
- [Visual guide](http://browsenpm.org/package.json)
- [nodejitsu's Package.json dependencies done righty](http://blog.nodejitsu.com/package-dependencies-done-right/)
- [npm documentation](http://browsenpm.org/help)