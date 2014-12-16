/*
   ___  ___   ___         _                  
  / __\/ __\ / __\ /\   /(_)____ /\/\   ___  
 / _\ / /   / /    \ \ / / |_  //    \ / _ \ 
/ /  / /___/ /___   \ V /| |/ // /\/\ \ (_) |
\/   \____/\____/    \_/ |_/___\/    \/\___/ 

*/   
var map;
var activeLayerGroup;

// geocoder
var geocoder;
var geocoder_places;
var geocoder_zip;

// hex bin layer
var hexLayer;

var tabler;

var hexOptions = {
	color: '#f0ff00',      	// Stroke color
	opacity: 0.9,         	// Stroke opacity
	weight: 7,         		// Stroke weight
	fillColor: '#f0ff00',  	// Fill color
	fillOpacity: 0.0    	// Fill opacity
};

// setup map
$(function() {
	
	setMeta();
	
	L.mapbox.accessToken = 'pk.eyJ1IjoiZmNjIiwiYSI6IlIzd09zN3MifQ.zCeIv0zfGXR4jNdPl3-z7w';	
	
	geocoder_places = L.mapbox.geocoder('mapbox.places');
	//geocoder_zip = L.mapbox.geocoder('mapbox.places-postcode-us-v1');
	
	map = L.mapbox.map('map', 'fcc.map-kzt95hy6', {infoControl: false, attributionControl: true, maxZoom:12})
		.setView([38.82, -94.96], 4);
	//map.addControl(L.mapbox.infoControl().addInfo('Map data provided by crowdsourced results - <a href="">Learn More</a>'));

	map.scrollWheelZoom.disable();	
		
	//L.control.fullscreen().addTo(map);	

	activeLayerGroup = new L.LayerGroup();
	var default_TL = L.mapbox.tileLayer('fcc.combined-speed-total');

	activeLayerGroup.addLayer(default_TL);
	activeLayerGroup.addTo(map);	
	
	// hash location
	var hashURL = window.location.hash;
	if (hashURL.indexOf('#') === 0) {
		hashURL = hashURL.substr(1);
	}
	var hashArgs = hashURL.split('/');

	if (hashArgs.length == 3) {
		var hash_zoom = parseInt(hashArgs[0], 10);
		var hash_lat = parseFloat(hashArgs[1]);
		var hash_lon = parseFloat(hashArgs[2]);
					
		if ((isNaN(hash_zoom)) || (isNaN(hash_lat)) || (isNaN(hash_lon))) {	
			//alert('hash error');
			loadData();			
		}
		else {
			if (hash_zoom <= 5) {			
				loadData();
			}
			else {
				loadData(hash_lat, hash_lon, 'init');
			}
		}
	} 
	else {
		//alert('blank hash');
		loadData();			
	}
	
	// onclick map event
	map.on('click', function(e) {		
		//console.log('click');
		
		var click_lat = e.latlng.lat;
		var click_lon = e.latlng.lng;
		
		var click_zoom = map.getZoom();		
		var click_geo = getGeoType(click_zoom);

		loadData(click_lat, click_lon, click_geo);
	});
	
	// ondoubleclick map event
	map.on('dblclick', function(e) {
		//console.log('dblclick');
		
		//var dblclick_lat = e.latlng.lat;
		//var dblclick_lon = e.latlng.lng;
		
		//loadData(dblclick_lat, dblclick_lon, 'dblclick');
	});
	
	// onzoom map event
	map.on('zoomend', function(e) {
		//alert(e.latlng);		
		
		var cur_zoom = map.getZoom();	
		
		//if zoom out switch to nationwide
		if (cur_zoom <= 5) {			
			loadData();
		}
		else {
		
			if (hexLayer) {
				var hex_center = hexLayer.getBounds().getCenter();
				var hex_lat = hex_center.lat;
				var hex_lon = hex_center.lng;
				
				var hex_geo = getGeoType(cur_zoom);

				loadData(hex_lat, hex_lon, hex_geo);
			}
		}
	});
	
	// add map hash function - after initial hash
	var hash = L.hash(map);		
	
});

