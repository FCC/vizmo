/*
   ___  ___   ___         _
  / __\/ __\ / __\ /\   /(_)____ /\/\   ___
 / _\ / /   / /    \ \ / / |_  //    \ / _ \
/ /  / /___/ /___   \ V /| |/ // /\/\ \ (_) |
\/   \____/\____/    \_/ |_/___\/    \/\___/

*/

// Config
var appConfig = require('./appConfig');
var configInfo = new appConfig();

// Require
var restify = require('restify');
var mongojs = require('mongojs');
var js2xmlparser = require('js2xmlparser');

// IP & Port
var ip_addr = configInfo.ip_addr;
var port = configInfo.appPort;

// Create Server
var server = restify.createServer({
    name : 'vizmo',
	version : '0.3.0'
});

server.pre(restify.pre.sanitizePath());

// Server Use
server.use(restify.acceptParser(server.acceptable));
server.use(restify.queryParser());
server.use(restify.gzipResponse());
//server.use(restify.bodyParser());
server.use(restify.jsonp());
server.use(restify.CORS());

// DB Connection
var conn = configInfo.mongoConn;

//var db = mongojs(conn, ['test']);
var db = mongojs(conn, ['db_mmba']);

// DB Collections
var agg = db.collection('aggregations');
var bin = db.collection('geo.bins');
var meta = db.collection('meta');
var log_api = db.collection('log.api');
var log_web = db.collection('log.web');

// API Routing
server.get('/api/:file', getAPI);
server.get('/api/carrier/:file', getAPI);
server.get('/api/mmba/carrier/:file', getAPI);
server.get('/api/vizmo/carrier/:file', getAPI);
server.get('/api/meta/:file', getMeta);

// API-Docs Routing
server.get(/\/api-docs\/*/,  
	function(req, res, next) {

        console.log('\n\n api-docs ' );
		console.log('req.url : ' + req.url );

		logWeb(req, res, next);

        return next();
    },
	restify.serveStatic({
		directory : './api-docs',
		default : 'default.json'
	})
);

// Web Routing
server.get(/\/?.*/,
	function(req, res, next) {

		logWeb(req, res, next);

        return next();
    },
	restify.serveStatic({
		directory : './web',
		default : 'index.html'
	})
);

// Log Functions
function logWeb(req, res, next){

	console.log('\n\n logWeb ' );

	var r_url = req.url;
	var r_params = req.params;
	var r_method = req.method;
	var r_headers = req.headers;
	//var r_httpVersion = req.httpVersion;
	//var r_version = req.version();

	var r_id = req.id();
	var r_contentType = req.contentType();
	var r_href = req.href();
	var r_path = req.path();

	var r_remoteAddress = req.connection.remoteAddress;
	var r_encrypted = req.connection.encrypted;

	//var ip = req.ip;
	//var auth = req.auth;
	//var agent = req.agent;
	//var r_host = req.host;
	//var r_hostname = req.hostname;
	//var port = req.port;
	//var localAddress = req.localAddress;
	//var socketPath = req.socketPath;
	//var trailers = req.trailers;

	//var contentLength = req.contentLength();

	console.log('params : ' + JSON.stringify(r_params) );
	console.log('url : ' + r_url );
	console.log('method : ' + r_method );
	console.log('headers : ' + JSON.stringify(r_headers) );

	//var h_useragent = req.headers['user-agent'];
	//var h_referer = req.headers['referer'];
	//var h_host = req.headers['host'];

	var r_time = req.time();
	var d = new Date();
	var d_time = d.getTime();
	var j_date = d.toJSON();
	var timer =  d_time - r_time;

	//console.log('r_time : ' + r_time );
	//console.log('d_time : ' + d_time );
	console.log('j_date : ' + j_date );

	var r_url = req.url;
	var r_params = req.params;
	var r_method = req.method;
	var r_headers = req.headers;
	//var r_httpVersion = req.httpVersion;
	//var r_version = req.version();

	var r_id = req.id();
	var r_contentType = req.contentType();
	var r_href = req.href();
	var r_path = req.path();

	var r_remoteAddress = req.connection.remoteAddress;
	var r_encrypted = req.connection.encrypted;

	var log_doc = {
		'date' : j_date,
		'timer' : timer,
		'request' : {
			'id' : r_id,
			'time' : r_time,
			'url' : r_url,
			'params' : r_params,
			'method' : r_method,
			'contentType' : r_contentType,
			'href' : r_href,
			'path' : r_path,
			'connection' : {
				'remoteAddress' : r_remoteAddress,
				'encrypted' : r_encrypted
			},
			'headers' : r_headers
		}
	};

	log_web.insert(log_doc, function(err , doc){

		if (doc) {
			console.log('log_web success ');
			return next();
		}
		else {
			console.log('log_web err ');
			return next(err);
		}
	});
}

