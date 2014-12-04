Minify JS/CSS
=============

This document will provide information for Minifying JS/CSS files with NodeJS.

# TL;DR

Place all the JS/CSS files that need to be minified/combined here:

    /web/js.min/*
	/web/css.min/*

Minified files will be stored in:

    /web/js/all.js
    /web/js/all.css

Set the JS/CSS path in index.html to the above files.<br/>
Wildcard is set to pickup any file/folder/file in ` .min ` folders.

**Note:** Any changes to the files require re-running the node


# Requirements

Packages [closure-compiler ^0.2.6](https://github.com/google/closure-compiler) and [node-minify ^0.10.5](https://github.com/srod/node-minify) are required.
 

# NodeJS code

package.json

```JSON

  "dependencies": {
    "js2xmlparser": "~0.1.3",
    "mongodb": "~1.4.7",
    "mongojs": "~0.13.0",
    "closure-compiler": "^0.2.6",
    "node-minify": "^0.10.5",
    "restify": "^2.8.1"
  } 

```

rest.js

```

    compressor = require('node-minify');

    new compressor.minify({
        type: 'uglifyjs',
        fileIn: 'web/js.min/**/*.js',
        fileOut: 'web/js/all.js',
        callback: function(err, min){
            console.log('JS minification errors: ' + err);
        }
    });

    new compressor.minify({
        type: 'clean-css',
        fileIn: 'web/css.min/**/*.css',
        fileOut: 'web/css/all.css',
        callback: function(err, min){
            console.log('CSS minification errors: ' + err);
        }
    });
 
```

Correct output when running node: null errors.

```

vizmo listening at http://127.0.0.1:8080
JS minification errors: null
CSS minification errors: null

```

# Local version onboarding

Remember to run ` npm install ` for the 2 new modules to be installed.