$(document).on('click', function(){
    if ($('#alert-box').is(':visible')) {
		$('#alert-box').remove();
		$('#input-location').removeAttr('aria-describedby');
	}    
});

$('#input-location').on('focus', function(){
	if ($(this).val() == 'Nationwide') {
		$(this).val('');
	}
});

function getGeoType(zoom) {
	var geotype;
	if (zoom >= 11) {
		geotype = 'hex5k';
	}
	else if ((zoom >= 9) && (zoom <= 10)) {
		geotype = 'hex10k';
	}
	else if ((zoom >= 6) && (zoom <= 8)) {
		geotype = 'hex25k';
	}
	else {
		geotype = 'nation';
	}
	return geotype;
}

// switch map ids
$('.list-carrier, .list-mapType').on('click','a', function(){
	
	var $this = $(this);
	var id = $this.attr('id');
	var id_arr = id.split('-');
	var id_type = id_arr[0];
	var id_val = id_arr[1];	
	
	$this.closest('ul').find('.glyphicon-ok, .sr-only').remove();		
	$this.prepend('<span class="glyphicon glyphicon-ok"></span>').append('<span class="sr-only"> ' + (id_type === 'mapType' ? 'map type' : id_type) + ' filter is selected</span>');
	
	$('#input-' + id_type).val(id_val);
	
	changeMapLayer();
	updateData();	
	
	// reload data for current hex/nation
	//alert('id_type : ' + id_type );
	if (id_type == 'time') {		
		if (hexLayer) {
			var hex_center = hexLayer.getBounds().getCenter();
			var hex_lat = hex_center.lat;
			var hex_lon = hex_center.lng;
			var map_zoom = map.getZoom();			
			var hex_geo = getGeoType(map_zoom);

			loadData(hex_lat, hex_lon, hex_geo);
		}
		else {
			loadData();
		}
	}
	
	//$('.map-filters').collapse('hide');
});

// click carrier table
$('.row-carrier-name').on('click', function(){
   
    var id = $(this).attr('id');
	//alert('id : ' + id );
	var id_arr = id.split('-');
	var id_type = id_arr[0];
	var id_val = id_arr[1];	
	
	//alert('id_type : ' + id_type );
	//alert('id_val : ' + id_val );
	
	$('#input-carrier').val(id_val);
	
	changeMapLayer();
	updateData();
	
	// dropdown menubar
	$('#carrier-'+ id_val).closest('ul').find('.glyphicon-ok').remove();
	$('#carrier-'+ id_val).prepend('<span class="glyphicon glyphicon-ok"></span>');
});

function changeMapLayer() {

	var input_carrier = $('#input-carrier').val();
	var input_mapType = $('#input-mapType').val();
	var input_time = $('#input-time').val();
		
    activeLayerGroup.clearLayers();
    activeLayerGroup.addLayer(L.mapbox.tileLayer('fcc.'+ input_carrier +'-'+ input_mapType +'-'+ input_time));	
	
	$( '#h-carrier' ).text( carrierName(input_carrier) );	
	
	if (input_mapType == 'speed') {
		//$( '#h-mapType' ).text( 'Speed' );
	}
	else if (input_mapType == 'participation') {
		//$( '#h-mapType' ).text( 'Participation' );
	}
	
	// change legend colors
	changeLegend(input_carrier, input_mapType);
}

