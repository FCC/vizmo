Application Requirements
========================

This document will provide essential information for setting up the NodeJS part of the Vizmo App.


## Prerequisites
The following is required for NodeJS Api and NodeJS Web App.

- [Python 2.7.8+ [1]](https://www.python.org/download/releases/2.7.8/)
- [NodeJS 0.10.28+ [1]](http://nodejs.org/download/)

[1] Make sure you have admin rights on your machine when you install these applications. Also see ` Troubleshooting ` section at the bottom of the page.

## Module requirements
The following modules are used:

- [js2xmlparser](https://github.com/michaelkourlas/node-js2xmlparser): ~0.1.3
- [mongodb](http://mongodb.github.io/node-mongodb-native/): ~1.4.7
- [mongojs](https://github.com/mafintosh/mongojs): ~0.13.0
- [restify](http://mcavage.me/node-restify/): ^2.8.1

last update: 08/27/2014

## Setting the Github repo localy

Clone the repo:

    git clone https://github.com/FCC/vizmo.git

Set the user credentials:

    git config user.name "Joe Smith"
    git config user.email "joe.smith@fcc.gov"

Set the SSH user/pass (git commands will stop asking you for your user/pass):

    git remote set-url origin https://joe:password@github.com/FCC/vizmo.git

Switch to `node-js` branch:

    git checkout node-js

[More on the Git for this app](https://github.com/FCC/vizmo/blob/docs/git.md)

## Localhost Installation
After confirming that ` python ` and ` nodejs ` are installed and PATHs are properly set, run the following in the repo folder of the ` node-js ` branch.

    npm install

This will install all modules and sub-module dependencies.

Example output:

![example](images/package-json-install.png)

You can ignore the errors for the NodeJS module: ` node-gyp `. It is used by ` restify ` for building submodules. The app is not using that submodule.

**Note:** The app specific module installation should be done through [package.json](https://github.com/FCC/vizmo/blob/docs/package-json.md) and ` npm install `.<br/> Only the utilities and process managers should be done through global module installation.

## Running the App
Checkout [--watch setup document](https://github.com/FCC/vizmo/blob/docs/localhost--watch-setup.md) if you'd like to have the `jekyll --watch` equivalent for your node app.
Otherwise you can run the app with:

    node rest.js

Once the app is launched you will see the output:

    vizmo listening at http://127.0.0.1:8080

## Configuration File
Checkout the [configuration setup for this app](https://github.com/FCC/vizmo/blob/docs/config-nodejs.md).

## Deployment
Checkout the [deployment instructions through git](https://github.com/FCC/vizmo/blob/docs/deployment.md).

<br><br><br>

# Troubleshooting FAQ

- Node doesn't install on my machine

    ` Make sure you have admin rights on your machine `

- NPM doesn't work in all folders

    ` Make sure the NPM folders are included in the PATH of your machine (also requires admin rights) `

- NPM is reporting an error ` can't create a folder in c:\USERS\ .... \npm `

    ` Confirm the mentioned above folder exists. If it doesn't, create it. In most cases it solves the problem. `
