Setting up localhost --watch feature
====================================

## Node Package

Module [nodemon](https://github.com/remy/nodemon) allows the same functionality as jekyll's --watch.

## Installation

    npm install -g nodemon

## Usage
To be able to use the --watch feature you need to start the node using the `nodemon` vs directly with node.
Look for the port number in the main app. Vizmo uses 8080 for the localhost.

    nodemon rest.js localhost 8080

![nodemon runing](images/nodemon-running.png)

You terminate the process the same way you would terminate the nodejs.

    CTRL+C

## Mode documentation
More options are available in the module [readme file](https://github.com/remy/nodemon/blob/master/README.md).