// change legend
function changeLegend(carrier, mapType) {

	if (mapType == 'participation') {
		$( '#map-legend-name' ).text( 'Participation Map' );	
		$( '#map-legend-desc' ).text( 'Number of Tests' );	
		
		$( '#map-legend-text-4' ).text( 'Over 300 Tests' );	
		$( '#map-legend-text-3' ).text( '150 - 300 Tests' );	
		$( '#map-legend-text-2' ).text( '50 - 150 Tests' );	
		$( '#map-legend-text-1' ).text( '10 - 50 Tests' );	
		$( '#map-legend-text-0' ).text( 'Not Enough Tests' );	
	}
	else if (mapType == 'speed') {
		$( '#map-legend-name' ).text( 'Speed Test Map' );
		$( '#map-legend-desc' ).text( 'Median Download Speed' );	
		
		$( '#map-legend-text-4' ).text( 'Above 10 Mbps' );	
		$( '#map-legend-text-3' ).text( '5 - 10 Mbps' );	
		$( '#map-legend-text-2' ).text( '1 - 5 Mbps' );	
		$( '#map-legend-text-1' ).text( 'Below 1 Mbps' );	
		$( '#map-legend-text-0' ).text( 'Not Enough Tests' );
	}
	
	if (carrier == 'combined') {
		$( '#map-legend-hex-4' ).css( 'color', '#002b11' );
		$( '#map-legend-hex-3' ).css( 'color', '#00441b' );
		$( '#map-legend-hex-2' ).css( 'color', '#3da659' );
		$( '#map-legend-hex-1' ).css( 'color', '#b1dfab' );
		$( '#map-legend-hex-0' ).css( 'color', '#00441b' );			
	}
	else if (carrier == 'att') {
		$( '#map-legend-hex-4' ).css( 'color', '#08306b' );
		$( '#map-legend-hex-3' ).css( 'color', '#3d8dc3' );
		$( '#map-legend-hex-2' ).css( 'color', '#afd1e7' );
		$( '#map-legend-hex-1' ).css( 'color', '#BBBDBF' );
		$( '#map-legend-hex-0' ).css( 'color', '#08306b' );		
	}
	else if (carrier == 'sprint') {
		$( '#map-legend-hex-4' ).css( 'color', '#141313' );
		$( '#map-legend-hex-3' ).css( 'color', '#505150' );
		$( '#map-legend-hex-2' ).css( 'color', '#777877' );
		$( '#map-legend-hex-1' ).css( 'color', '#CECFCD' );
		$( '#map-legend-hex-0' ).css( 'color', '#141313' );	
	}
	else if (carrier == 'tmobile') {
		$( '#map-legend-hex-4' ).css( 'color', '#b5048f' );
		$( '#map-legend-hex-3' ).css( 'color', '#ff4fd6' );
		$( '#map-legend-hex-2' ).css( 'color', '#ff99e3' );
		$( '#map-legend-hex-1' ).css( 'color', '#ffe3f0' );
		$( '#map-legend-hex-0' ).css( 'color', '#b5048f' );	
	}
	else if (carrier == 'verizon') {
		$( '#map-legend-hex-4' ).css( 'color', '#ac0b16' );
		$( '#map-legend-hex-3' ).css( 'color', '#d70002' );
		$( '#map-legend-hex-2' ).css( 'color', '#f78892' );
		$( '#map-legend-hex-1' ).css( 'color', '#f3ccdc' );
		$( '#map-legend-hex-0' ).css( 'color', '#ac0b16' );	
	}
	else if (carrier == 'other') {
		$( '#map-legend-hex-4' ).css( 'color', '#df5900' );
		$( '#map-legend-hex-3' ).css( 'color', '#f79030' );
		$( '#map-legend-hex-2' ).css( 'color', '#e9af78' );
		$( '#map-legend-hex-1' ).css( 'color', '#dfcfc0' );
		$( '#map-legend-hex-0' ).css( 'color', '#df5900' );	
	}
}

// set last updated date
function setMeta() {
	
	var loadURL = '/api/meta.json';	
	
	$.getJSON(loadURL, function( data ) {	
		
		var last_updated = data.dates.latest_aggregated;
		var last_updated_year = last_updated.substring(0, 4);
		var last_updated_month = parseInt(last_updated.substring(4, 6)) - 1;
		var last_updated_day = last_updated.substring(6, 8);
		
		var last_updated_date = new Date(last_updated_year, last_updated_month, last_updated_day)

		var total_bins = data.bins.total;
		var total_tests = data.aggregations.total;
			
		$( '#dateUpdated' ).text( 'Updated ' + last_updated_date.toLocaleDateString() );
		
		$( '#stats-total-bins' ).text( total_bins.toLocaleString() );
		$( '#stats-total-tests' ).text( total_tests.toLocaleString() );
		$( '#stats-last-updated' ).text( last_updated_date.toLocaleDateString() );		
	});	
}