function logAPI(req, res, next){

	console.log('\n\n logAPI ' );

	var r_url = req.url;
	var r_params = req.params;
	var r_method = req.method;
	var r_headers = req.headers;

	var r_id = req.id();
	var r_contentType = req.contentType();
	var r_href = req.href();
	var r_path = req.path();

	var r_remoteAddress = req.connection.remoteAddress;
	var r_encrypted = req.connection.encrypted;

	var r_time = req.time();
	var d = new Date();
	var d_time = d.getTime();
	var j_date = d.toJSON();
	var timer =  d_time - r_time;

	var r_url = req.url;
	var r_params = req.params;
	var r_method = req.method;
	var r_headers = req.headers;

	var r_id = req.id();
	var r_contentType = req.contentType();
	var r_href = req.href();
	var r_path = req.path();

	var r_remoteAddress = req.connection.remoteAddress;
	var r_encrypted = req.connection.encrypted;

	var log_doc = {
		'date' : j_date,
		'timer' : timer,
		'request' : {
			'id' : r_id,
			'time' : r_time,
			'url' : r_url,
			'params' : r_params,
			'method' : r_method,
			'contentType' : r_contentType,
			'href' : r_href,
			'path' : r_path,
			'connection' : {
				'remoteAddress' : r_remoteAddress,
				'encrypted' : r_encrypted
			},
			'headers' : r_headers
		}
	};

	log_api.insert(log_doc, function(err , doc){

		if (doc) {
			console.log('logAPI success ');
			return next();
		}
		else {
			console.log('logAPI err ');
			return next(err);
		}
	});

}

