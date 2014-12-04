Deployment
==========

This document will provide guidelines for deploying the app through Git.

# Step1: Prerequisites
Confirm everything described in [pre-deployment document](https://github.com/FCC/vizmo/blob/docs/pre-deployment.md) is OK.

# Step2: Get the Deployment Code

Go to the folder where you keep the Git code.

Get the latest code:

```bash
$ git pull origin
```

Checkout the AT Deployment

```bash
$ git checkout AT001-2004-09-16
```

# Step 3: Copy the code
Copy the code from `Git Location` to the `App Folder Location`

# Step 4: Install modules
Run the following:
```bash
$ npm install
```

# Step 5: Move Config file (1st deployment only)
Move the `appConfig.js` file from the root of the `App Location` to `../config/vizmo/` folder.

# Step 6: Setup Config file (1st deployment only)
Edit the config file and set the host/user/password/port for MongoDB connection.

Line:
```
self.mongoConn = 'mongo_user:mongo_password@mongo_:1234/db_name'; 
```

# Step 7: Run The Test
Go to the `App Folder Location`.
Run:

```bash
$ node status.js
```

The correct response would have `OK` in front of every check. Example:

```

 	OK · Node version confirmed.
 	OK · js2xmlparser found in: node_modules\js2xmlparser\lib\js2xmlparser.js
 	OK · mongodb found in: node_modules\mongodb\lib\mongodb\index.js
 	OK · mongojs found in: node_modules\mongojs\index.js
 	OK · restify found in: node_modules\restify\lib\index.js
	OK · MongoDB connection confirmed

```

If you get `FAIL` for any of the tests above, **contact developers**

# Step 8: Launch the APP

Run:

```bash
$ pm2 start up.json
```

You should see processes started table similar to this:
![pm2](https://github.com/FCC/vizmo/raw/docs/images/pm2running.png)


# Step 9: Start Monitoring

Run:

```bash
$ pm2 monit
```

You should see a screen similar to this:
![pm2monit](https://raw.githubusercontent.com/unitech/pm2/master/pres/pm2-monit.png)

***