// carrier color
function carrierColor(carrier) {
	var color_carrier = '#09A058';
	if (carrier == 'combined') {
		color_carrier = '#09A058';
	}
	else if (carrier == 'att') {
		color_carrier = '#4f97ff';
	}
	else if (carrier == 'sprint') {
		color_carrier = '#a8a8a8';
	}
	else if (carrier == 'tmobile') {
		color_carrier = '#C95FB1';
	}
	else if (carrier == 'verizon') {
		color_carrier = '#B83842';
	}
	else if (carrier == 'other') {
		color_carrier = '#d7702e';
	}
	return color_carrier;
	//return '#999';
}

function carrierName(carrier) {
	var name_carrier = '';
	if (carrier == 'combined') {
		name_carrier = 'Combined';
	}
	else if (carrier == 'att') {
		name_carrier = 'AT&T';
	}
	else if (carrier == 'sprint') {
		name_carrier = 'Sprint';
	}
	else if (carrier == 'tmobile') {
		name_carrier = 'T-Mobile';
	}
	else if (carrier == 'verizon') {
		name_carrier = 'Verizon';
	}
	else if (carrier == 'other') {
		name_carrier = 'Other';
	}
	return name_carrier;
}

function getPercentileText(perc) {	
	var perc_text;
	if (perc == '0') {
		perc_text = 'Minimum';
	}
	else if (perc == '25') {
		perc_text = 'Lower';
	}
	else if (perc == '50') {
		perc_text = 'Median';
	}
	else if (perc == '75') {
		perc_text = 'Upper';
	}
	else if (perc == '100') {
		perc_text = 'Maximum';
	}	
	return perc_text;
}