// API Function
function getAPI(req, res, next){

	console.log('\n\n getAPI ' );

	if (!validFileExt(req.params.file)) {
		return next(new restify.InvalidArgumentError('Invalid file extension. Only json, jsonp, geojson, and xml are supported.'));
	}
	else if (!validFileName(req.params.file)) {
		return next(new restify.InvalidArgumentError('Invalid file name/extension.'));
	}
	else if (!validFileJSONP(req.params.file, req.query.callback, req.query.jsonp)) {
		return next(new restify.InvalidArgumentError('Invalid jsonp request. A callback or jsonp parameter is required.'));
	}
	else {

		// get file ext/name
		var fileExt = getFileExt(req.params.file);
		var fileName = getFileName(req.params.file);

		if (fileName == 'meta') {
			getMeta(req, res, next);
		}
		else {

			console.log('fileExt : ' + fileExt );
			console.log('fileName : ' + fileName );

			var q_find, q_limit, q_sort;
			q_limit = 1;
			q_sort = {'id.geo_zoom' : -1};

			var carrier_find, time_find, ll_find;

			// get carrier name/id
			var carrierName;
			var carrierID = fileName;
			
			// if no carrier specified, then return all
			if ((carrierID != 'combined') && (carrierID != 'att') && (carrierID != 'sprint') && (carrierID != 'tmobile') && (carrierID != 'verizon') && (carrierID != 'other')) {
				carrierID = 'all';
			}

			// support all carrier return - all 6 carriers
			if (carrierID == 'all') {
				//carrier_find = {$or : [{'id.carrier' : 'combined'}, {'id.carrier' : 'att'}, {'id.carrier' : 'sprint'}, {'id.carrier' : 'tmobile'}, {'id.carrier' : 'verizon'}, {'id.carrier' : 'other'}]};
				q_limit = 6;
			}
			else {
				//carrier_find = {'id.carrier' : carrierID};
				carrier_find = true;
			}

			var lat = req.query.lat;
			var lon = req.query.lon;
			var geotype = req.query.geo;

			if (validLatLon(lat, lon)) {

				console.log('lon ' + lon);
				console.log('lat ' + lat);

				lat = Number(lat);
				lon = Number(lon);

				//ll_find = {geometry : { $geoIntersects : { $geometry : { type : 'Point', coordinates : [lon, lat] }}}};
				ll_find = true;
			}

			// create query
			if (ll_find) {
				//q_find = {'id.time' : 'total', geometry : { $geoIntersects : { $geometry : { type : 'Point', coordinates : [lon, lat] }}}};

				var b_find, b_sort, b_limit;

				if (validGeoType(geotype)) {
					b_find = {'geo_type' : geotype, 'geometry' : { $geoIntersects : { $geometry : { type : 'Point', coordinates : [lon, lat]}}}};
				}
				else {
					b_find = {'geometry' : { $geoIntersects : { $geometry : { type : 'Point', coordinates : [lon, lat]}}}};
				}

				b_sort = {'geo_zoom' : -1};
				b_limit = 1;

				bin.find(b_find).sort(b_sort).limit(b_limit, function(err , doc){

					console.log('bin sent');

					if (doc) {
						console.log('search bin success');
						console.log('doc.length : ' + doc.length);

						if (doc.length == 1) {

							var geo_id = doc[0].geo_id;
							console.log('geo_id : ' + geo_id);

							if (carrier_find) {
								q_find = {'id.geo_id' : geo_id, 'id.time' : 'total', 'id.carrier' : carrierID};
							}
							else {
								q_find = {'id.geo_id' : geo_id, 'id.time' : 'total'};
							}

							queryAPI(q_find, q_limit, q_sort, req, res, next);
							//return next();
						}
						else {
							console.log('no bin results ');
							return next(new restify.ResourceNotFoundError('No geographic results returned.'));
						}
					}
					else {
						console.log('search bin err ');
						return next(err);
					}
				});
			}
			else {
				if (carrier_find) {
					q_find = {'id.geo_id' : 'national', 'id.time' : 'total', 'id.carrier' : carrierID};
				}
				else {
					q_find = {'id.geo_id' : 'national', 'id.time' : 'total'};
				}

				queryAPI(q_find, q_limit, q_sort, req, res, next);
			}
		}
	}

	// Query Function
	function queryAPI(find, limit, sort, req, res, next) {

		console.log('queryAPI ');

		console.log( 'find('+ JSON.stringify( find ) +')' );
		console.log( 'sort('+ JSON.stringify( sort ) +')' );
		console.log( 'limit('+ JSON.stringify( limit ) +')' );

		agg.find(find).sort(sort).limit(limit, function(err , doc){

			console.log('query sent');

			if (doc) {
				console.log('search doc success');
				//console.log('doc.length : ' + doc.length);

				if (doc.length > 0) {

					var out;

					var out_geometry = doc[0].geometry;

					var out_id = doc[0].id;
					var out_value = doc[0].value;
					var out_bbox = doc[0].bbox;
					var out_properties = [];
					var out_geo_type = doc[0].id.geo_type;

					if (carrierID == 'all') {

						console.log('carrierID all : ' );

						for (var i = 0; i < doc.length; i++) {

							if (doc[i].id.geo_type == out_geo_type) {
								out_properties.push(
									{
										'id' : doc[i].id,
										'value' : doc[i].value
									}
								);
							}
						}
					}
					else {
						out_properties.push(
							{
								'id' : out_id,
								'value' : out_value
							}
						);
					}

					// always output geojson - single feature
					out = {
						'type' : 'Feature',
						'bbox' : out_bbox,
						'geometry' : out_geometry,
						'properties' : out_properties
					};

					// convert to xml with js2xmlparser
					if (fileExt == '.xml') {
						out = js2xmlparser('vizmo', out);
						res.setHeader('Content-Type', 'text/xml');
					}

					// add headers and send
					res.header('Access-Control-Allow-Origin', '*');
					res.header('Access-Control-Allow-Headers', 'X-Requested-With');
					//res.send(out);
					res.send(200 , out);

					// log api
					logAPI(req, res, next);

					//return next();
				}
				else {
					console.log('no results ');
					return next(new restify.ResourceNotFoundError('No results returned.'));
				}
			}
			else {
				console.log('search err ');
				return next(err);
			}
		});
	}
}