function updateData(){
	
	var prop = alljson.properties;
	
	var input_carrier = $('#input-carrier').val();
	var input_mapType = $('#input-mapType').val();
	var input_time = $('#input-time').val();
	
	//var input_percentile = $('#input-percentile').val();
	var percentile_arr = ['0', '25', '50', '75', '100'];	
	
	var color_carrier;
	var val_carrier;
	var val_download, val_upload, val_latency, val_packet, val_participation;
	var val_download_75, val_upload_75, val_latency_75, val_packet_75;
	var val_download_25, val_upload_25, val_latency_25, val_packet_25;
	var val_download_perc;
	
	//console.log('prop.length : ' + prop.length);
			
	for (var i = 0; i < prop.length; i++) { 	
	
		val_carrier = prop[i].id.carrier;
		color_carrier = carrierColor(val_carrier);
		
		//console.log('val_carrier : ' + val_carrier);
		
		val_participation = prop[i].value[input_time].download.participation;		
		
		val_download_25 = prop[i].value[input_time].download.percentile['percentile_25'];
		val_download_75 = prop[i].value[input_time].download.percentile['percentile_75'];
		
		val_upload_25 = prop[i].value[input_time].upload.percentile['percentile_25'];
		val_upload_75 = prop[i].value[input_time].upload.percentile['percentile_75'];
		
		val_latency_25 = prop[i].value[input_time].latency.percentile['percentile_25'];
		val_latency_75 = prop[i].value[input_time].latency.percentile['percentile_75'];
		
		val_packet_25 = prop[i].value[input_time].packet_loss.percentile['percentile_25'];
		val_packet_75 = prop[i].value[input_time].packet_loss.percentile['percentile_75'];
		
		val_download_perc = prop[i].value[input_time].download.percentile;		
		
		// download percentile array
		var boxplot_arr, boxplot_0, percentile_25, percentile_50, percentile_75, percentile_100;
		
		if (val_download_perc.percentile_0 != null) {
			boxplot_0 = val_download_perc.percentile_0.toFixed(2);
			boxplot_25 = val_download_perc.percentile_25.toFixed(2);
			boxplot_50 = val_download_perc.percentile_50.toFixed(2);
			boxplot_75 = val_download_perc.percentile_75.toFixed(2);
			boxplot_100 = val_download_perc.percentile_100.toFixed(2);

			boxplot_arr = [boxplot_0, boxplot_25, boxplot_50, boxplot_75, boxplot_100];	
		}
		
		//for (var j = 0; j < percentile_arr.length; j++) { 	
			
			//var cur_percentile = percentile_arr[j];
			var cur_percentile = $('#sel-percentile').val();
			
			//console.log('cur_percentile : ' + cur_percentile);
			
			var ud_percentile = cur_percentile;
			var lp_percentile = Math.abs(parseInt(cur_percentile) - 100);				
			//console.log('ud_percentile : ' + ud_percentile);
			//console.log('lp_percentile : ' + lp_percentile);
			
			val_download = prop[i].value[input_time].download.percentile['percentile_'+ud_percentile];
			val_upload = prop[i].value[input_time].upload.percentile['percentile_'+ud_percentile];
			val_latency = prop[i].value[input_time].latency.percentile['percentile_'+lp_percentile];
			val_packet = prop[i].value[input_time].packet_loss.percentile['percentile_'+lp_percentile];			
			//console.log('val_download : ' + val_download);		
			
			if ((val_download == null) || (val_upload == null) || (val_latency == null) || (val_packet == null)) {
				
			}
			else {				
				
				$('#table-carriers').find('.'+ val_carrier +'-download').text( val_download.toFixed(2) );
				$('#table-carriers').find('.'+ val_carrier +'-upload').text( val_upload.toFixed(2) );
				$('#table-carriers').find('.'+ val_carrier +'-latency').text( Math.round(val_latency / 1000) );
				$('#table-carriers').find('.'+ val_carrier +'-packet').text( val_packet.toFixed(1) );

				$('#table-carriers').find('.'+ val_carrier +'-download').parent().attr('data-order', val_download.toFixed(2) );
				$('#table-carriers').find('.'+ val_carrier +'-upload').parent().attr('data-order', val_upload.toFixed(2) );
				$('#table-carriers').find('.'+ val_carrier +'-latency').parent().attr('data-order', Math.round(val_latency / 1000) );
				$('#table-carriers').find('.'+ val_carrier +'-packet').parent().attr('data-order', val_packet.toFixed(1) );				
							
				$('#table-carriers').find('.'+ val_carrier +'-sparkline').sparkline(boxplot_arr, {
					width: '80px', height: '24px',
					barWidth: 11, barSpacing: 4, barColor: color_carrier, //barColor: '#777777', 
					chartRangeMin: 0, chartRangeMax: 50, tooltipSuffix: '&nbsp;Mbps',
					type: 'bar'});					
			}			
		//}		
		

		if (val_carrier == input_carrier) {
			
			if ((val_download_25 != null) && ((val_download_75 != null))) {
				$('#main-download-lower').text( val_download_25.toFixed(1) );
				$('#main-download-upper').text( val_download_75.toFixed(1) );	
				
				$('#main-sparkbox').sparkline(boxplot_arr, {
					width: '65%', height: '25px', lineColor: '#666666', color: '#666666',
					raw: true,
					boxLineColor: '#666666',
					boxFillColor: '#e5e5e5',
					whiskerColor: '#666666',
					medianColor: color_carrier,
					targetColor: '#666666',
					showOutliers: false,
					//outlierLineColor: 'red',
					//outlierFillColor: 'red',
					type: 'box'});
				
			}
			else {
				$('#main-sparkbox').html('&nbsp;');
	
				$('#main-download-lower').text( '' );
				$('#main-download-upper').text( '' );	
			}
			
			if ((val_upload_25 != null) && ((val_upload_75 != null))) {
				$('#main-upload-lower').text( val_upload_25.toFixed(1) );
				$('#main-upload-upper').text( val_upload_75.toFixed(1) );
			}
			else {
				$('#main-upload-lower').text( '' );
				$('#main-upload-upper').text( '' );
			}
			
			if ((val_latency_25 != null) && ((val_latency_75 != null))) {
				$('#main-latency-lower').text( Math.round(val_latency_75 / 1000) );
				$('#main-latency-upper').text( Math.round(val_latency_25 / 1000) );
			}
			else {
				$('#main-latency-lower').text( '' );
				$('#main-latency-upper').text( '' );
			}			
		}
	} 	

	tabler = $('.tablers').dataTable({
		paging: false,
		info: false,
		searching: false,
		destroy: true,
		order: [],
		aoColumns: [
            null,
            { "orderSequence": [ "desc", "asc" ] },
            { "orderSequence": [ "desc", "asc" ] },
            { "orderSequence": [ "asc", "desc" ] },
            { "orderSequence": [ "asc", "desc" ] }
        ],
		columnDefs: [ {
		  targets: 0,
		  orderable: false
		} ]
	});		
}

var alljson;
// load data
function loadData(lat, lon, type) {

	//$('body').css('cursor', 'wait');	
	//$('#map').css('cursor', 'wait');
	var loadURL = '/api/carrier.json';
	
	if ((isNaN(lat)) || (isNaN(lon))) {
		// national search
		type = 'nation';
	}
	else if ((lat == 0) && (lon == 0)) {
		// national search
		type = 'nation';
	}
	else if (type == 'nation') {
		// national search
	}
	else {
		loadURL += '?lat='+ lat +'&lon='+ lon +'';
		
		if ((type == 'hex5k') || (type == 'hex10k') || (type == 'hex25k')) {
			loadURL += '&geo='+  type;
		}	
	}

	$.getJSON(loadURL, function( data ) {

		alljson = data;
		//$('body').css('cursor', 'auto');
		//$('#map').css('cursor', 'grab');
		
		resetTableDataText();
		
		if (hexLayer) {
			hexLayer.clearLayers();
			hexLayer = false;
		}
		
		var prop = alljson.properties;	
		
		var val_geo_type = prop[0].id.geo_type;	
		var val_geo_id = prop[0].id.geo_id;
		var val_geo_zoom = prop[0].id.geo_zoom;	
		
		var cur_zoom = map.getZoom();		
		var zoom_bounds = false;
		
		if ((type == 'search') || (type == 'dblclick') || (type == 'nav')) {
			zoom_bounds = true;
		}
		else if ((type == 'init') || (type == 'select') || (type == 'nation')) {
			zoom_bounds = false;
		}
		
		if (val_geo_id == 'national') {
			$('#input-location').val('');
			$('#h-location').text('Nationwide');
		}
		else { //if (val_geo_id != 'national') {
			
			// reverse geocode after loading
			if (type != 'search') {
				geocoder_places.reverseQuery([lon, lat], reverseMap);	
			}
			
			// create hex highlight
			hexLayer = L.mapbox.featureLayer(alljson);
			hexLayer.addTo(map);
			hexLayer.setStyle(hexOptions);
			
			hexLayer.on('dblclick', function(e) {
				//alert('dblclick');
				
				var dblclick_lat = e.latlng.lat;
				var dblclick_lon = e.latlng.lng;
				
				loadData(dblclick_lat, dblclick_lon, 'dblclick');
			});
			
			if (zoom_bounds) {
				var hexCenter = hexLayer.getBounds().getCenter();
				map.setView(hexCenter, val_geo_zoom);
			}
			//map.setZoom(val_geo_zoom);
		}	
		
		//alert('prop.length : ' + prop.length);
		updateData();
		
	})
	.fail(function() {
			
		//map.setView([lat, lon]);	
		
		$('.map-filters').before(createAlert('Not enough tests in this location.'));
		$('#alert-box').focus();
		$('#input-location').attr('aria-describedby', 'alert-msg'); 		
		
		resetTableDataText();
		
		if (hexLayer) {
			hexLayer.clearLayers();
			hexLayer = false;
		}
	});		
		
	//$('body').css('cursor', 'auto');
	//$('#map').css('cursor', 'grab');
}