function getMeta(req, res, next){

	console.log('\n\n getMeta ' );

	var fileExt = getFileExt(req.params.file);
	var fileName = getFileName(req.params.file);
	
	console.log('fileName : ' + fileName);	 
			
	var m_find, m_proj;
	
	
	if ((fileName == 'bins') || (fileName == 'bin') || (fileName == 'hex')){
		m_find = {'type' : 'bins'};
		m_proj = {'type': true, 'hex5k':true, 'hex10k': true, 'hex25k': true};
	}
	else if ((fileName == 'agg') || (fileName == 'aggregation') || (fileName == 'aggregations')){
		m_find = {'type' : 'aggregations'};
		m_proj = {'type': true, 'total': true, 'geo.hex5k.total.total': true, 'geo.hex10k.total.total': true, 'geo.hex25k.total.total': true};
	}
	else if ((fileName == 'dates') || (fileName == 'date')){
		m_find = {'type' : 'dates'};
		m_proj = {'type': true, 'latest_aggregated_date':true, 'latest_binned_date': true, 'latest_imported_date': true};
	}
	else {
		m_find = {$or: [{'type' : 'bins'}, {'type' : 'aggregations'}, {'type' : 'dates'}]};
		m_proj = {'type': true, 'hex5k': true, 'hex10k': true, 'hex25k': true, 'total': true, 'geo.hex5k.total.total': true, 'geo.hex10k.total.total': true, 'geo.hex25k.total.total': true, 'latest_aggregated_date':true, 'latest_binned_date': true, 'latest_imported_date': true};
	}
	
	console.log( 'm_find : '+ JSON.stringify( m_find  ) +'' );
	console.log( 'm_proj : '+ JSON.stringify( m_proj  ) +'' );
	
	meta.find(m_find, m_proj, function(err , doc){
	
		console.log('getMeta query sent');

		if (doc) {
			console.log('getMeta doc success');
			
			console.log( 'doc : '+ JSON.stringify( doc  ) +' ' );
			
			if (doc.length > 0) {

				var out = {};

				//var dates_arr = doc[0].dates;

				//dates_arr.sort();
				//dates_arr.reverse();

				//var last_date = dates_arr[0];
				
				for (var i = 0; i < doc.length; i++) {

					if (doc[i].type == 'bins') {
						out.bins = {
							'total' : doc[i].hex5k + doc[i].hex10k + doc[i].hex25k,
							'geo': {
								'hex5k' : doc[i].hex5k,
								'hex10k' : doc[i].hex10k,
								'hex25k' : doc[i].hex25k
							}
						};
					}
					if (doc[i].type == 'aggregations') {
						//out.aggregations.total = doc[i].total.total;
						out.aggregations = {
							'total' : doc[i].total.total,
							'geo': {
								'hex5k' : doc[i].geo.hex5k.total.total,
								'hex10k' : doc[i].geo.hex10k.total.total,
								'hex25k' : doc[i].geo.hex25k.total.total
							},
							'carrier' : {
								'combined' : doc[i].total.combined,
								'att' : doc[i].total.att,
								'sprint' : doc[i].total.sprint,
								'tmobile' : doc[i].total.tmobile,
								'verizon' : doc[i].total.verizon,
								'other' : doc[i].total.other
							}
						};						
					}
					if (doc[i].type == 'dates') {
						out.dates = {								
							'latest_aggregated' : doc[i].latest_aggregated_date,
							'latest_binned' : doc[i].latest_binned_date,
							'latest_imported' : doc[i].latest_imported_date
						};	
					}
				}	
				
				/*
				out = {
					'meta_type' : 'last_updated',
					'meta_value' : '06041979'
				};
				*/

				// convert to xml with js2xmlparser
				if (fileExt == '.xml') {
					out = js2xmlparser('vizmo', out);
					res.setHeader('Content-Type', 'text/xml');
				}

				// add headers and send
				res.header('Access-Control-Allow-Origin', '*');
				res.header('Access-Control-Allow-Headers', 'X-Requested-With');
				//res.send(out);
				res.send(200 , out);

				// log api
				logAPI(req, res, next);

				return next();
			}
			else {
				console.log('no results ');
				return next(new restify.ResourceNotFoundError('No results returned.'));
			}
		}
		else {
			console.log('search err ');
			return next(err);
		}
	});
}

// Listen
server.listen(port, ip_addr, function(){
    console.log('%s listening at %s ', server.name , server.url);
});

// Functions
function getFileExt(p) {

	var rx = /(\.jsonp$|\.json$|\.geojson$|\.xml$)/i;
	var m = p.match(rx);

	if (m == null) {
		return '';
	}
	else {
		return m[0];
	}
}
function validFileExt(p) {

	var rx = /(\.jsonp$|\.json$|\.geojson$|\.xml$)/i;
	var m = p.match(rx);

	if (m == null) {
		return false;
	}
	else {
		return true;
	}
}

function validFileJSONP(p, c, j) {

	var f = getFileExt(p);
	var j_val = true;
	var c_val = true;

	if (f == '.jsonp') {

		if ((typeof j === 'undefined') || (j == '')) {
			j_val = false;
		}
		if ((typeof c === 'undefined') || (c == '')) {
			c_val = false;
		}

		if ((!j_val) && (!c_val)) {
			return false;
		}
		else {
			return true;
		}
	}
	else {
		return true;
	}
}

function getFileName(p) {

	var s = p.split('.');

	if (s.length >= 0) {
		return s[0];
	}
	else{
		return null;
	}
}

function validFileName(p) {

	var s = p.split('.');

	if (s.length >= 0) {
		return true;
	}
	else{
		return false;
	}
}

function validLatLon(lat, lon) {

	if ( (!isNaN(lat)) && (!isNaN(lon)) ) {

		if ( (lat >= -90) && (lat <= 90) && (lon >= -180) && (lat <= 180) ) {
			return true;
		}
		else {
			return false;
		}
	}
	else {
		return false;
	}
}


function validGeoType(geotype) {

	if ((geotype == 'hex5k') || (geotype == 'hex10k') || (geotype == 'hex25k')) {
		return true;
	}
	else {
		return false;
	}
}