// reset data to --
function resetTableDataText() {
	$('#main-sparkbox').html('&nbsp;');
	
	$('#main-download-lower').text( '' );
	$('#main-download-upper').text( '' );
	
	$('#main-upload-lower').text( '' );
	$('#main-upload-upper').text( '' );
	
	$('#main-latency-lower').text( '' );
	$('#main-latency-upper').text( '' );	
	
	var carrier_types = ['main', 'combined', 'att', 'sprint', 'tmobile', 'verizon', 'other'];
	var data_types = ['download', 'upload', 'latency', 'packet'];
	var perc_types = ['0', '25', '50', '75', '100'];
	
	//for (var h = 0; h < perc_types.length; h++) { 
		for (var i = 0; i < carrier_types.length; i++) { 
		
			for (var j = 0; j < data_types.length; j++) { 
				
				$('#table-carriers').find('.'+ carrier_types[i] +'-'+ data_types[j] +'').text( '--' );	
				$('#table-carriers').find('.'+ carrier_types[i] +'-'+ data_types[j] +'').parent().attr('data-order', 0 );	
			}
			$('#table-carriers').find('.'+ carrier_types[i] +'-sparkline').html('&nbsp;&nbsp;--&nbsp;&nbsp;--');		
		}	
	//}
}

// create alert box
function createAlert(alertMsg) {
    var alertBox = '<div id="alert-box" role="alert" tabindex="-1"><div class="alert alert-warning alert-popover fade in">'
             + '<button type="button" class="close" data-dismiss="alert"><span>&times;</span><span class="sr-only">Close</span></button>'
             + '<p id="alert-msg">' + alertMsg + '</p>'
             + '</div></div>';
    
    return alertBox;
}

// search geocode
function searchMap(err, data) {
	if (data.latlng) {
		
		//console.log('searchMap data : ' + JSON.stringify(data));		
		
        if (data.lbounds) {
            //map.fitBounds(data.lbounds);
        } 
        else if (data.latlng) {        
            //map.setView([lat, lon], 12);			
        }
        
        var lat = data.latlng[0];
        var lon = data.latlng[1];
		
		//alert('lat : ' + lat);	
        
        loadData(lat, lon, 'search');	
        
        // get city/state from results
        var name = '';
		var features_arr = data.results.features[0];
        var context_arr = features_arr.context;
		
		//console.log('features_arr : ' + features_arr);
		//console.log('context_arr.length : ' + context_arr.length);
		
		if (features_arr.id.indexOf('place') >= 0) {
			name = features_arr.text;			
			
			if (context_arr) {
				for (i = 0; i < context_arr.length; i++) {
					if (context_arr[i].id.indexOf('region') >= 0) {
						if (context_arr[i].text == 'District of Columbia') {
							name += ', DC';
						}
						else {
							name += ', ' + context_arr[i].text;
						}
					}
				}
			}
		}
		else if (features_arr.id.indexOf('postcode') >= 0) {
			name = features_arr.text;
		}
		else if (features_arr.id.indexOf('region') >= 0) {
			name = features_arr.text;
		}
		else {		
			if (context_arr) {
				for (i = 0; i < context_arr.length; i++) {

					if (context_arr[i].id.indexOf('city') >= 0) {
						name = context_arr[i].text;
					}
					else if (context_arr[i].id.indexOf('postcode') >= 0) {
						if (name == '') {
							name = context_arr[i].text;
						}
					}
					else if (context_arr[i].id.indexOf('province') >= 0) {
						if (name != '') {
							if (context_arr[i].text == 'District of Columbia') {
								name += ', DC';
							}
							else {
								name += ', ' + context_arr[i].text;
							}
						}
						else {
							name = context_arr[i].text;
						}
					}
				}
			}			
		}
        
        if ((name.length > 0) && (name != '')) {
            $('#h-location').text( name );
        }
        else {
            $('#h-location').text( lat +', '+ lon );
        }
    } 
	else {
        $('.map-filters').before(createAlert('The location was not found, please try again.'));
		$('#alert-box').focus();
		$('#input-location').attr('aria-describedby', 'alert-msg');        
    }
}

$('#form-search').submit(function( event ) {
	var input_location = $('#input-location').val();

	event.preventDefault();
	
	if ((input_location.toLowerCase() == 'new york, ny') || (input_location.toLowerCase() == 'new york ny')) {
		input_location = 'new york city, ny';
	}
	
	if ((input_location != 'Nationwide') && (input_location != '')) {
		
		geocoder_places.query(input_location, searchMap);
		
		/*
		if ( (input_location.length = 5) && ($.isNumeric( input_location )) ) {
			geocoder_zip.query(input_location, searchMap);
		}
		else {
			geocoder_places.query(input_location, searchMap);
		}
		*/
	}
	else {
		loadData();
		map.setView([38.82, -94.96], 4);	
		return false;
	}
	
	$('#input-location').blur();
});

function reverseMap(err, data) {
	
	var lat = data.query[1];
	var lon = data.query[0];
	
	//map.setView([lat, lon], 12);	
	//console.log('reverseMap data : ' + JSON.stringify(data));
	
	var name = '';
	var features_arr = data.features;	
	//console.log('features_arr.length : ' + features_arr.length);
	
	for (var i = 0; i < features_arr.length; i++) {
		
		//if (features_arr[i].id == 'city.20001') {
		if (features_arr[i].id.indexOf('place') >= 0) {
		
			name = features_arr[i].text;
			
			var context_arr = features_arr[i].context;			
			
			for (var j = 0; j < context_arr.length; j++) {				
				
				if (context_arr[j].id.indexOf('region') >= 0) {					
					
					if (context_arr[j].text == 'District of Columbia') {
						name += ', DC';
					}
					else {
						name += ', ' + context_arr[j].text;
					}
				}
			}
        }
    }
	
	if ((name.length > 0) && (name != '')) {
		$('#input-location').val(name);
		$('#h-location').text( name );
	}
	else {
		$('#input-location').val(lat +', '+ lon);
		$('#h-location').text( lat +', '+ lon );
	}
}

$('#btn-geoLocation').click(function( event ) {

	if (navigator.geolocation) {
		navigator.geolocation.getCurrentPosition(function(position) {
			var geo_lat = position.coords.latitude;
			var geo_lon = position.coords.longitude;
			var geo_acc = position.coords.accuracy;

			loadData(geo_lat, geo_lon, 'nav');			
			
		}, function(error) {
            $('.map-filters').before(createAlert('Your current location be found.'));
            $('#alert-box').focus();    
            $('#input-location').attr('aria-describedby', 'alert-msg');

		},{timeout:4000});
	}
	else{
        $('.map-filters').before(createAlert('Your current location be found.'));
        $('#alert-box').focus();
        $('#input-location').attr('aria-describedby', 'alert-msg');
	}
	
	return false;
});

$('#btn-nationLocation').click(function( event ) {
	
	loadData();
	map.setView([38.82, -94.96], 4);	
	return false;
});

$('#input-percentile, #sel-percentile').change(function( event ) {
	//console.log('sel-percentile');
	updateData();	
	return false;
});

$('.sparkline').tooltip({
	'container':'body', 
	'placement': function(ele) {
		if ($('.container').width() <= 720) {
			return 'bottom';	
		} else {
			return 'left';	
		}
	}
});

$('[data-toggle="chosen"]').chosen({ disable_search: true });

$('[data-toggle="tooltip"]').tooltip({ trigger: 'hover' });

if ('ontouchstart' in document.documentElement) {
  $('[data-toggle="tooltip"]').on('shown.bs.tooltip', function(e) {
		$(this).tooltip('toggle').click();
	});
} 

$('.clear-search').on('click', function() {
	$(this).addClass('hide');
});

$('#input-location').on('input', function() { 
	if ($(this).val().length > 0) {
		$('.clear-search').removeClass('hide');
	} else {
		$('.clear-search').addClass('hide');
	}
});
	
$('.btn-legend').click(function(){ 
	$(this).hide();
	$('.legend').show('fast');
});

$('.btn-closeLegend').click(function() { 
	$('.legend').hide('fast');
	$('.btn-legend').show();
});

$('.map-filters')
	.on('show.bs.collapse', function(e) { 
		$('.link-togFilters').find('span').toggleClass('glyphicon-chevron-down glyphicon-chevron-up');			
	}).on('shown.bs.collapse', function(e) { 
		$('.map-filters').find('a:first').focus();	
	}).on('hide.bs.collapse', function() {
		$('.link-togFilters').find('span').toggleClass('glyphicon-chevron-down glyphicon-chevron-up');	
	});
	
$('[data-tab]').click(function(){ 
	var tab = $(this).data('tab');
	$('#tab-list a[href="#tab-'+tab+'"]').tab('show');
});