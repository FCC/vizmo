import sys
import psycopg2
import os
import requests
import json as js
import re
import datetime
import time
import tarfile
import config

#set up dates table
def setup_dates_table(conn, cur):

	query = """SELECT EXISTS (
			SELECT 1 FROM information_schema.tables
			WHERE  table_schema = '%s' AND table_name = '%s_dates')
			""" % (SCHEMA_NAME, TABLE_NAME_PREFIX)
	print(query)
	cur.execute(query)
	row = cur.fetchall()
	table_exists = row[0][0]
	
	if table_exists:
		return

	query = """CREATE TABLE %s.%s_dates (
	id serial primary key,
	last_imported_date character varying(8),
	all_imported_dates json
	)""" % (SCHEMA_NAME, TABLE_NAME_PREFIX)
	cur.execute(query)
	conn.commit()
	
	query = """INSERT INTO %s.%s_dates (last_imported_date, all_imported_dates)
				VALUES (null, '{"all_imported_dates": []}')
				""" % (SCHEMA_NAME, TABLE_NAME_PREFIX)
	cur.execute(query)
	conn.commit()
	



#create tables
def create_tables(conn, cur):

	#cdmacelllocation
	query = """CREATE TABLE IF NOT EXISTS %s.%s_cdmacelllocation (
		id serial primary key,
		ix smallint NOT NULL DEFAULT 0::smallint,
		submission_id character(32) NOT NULL DEFAULT ''::bpchar,
		metric character varying(32) DEFAULT NULL::character varying,
		dtime timestamp without time zone NOT NULL,
		localdtime timestamp without time zone NOT NULL,
		system_id integer,
		network_id integer,
		ecio integer,
		dbm integer,
		base_station_id integer,
		base_station_latitude integer,
		base_station_longitude integer,
		geom geometry(Point, 4326),
		cma varchar(3),
		block varchar(15)
		--CONSTRAINT vizmo_cdmacelllocation_pkey PRIMARY KEY (submission_id, localdtime, ix)
		)""" % (SCHEMA_NAME, TABLE_NAME_PREFIX)

	cur.execute(query)
	conn.commit()

	#cellneighbourtower
	query = """CREATE TABLE IF NOT EXISTS %s.%s_cellneighbourtower (
		id serial primary key,
		ix smallint NOT NULL DEFAULT 0::smallint,
		submission_id character(32) NOT NULL DEFAULT ''::bpchar,
		metric character varying(32) DEFAULT NULL::character varying,
		dtime timestamp without time zone NOT NULL,
		localdtime timestamp without time zone NOT NULL,
		location_area_code integer,
		cell_tower_id integer,
		network_type_code text DEFAULT NULL::character varying,
		network_type text DEFAULT NULL::text,
		umts_psc integer,
		rssi integer
		--CONSTRAINT vizmo_cellneighbourtower_pkey PRIMARY KEY (submission_id, localdtime, ix)
		)""" % (SCHEMA_NAME, TABLE_NAME_PREFIX)

	cur.execute(query)
	conn.commit()


	#closesttarget
	query = """CREATE TABLE IF NOT EXISTS %s.%s_closesttarget (
		id serial primary key,
		ix smallint NOT NULL DEFAULT 0::smallint,
		submission_id character(32) NOT NULL DEFAULT ''::bpchar,
		dtime timestamp without time zone NOT NULL,
		localdtime timestamp without time zone NOT NULL,
		target character varying(100) DEFAULT NULL::character varying,
		ipaddress character varying(46) DEFAULT NULL::character varying
		--CONSTRAINT vizmo_closesttarget_pkey PRIMARY KEY (submission_id, localdtime, ix)
		)""" % (SCHEMA_NAME, TABLE_NAME_PREFIX)

	cur.execute(query)
	conn.commit()


	#closesttarget
	query = """CREATE TABLE IF NOT EXISTS %s.%s_cpuactivity (
		id serial primary key,
		ix smallint NOT NULL DEFAULT 0::smallint,
		submission_id character(32) NOT NULL DEFAULT ''::bpchar,
		dtime timestamp without time zone NOT NULL,
		localdtime timestamp without time zone NOT NULL,
		success smallint DEFAULT 0::smallint,
		max_average integer DEFAULT 0,
		read_average integer DEFAULT 0
		--CONSTRAINT vizmo_cpuactivity_pkey PRIMARY KEY (submission_id, localdtime, ix)
		)""" % (SCHEMA_NAME, TABLE_NAME_PREFIX)

	cur.execute(query)
	conn.commit()


	#datacap
	query = """CREATE TABLE IF NOT EXISTS %s.%s_datacap (
		id serial primary key,
		ix smallint NOT NULL DEFAULT 0::smallint,
		submission_id character(32) NOT NULL DEFAULT ''::bpchar,
		dtime timestamp without time zone NOT NULL,
		localdtime timestamp without time zone NOT NULL,
		success smallint
		--CONSTRAINT vizmo_datacap_pkey PRIMARY KEY (submission_id, localdtime, ix)
		)""" % (SCHEMA_NAME, TABLE_NAME_PREFIX)

	cur.execute(query)
	conn.commit()


	#gsmcelllocation
	query = """CREATE TABLE IF NOT EXISTS %s.%s_gsmcelllocation (
		id serial primary key,
		ix smallint NOT NULL DEFAULT 0::smallint,
		submission_id character(32) NOT NULL DEFAULT ''::bpchar,
		metric character varying(32) DEFAULT NULL::character varying,
		dtime timestamp without time zone NOT NULL,
		localdtime timestamp without time zone NOT NULL,
		signal_strength smallint,
		umts_psc integer,
		location_area_code integer,
		cell_tower_id integer
		--CONSTRAINT vizmo_gsmcelllocation_pkey PRIMARY KEY (submission_id, localdtime, ix)
		)""" % (SCHEMA_NAME, TABLE_NAME_PREFIX)

	cur.execute(query)
	conn.commit()


	#httpget
	query =  """CREATE TABLE IF NOT EXISTS %s.%s_httpget (
		id serial primary key,
		ix smallint NOT NULL DEFAULT 0::smallint,
		submission_id character(32) NOT NULL DEFAULT ''::bpchar,
		dtime timestamp without time zone NOT NULL,
		localdtime timestamp without time zone NOT NULL,
		success smallint,
		target character varying(100) DEFAULT NULL::character varying,
		ipaddress character varying(46) DEFAULT NULL::character varying,
		transfer_time integer,
		transfer_bytes integer,
		bytes_sec integer,
		warmup_time integer,
		warmup_bytes integer,
		number_of_threads integer
		--CONSTRAINT vizmo_httpget_pkey PRIMARY KEY (submission_id, localdtime, ix)
		)""" % (SCHEMA_NAME, TABLE_NAME_PREFIX)

	cur.execute(query)
	conn.commit()


	#httppost
	query = """CREATE TABLE IF NOT EXISTS %s.%s_httppost (
		id serial primary key,
		ix smallint NOT NULL DEFAULT 0::smallint,
		submission_id character(32) NOT NULL DEFAULT ''::bpchar,
		dtime timestamp without time zone NOT NULL,
		localdtime timestamp without time zone NOT NULL,
		success smallint,
		target character varying(100) DEFAULT NULL::character varying,
		ipaddress character varying(46) DEFAULT NULL::character varying,
		transfer_time integer,
		transfer_bytes integer,
		bytes_sec integer,
		warmup_time integer,
		warmup_bytes integer,
		number_of_threads integer
		--CONSTRAINT vizmo_httppost_pkey PRIMARY KEY (submission_id, localdtime, ix)
		)""" % (SCHEMA_NAME, TABLE_NAME_PREFIX)

	cur.execute(query)
	conn.commit()


	#location
	query = """CREATE TABLE IF NOT EXISTS %s.%s_location (
		id serial primary key,
		ix smallint NOT NULL DEFAULT 0::smallint,
		submission_id character(32) NOT NULL DEFAULT ''::bpchar,
		metric character varying(32) DEFAULT NULL::character varying,
		dtime timestamp without time zone NOT NULL,
		localdtime timestamp without time zone NOT NULL,
		source text DEFAULT NULL::character varying,
		latitude double precision,
		longitude double precision,
		accuracy double precision,
		geom geometry(Point, 4326),
		cma varchar(3),
		block varchar(15)
		--CONSTRAINT vizmo_location_pkey PRIMARY KEY (submission_id, localdtime, ix)
		)""" % (SCHEMA_NAME, TABLE_NAME_PREFIX)

	cur.execute(query)
	conn.commit()


	#netactivity
	query = """CREATE TABLE IF NOT EXISTS %s.%s_netactivity (
		id serial primary key,
		ix smallint NOT NULL DEFAULT 0::smallint,
		submission_id character(32) NOT NULL DEFAULT ''::bpchar,
		dtime timestamp without time zone NOT NULL,
		localdtime timestamp without time zone NOT NULL,
		success smallint,
		maxbytesout integer,
		maxbytesin integer,
		bytesout integer,
		bytesin integer
		--CONSTRAINT vizmo_netactivity_pkey PRIMARY KEY (submission_id, localdtime, ix)
		)""" % (SCHEMA_NAME, TABLE_NAME_PREFIX)

	cur.execute(query)
	conn.commit()


	#netusage
	query = """CREATE TABLE IF NOT EXISTS %s.%s_netusage (
		id serial primary key,
		ix smallint NOT NULL DEFAULT 0::smallint,
		submission_id character(32) NOT NULL DEFAULT ''::bpchar,
		dtime timestamp without time zone NOT NULL,
		localdtime timestamp without time zone NOT NULL,
		duration bigint,
		total_rx_bytes bigint,
		total_tx_bytes bigint,
		mobile_rx_bytes bigint,
		mobile_tx_bytes bigint,
		app_rx_bytes bigint,
		app_tx_bytes bigint
		--CONSTRAINT vizmo_netusage_pkey PRIMARY KEY (submission_id, localdtime, ix)
		)""" % (SCHEMA_NAME, TABLE_NAME_PREFIX)

	cur.execute(query)
	conn.commit()


	#vizmo_networkdata
	query = """CREATE TABLE IF NOT EXISTS %s.%s_networkdata (
		id serial primary key,
		ix smallint NOT NULL DEFAULT 0::smallint,
		submission_id character(32) NOT NULL DEFAULT ''::bpchar,
		metric character varying(32) DEFAULT NULL::character varying,
		dtime timestamp without time zone NOT NULL,
		localdtime timestamp without time zone NOT NULL,
		connected smallint,
		active_network_type_code text DEFAULT NULL::character varying,
		active_network_type text DEFAULT NULL::text,
		sim_operator_code text DEFAULT NULL::character varying,
		sim_operator_name character varying(32) DEFAULT NULL::character varying,
		roaming smallint,
		phone_type_code text DEFAULT NULL::character varying,
		phone_type text DEFAULT NULL::text,
		network_type_code text DEFAULT NULL::character varying,
		network_type text DEFAULT NULL::text,
		network_operator_code text DEFAULT NULL::character varying,
		network_operator_name text DEFAULT NULL::text
		--CONSTRAINT vizmo_networkdata_pkey PRIMARY KEY (submission_id, localdtime, ix)
		)""" % (SCHEMA_NAME, TABLE_NAME_PREFIX)

	cur.execute(query)
	conn.commit()


	#vizmo_udplatency
	query = """CREATE TABLE IF NOT EXISTS %s.%s_udplatency (
		id serial primary key,
		ix smallint NOT NULL DEFAULT 0::smallint,
		submission_id character(32) NOT NULL DEFAULT ''::bpchar,
		dtime timestamp without time zone NOT NULL,
		localdtime timestamp without time zone NOT NULL,
		success smallint,
		target character varying(100) DEFAULT NULL::character varying,
		ipaddress character varying(46) DEFAULT NULL::character varying,
		rtt_avg integer,
		rtt_min integer,
		rtt_max integer,
		rtt_stddev integer,
		received_packets integer,
		lost_packets integer
		--CONSTRAINT vizmo_udplatency_pkey PRIMARY KEY (submission_id, localdtime, ix)
		)""" % (SCHEMA_NAME, TABLE_NAME_PREFIX)

	cur.execute(query)
	conn.commit()


	#vizmo_submission
	query = """CREATE TABLE IF NOT EXISTS %s.%s_submission (
		id serial primary key,
		submission_id character(32) NOT NULL DEFAULT ''::bpchar,
		enterprise_id character varying(32) NOT NULL DEFAULT ''::character varying,
		dtime timestamp without time zone NOT NULL,
		localdtime timestamp without time zone NOT NULL,
		devicedtime character varying(100) NOT NULL DEFAULT '0000-00-00 00:00:00'::character varying,
		schedule_config_version text DEFAULT NULL::character varying,
		sim_operator_code text DEFAULT NULL::character varying,
		submission_type text DEFAULT NULL::character varying,
		timezone double precision,
		received timestamp without time zone,
		source_ip text DEFAULT NULL::character varying,
		app_version_code text NOT NULL DEFAULT ''::character varying,
		app_version_name text NOT NULL DEFAULT ''::character varying,
		tests smallint,
		metrics smallint,
		conditions smallint,
		os_type text DEFAULT NULL::character varying,
		os_version text DEFAULT NULL::character varying,
		model text DEFAULT NULL::text,
		manufacturer text DEFAULT NULL::text,
		imei character varying(16) DEFAULT NULL::character varying,
		imsi character varying(15) DEFAULT NULL::character varying,
		iosapp_id character varying(36) DEFAULT NULL::character varying,
		mobile_location_id integer
		--CONSTRAINT vizmo_submission_pkey PRIMARY KEY (submission_id)
		)""" % (SCHEMA_NAME, TABLE_NAME_PREFIX)

	cur.execute(query)
	conn.commit()

	
def write_to_table(type, content):
	content = content.replace(OUTPUTRECORDDELIMITER, '')

	if type == 'cdma_cell_location':
		items = content.split('\t')
		(ix, submission_id, metric, dtime, localdtime, system_id, network_id, ecio ,\
		dbm ,base_station_id ,base_station_latitude ,base_station_longitude) = items

		lat = float(base_station_latitude) / 10000
		lon = float(base_station_longitude) / 10000
		geom = get_geom_string(lat,lon)
		
		cma = get_cma(lat, lon)
		block = get_block(lat, lon)

		if cma is not None:
			cma = "'%s'" % (cma,)
		else:
			cma = "NULL"
		if block is not None:
			block = "'%s'" % (block,)
		else:
			block = "NULL"

		(ix, submission_id, metric, dtime, localdtime, system_id, network_id, ecio ,\
		dbm ,base_station_id ,base_station_latitude ,base_station_longitude) = \
		map(process_null, (ix, submission_id, metric, dtime, localdtime, system_id, network_id, ecio ,\
			dbm ,base_station_id ,base_station_latitude ,base_station_longitude))

		query = """INSERT INTO %s.%s_cdmacelllocation (
			ix, submission_id, metric, dtime, localdtime, system_id, network_id, ecio,
			dbm, base_station_id, base_station_latitude, base_station_longitude, geom, cma, block)
			VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
			""" % (SCHEMA_NAME, TABLE_NAME_PREFIX, ix, submission_id, metric, dtime, localdtime, system_id, network_id, ecio,\
			dbm, base_station_id, base_station_latitude, base_station_longitude, geom, cma, block)

		cur.execute(query)
		conn.commit()

	if type == 'cell_neighbour_tower_data':
		items = content.split('\t')
		(ix,submission_id,metric,dtime,localdtime,location_area_code,\
			cell_tower_id,network_type_code,network_type,umts_psc,rssi) = items
		
		(ix,submission_id,metric,dtime,localdtime,location_area_code,\
			cell_tower_id,network_type_code,network_type,umts_psc,rssi) = \
		map(process_null, (ix,submission_id,metric,dtime,localdtime,location_area_code,\
			cell_tower_id,network_type_code,network_type,umts_psc,rssi))

		query = """INSERT INTO %s.%s_cellneighbourtower (
			ix,submission_id,metric,dtime,localdtime,location_area_code,
			cell_tower_id,network_type_code,network_type,umts_psc,rssi)
			VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
			""" % (SCHEMA_NAME, TABLE_NAME_PREFIX, ix,submission_id,metric,dtime,localdtime,location_area_code,\
			cell_tower_id,network_type_code,network_type,umts_psc,rssi)

		cur.execute(query)
		conn.commit()


	if type == 'CLOSESTTARGET':
		items = content.split('\t')

		(ix,submission_id,dtime,localdtime,target,ipaddress) = items

		(ix,submission_id,dtime,localdtime,target,ipaddress) = \
		map(process_null, (ix,submission_id,dtime,localdtime,target,ipaddress))

		query = """INSERT INTO %s.%s_closesttarget (
			ix,submission_id,dtime,localdtime,target,ipaddress)
			VALUES (%s, %s, %s, %s, %s, %s)
			""" % (SCHEMA_NAME,TABLE_NAME_PREFIX,ix,submission_id,dtime,localdtime,target,ipaddress)

		cur.execute(query)
		conn.commit()


	if type == 'CPUACTIVITY':
		items = content.split('\t')

		(ix,submission_id,dtime,localdtime,success,max_average,read_average) = items
		(ix,submission_id,dtime,localdtime,success,max_average,read_average) = \
		map(process_null, (ix,submission_id,dtime,localdtime,success,max_average,read_average))

		query = """INSERT INTO %s.%s_cpuactivity (
			ix,submission_id,dtime,localdtime,success,max_average,read_average)
			VALUES (%s, %s, %s, %s, %s, %s, %s)
			""" % (SCHEMA_NAME,TABLE_NAME_PREFIX, ix,submission_id,dtime,localdtime,success,max_average,read_average)

		cur.execute(query)
		conn.commit()


	if type == 'DATACAP':
		items = content.split('\t')
		(ix,submission_id,dtime,localdtime,success) = items
		(ix,submission_id,dtime,localdtime,success) = \
		map(process_null, (ix,submission_id,dtime,localdtime,success))

		query = """INSERT INTO %s.%s_datacap (
			ix,submission_id,dtime,localdtime,success)
			VALUES (%s, %s, %s, %s, %s)
			""" % (SCHEMA_NAME,TABLE_NAME_PREFIX, ix,submission_id,dtime,localdtime,success)

		cur.execute(query)
		conn.commit()


	if type == 'gsm_cell_location':
		items = content.split('\t')

		(ix,submission_id,metric,dtime,localdtime,signal_strength,\
			umts_psc,location_area_code,cell_tower_id) = items

		(ix,submission_id,metric,dtime,localdtime,signal_strength,\
			umts_psc,location_area_code,cell_tower_id) = \
		map(process_null, (ix,submission_id,metric,dtime,localdtime,signal_strength,\
			umts_psc,location_area_code,cell_tower_id))

		query = """INSERT INTO %s.%s_gsmcelllocation (
			ix,submission_id,metric,dtime,localdtime,signal_strength,
			umts_psc,location_area_code,cell_tower_id)
			VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
			""" % (SCHEMA_NAME,TABLE_NAME_PREFIX, ix,submission_id,metric,dtime,localdtime,signal_strength,\
			umts_psc,location_area_code,cell_tower_id)

		cur.execute(query)
		conn.commit()


	if type in ('JHTTPGET', 'JHTTPGETMT'):
		items = content.split('\t')

		(ix,submission_id,dtime,localdtime,success,target,ipaddress,transfer_time,\
			transfer_bytes,bytes_sec,warmup_time,warmup_bytes,number_of_threads) = items

		(ix,submission_id,dtime,localdtime,success,target,ipaddress,transfer_time,\
			transfer_bytes,bytes_sec,warmup_time,warmup_bytes,number_of_threads) = \
		map(process_null, (ix,submission_id,dtime,localdtime,success,target,ipaddress,transfer_time,\
			transfer_bytes,bytes_sec,warmup_time,warmup_bytes,number_of_threads))

		query = """INSERT INTO %s.%s_httpget (
			ix,submission_id,dtime,localdtime,success,target,ipaddress,transfer_time,
			transfer_bytes,bytes_sec,warmup_time,warmup_bytes,number_of_threads)
			VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
			""" % (SCHEMA_NAME,TABLE_NAME_PREFIX, ix,submission_id,dtime,localdtime,success,target,ipaddress,transfer_time,\
			transfer_bytes,bytes_sec,warmup_time,warmup_bytes,number_of_threads)

		cur.execute(query)
		conn.commit()


	if type in ('JHTTPPOST', 'JHTTPPOSTMT'):
		items = content.split('\t')

		(ix,submission_id,dtime,localdtime,success,target,ipaddress,transfer_time,\
			transfer_bytes,bytes_sec,warmup_time,warmup_bytes,number_of_threads) = items

		(ix,submission_id,dtime,localdtime,success,target,ipaddress,transfer_time,\
			transfer_bytes,bytes_sec,warmup_time,warmup_bytes,number_of_threads) = \
		map(process_null, (ix,submission_id,dtime,localdtime,success,target,ipaddress,transfer_time,\
			transfer_bytes,bytes_sec,warmup_time,warmup_bytes,number_of_threads))

		query = """INSERT INTO %s.%s_httppost (
			ix,submission_id,dtime,localdtime,success,target,ipaddress,transfer_time,
			transfer_bytes,bytes_sec,warmup_time,warmup_bytes,number_of_threads)
			VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
			""" % (SCHEMA_NAME,TABLE_NAME_PREFIX, ix,submission_id,dtime,localdtime,success,target,ipaddress,transfer_time,\
			transfer_bytes,bytes_sec,warmup_time,warmup_bytes,number_of_threads)

		cur.execute(query)
		conn.commit()

	if type == 'location':
		items = content.split('\t')

		(ix,submission_id,metric,dtime,localdtime,source,latitude,longitude,accuracy) = items

		lat = float(latitude)
		lon = float(longitude)
		geom = get_geom_string(lat,lon)
		
		cma = get_cma(lat, lon)
		block = get_block(lat, lon)

		if cma is not None:
			cma = "'%s'" % (cma,)
		else:
			cma = "NULL"
		if block is not None:
			block = "'%s'" % (block,)
		else:
			block = "NULL"

		(ix,submission_id,metric,dtime,localdtime,source,latitude,longitude,accuracy) = \
		map(process_null, (ix,submission_id,metric,dtime,localdtime,source,latitude,longitude,accuracy))

		query = """INSERT INTO %s.%s_location (
				ix,submission_id,metric,dtime,localdtime,source,latitude,longitude,accuracy, geom, cma, block)
				VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
				""" % (SCHEMA_NAME,TABLE_NAME_PREFIX, ix,submission_id,metric,dtime,localdtime,source,\
				latitude,longitude,accuracy, geom, cma, block)

		cur.execute(query)
		conn.commit()


	if type == 'NETACTIVITY':
		items = content.split('\t')

		(ix,submission_id,dtime,localdtime,success,maxbytesout,maxbytesin,bytesout,bytesin) = items

		(ix,submission_id,dtime,localdtime,success,maxbytesout,maxbytesin,bytesout,bytesin) = \
		map(process_null, (ix,submission_id,dtime,localdtime,success,maxbytesout,maxbytesin,bytesout,bytesin))

		query = """INSERT INTO %s.%s_netactivity (
				ix,submission_id,dtime,localdtime,success,maxbytesout,maxbytesin,bytesout,bytesin)
				VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
				""" % (SCHEMA_NAME,TABLE_NAME_PREFIX, ix,submission_id,dtime,localdtime,success,maxbytesout,maxbytesin,bytesout,bytesin)

		cur.execute(query)
		conn.commit()


	if type == 'net_usage':
		items = content.split('\t')

		(ix,submission_id,dtime,localdtime,duration,total_rx_bytes,total_tx_bytes,\
			mobile_rx_bytes,mobile_tx_bytes,app_rx_bytes,app_tx_bytes) = items

		(ix,submission_id,dtime,localdtime,duration,total_rx_bytes,total_tx_bytes,\
			mobile_rx_bytes,mobile_tx_bytes,app_rx_bytes,app_tx_bytes) = \
		map(process_null, (ix,submission_id,dtime,localdtime,duration,total_rx_bytes,total_tx_bytes,\
			mobile_rx_bytes,mobile_tx_bytes,app_rx_bytes,app_tx_bytes))

		query = """INSERT INTO %s.%s_netusage (
				ix,submission_id,dtime,localdtime,duration,total_rx_bytes,total_tx_bytes,\
					mobile_rx_bytes,mobile_tx_bytes,app_rx_bytes,app_tx_bytes)
				VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
				""" % (SCHEMA_NAME,TABLE_NAME_PREFIX, ix,submission_id,dtime,localdtime,duration,total_rx_bytes,total_tx_bytes,\
						mobile_rx_bytes,mobile_tx_bytes,app_rx_bytes,app_tx_bytes)

		cur.execute(query)
		conn.commit()


	if type == 'network_data':
		items = content.split('\t')

		(ix,submission_id,metric,dtime,localdtime,connected,active_network_type_code,\
			active_network_type,sim_operator_code,sim_operator_name,roaming,\
			phone_type_code,phone_type,network_type_code,network_type,\
			network_operator_code,network_operator_name) = items

		(ix,submission_id,metric,dtime,localdtime,connected,active_network_type_code,\
			active_network_type,sim_operator_code,sim_operator_name,roaming,\
			phone_type_code,phone_type,network_type_code,network_type,\
			network_operator_code,network_operator_name) = \
		map(process_null, (ix,submission_id,metric,dtime,localdtime,connected,active_network_type_code,\
			active_network_type,sim_operator_code,sim_operator_name,roaming,\
			phone_type_code,phone_type,network_type_code,network_type,\
			network_operator_code,network_operator_name))

		query = """INSERT INTO %s.%s_networkdata (
				ix,submission_id,metric,dtime,localdtime,connected,active_network_type_code,
				active_network_type,sim_operator_code,sim_operator_name,roaming,
				phone_type_code,phone_type,network_type_code,network_type,
				network_operator_code,network_operator_name)
				VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
				""" % (SCHEMA_NAME,TABLE_NAME_PREFIX, ix,submission_id,metric,dtime,localdtime,connected,active_network_type_code,\
						active_network_type,sim_operator_code,sim_operator_name,roaming,\
						phone_type_code,phone_type,network_type_code,network_type,\
						network_operator_code,network_operator_name)

		cur.execute(query)
		conn.commit()


	if type == 'JUDPLATENCY':
		items = content.split('\t')

		(ix,submission_id,dtime,localdtime,success,target,ipaddress,\
			rtt_avg,rtt_min,rtt_max,rtt_stddev,received_packets,lost_packets) = items

		(ix,submission_id,dtime,localdtime,success,target,ipaddress,\
			rtt_avg,rtt_min,rtt_max,rtt_stddev,received_packets,lost_packets) = \
			map(process_null, (ix,submission_id,dtime,localdtime,success,target,ipaddress,\
				rtt_avg,rtt_min,rtt_max,rtt_stddev,received_packets,lost_packets))

		query = """INSERT INTO %s.%s_udplatency (
				ix,submission_id,dtime,localdtime,success,target,ipaddress,\
				rtt_avg,rtt_min,rtt_max,rtt_stddev,received_packets,lost_packets)
				VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
				""" % (SCHEMA_NAME,TABLE_NAME_PREFIX, ix,submission_id,dtime,localdtime,success,target,ipaddress,\
						rtt_avg,rtt_min,rtt_max,rtt_stddev,received_packets,lost_packets)

		cur.execute(query)
		conn.commit()


	if type == 'submission':
		items = content.split('\t')

		(submission_id,enterprise_id,dtime,localdtime,devicedtime,\
				schedule_config_version,sim_operator_code,submission_type,\
				timezone,received,source_ip,app_version_code,app_version_name,\
				tests,metrics,conditions,os_type,os_version,model,manufacturer,\
				imei,imsi,iosapp_id) = items

		(submission_id,enterprise_id,dtime,localdtime,devicedtime,\
				schedule_config_version,sim_operator_code,submission_type,\
				timezone,received,source_ip,app_version_code,app_version_name,\
				tests,metrics,conditions,os_type,os_version,model,manufacturer,\
				imei,imsi,iosapp_id) = \
					map(process_null, (submission_id,enterprise_id,dtime,localdtime,devicedtime,\
						schedule_config_version,sim_operator_code,submission_type,\
						timezone,received,source_ip,app_version_code,app_version_name,\
						tests,metrics,conditions,os_type,os_version,model,manufacturer,\
						imei,imsi,iosapp_id))
		query = """INSERT INTO %s.%s_submission (
				submission_id,enterprise_id,dtime,localdtime,devicedtime,
				schedule_config_version,sim_operator_code,submission_type,
				timezone,received,source_ip,app_version_code,app_version_name,
				tests,metrics,conditions,os_type,os_version,model,manufacturer, imei,imsi,iosapp_id)
				VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
				""" % (SCHEMA_NAME,TABLE_NAME_PREFIX, submission_id,enterprise_id,dtime,localdtime,devicedtime,\
					schedule_config_version,sim_operator_code,submission_type,\
					timezone,received,source_ip,app_version_code,app_version_name,\
					tests,metrics,conditions,os_type,os_version,model,manufacturer,\
					imei,imsi,iosapp_id)

		cur.execute(query)
		conn.commit()

def drop_tables(conn, cur):
	drop_table(conn, cur, 'cdmacelllocation')
	drop_table(conn, cur, 'cellneighbourtower')
	drop_table(conn, cur, 'closesttarget')
	drop_table(conn, cur, 'cpuactivity')
	drop_table(conn, cur, 'datacap')
	drop_table(conn, cur, 'gsmcelllocation')
	drop_table(conn, cur, 'httpget')
	drop_table(conn, cur, 'httppost')
	drop_table(conn, cur, 'location')
	drop_table(conn, cur, 'netactivity')
	drop_table(conn, cur, 'netusage')
	drop_table(conn, cur, 'networkdata')
	drop_table(conn, cur, 'udplatency')
	drop_table(conn, cur, 'submission')

def drop_table(conn, cur, name):
	table = "%s.%s_%s" % (SCHEMA_NAME, TABLE_NAME_PREFIX, name)
	query = "DROP TABLE IF EXISTS %s" % table
	cur.execute(query)
	conn.commit()


def get_date(conn, cur, a):
	query = """SELECT %s FROM %s.%s_dates ORDER BY id DESC LIMIT 1""" % (a, SCHEMA_NAME, TABLE_NAME_PREFIX)
	cur.execute(query)
	rows = cur.fetchall()
	if rows == []:
		return None
	else:
		return rows[0][0]

def add_date_to_table(conn,cur, date):
	a = get_date(conn, cur, 'all_imported_dates')['all_imported_dates']
	a = [str(i) for i in a]
	a.append(date)
	entry = {"all_imported_dates": a}
	entry = re.sub("'", '"', str(entry))
	query = """UPDATE %s.%s_dates SET all_imported_dates = '%s'""" % (SCHEMA_NAME, TABLE_NAME_PREFIX, entry)
	cur.execute(query)
	conn.commit()
	query = """UPDATE %s.%s_dates SET last_imported_date = '%s'""" % (SCHEMA_NAME, TABLE_NAME_PREFIX, date)
	cur.execute(query)
	conn.commit()

	
def next_date(d):
	da = datetime.datetime.strptime(d, '%Y%m%d').date()
	da = da + datetime.timedelta(days=1)
	ret = da.strftime('%Y%m%d')
	return ret

	
def write_log(out_str):
	logs_dir = BASE_PATH + '/logs'
	log_path = '%s/log_%s' % (logs_dir, TODAY)
	fp_log = open(log_path, 'a')
	fp_log.write(out_str)
	fp_log.close()

	
def get_tar_file(date):
	#get tar file
	CHUNKSIZE = 256
	
	parser = config.Config()
	base_url = parser['vizmo_import']['test_url']
	url = base_url + '/' + filename
	username = parser['vizmo_import']['test_username']
	password = parser['vizmo_import']['test_password']
	request = requests.get(url, stream=True, auth=(username, password))

	with open(outfile_path, 'wb') as file:
		for chunk in request.iter_content(CHUNKSIZE):
	 		file.write(chunk)

			
def get_geom_string(lat, lon):
	geom = 'null'
	if (lat >= -90 and lat <= 90 and lon >= -180 and lon <= 180):
		geom = "ST_GeomFromText('POINT(%s %s)', 4326)" % (lon, lat)

	return geom

def process_null(a):
	if a in ('\\N', 'NA') or 'null' in a:
		return 'null'
	elif a == 'true':
		return "'1'"
	elif a == 'false':
		return "'0'"
	else:
		a = re.sub("'", "''", a)
		return "'%s'" % a



#tries to extract a value from an array, if not present returns  default
def get(assoc, key, default):
	return assoc[key] if key in assoc else default


def getConfiguration():
	BASE_PATH = config.Config()['postgres']['base_path']
	json_config_file = BASE_PATH + '/config.json'
	fp = open(json_config_file, 'r')
	conf = fp.read()
	fp.close()

	return js.loads(conf)


def basename(file_path):
	bname = re.sub('^.*/', '', file_path)

	return bname


def get_submission_id(bname):
	item = re.sub('^.*_', '', bname)
	item = item.replace('.json', '')

	return item


def getEnterpriseId(json):
	enterprise_id = json[ENTERPRISE_ID]
	if len(enterprise_id) == 0 or len(enterprise_id) > 255:
		enterprise_id = NO_ENTERPRISE_ID
	if '.' in enterprise_id and enterprise_id.index('.') == 0:
		enterprise_id = NO_ENTERPRISE_ID
	if '/' in enterprise_id:
		enterprise_id = NO_ENTERPRISE_ID

	return enterprise_id

def filesSuffix(enterprise_id, timestamp):
	time = int(timestamp) - (int(timestamp) % int(OUTFILE_NAME_TIME))
	ret = OUTFILE_NAME_DELIMITER + enterprise_id + OUTFILE_NAME_DELIMITER + str(time)

	return ret


def getTestsTimesAndTypes(configuration, json):

	ret = {}
	if not JSON_TESTS_SECTION in json:
		return ret

	tests = json[JSON_TESTS_SECTION]
	tests_len = len(tests)
	for e in tests:
		if not JSON_TYPE in e:
			continue
		if not JSON_TIMESTAMP in e:
			continue

		#retrive the metric name from the configuration if available 
		#otherwise use the type field from the json file
		ret[e[JSON_TIMESTAMP]] = configuration['objects'][e[JSON_TYPE]]['metric'] if 'metric' in configuration['objects'][e[JSON_TYPE]] else e[JSON_TYPE]
	return ret

#converts the timezone field to utc offset second
def hour2seconds(tz):
	return int(float(tz)) * 3600


#convert a unix timestamp to a format suitable for importing into the db
def ts2utc(timestamp):
	if int(timestamp) > 9999999999 or int(timestamp) < 0:
		timestamp = 0
	return datetime.datetime.fromtimestamp(int(timestamp)).strftime(DATETIME_FORMAT)


#function to convert boolean values and boolean strings to integers
def filter_boolean(value):
	ret = 0
	value_type = type(value)
	if value_type == int:
		ret = value
	elif value_type == bool:
		ret = 1 if value else 0
	#elif value_type == str:
	else:
		ret = 1 if value == 'true' else 0

	return ret

def count(l):
	return len(l)


#compute the correct value from the context
def getContext(context, type, entry):
	if type == CONTEXT_TEST_TIMES:
		return context[type][entry] if entry in context[type] else OUTPUTNULL
	if type == CONTEXT_TZOFFSET:
		ts = int(context[type]) + int(entry)
		if ts < 0 or ts > 9999999999:
			ts = 0
		d = datetime.datetime.fromtimestamp(ts).strftime(DATETIME_FORMAT)
		return d



#replace special character from field 
def stripField(field):
	if type(field) != str:
		return field
	field = field.replace(OUTPUTFIELDDELIMITER, '    ')
	field = field.replace(OUTPUTRECORDDELIMITER, ' ')	
	return field


def getDataFileName(description, fileSuffix):
	dirname = BASE_PATH + '/' + DATA_DIR
	if  not os.path.isdir(dirname):
		os.makedirs(dirname)
	#ret = dirname + '/' + description['outfile'] + fileSuffix
	ret = dirname + '/' + description['outfile']

	return ret


def appendToFile(filename, content):
	ret = True
	fp = open(filename, 'a')
	try:
		fp.write(content)
	except:
		ret = False
	fp.close()

	return ret


#append the passed message to the error log file
def errorLog(error_msg):
	time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

	message = '[' +  time + '] [error] ' + error_msg + '\n'
	print(message)

	dirname= BASE_PATH + '/'  + LOG_DIR
	if  not os.path.isdir(dirname):
		os.makedirs(dirname)
	appendToFile(dirname + '/error.log', message)


#parse an string array in the json file and produce a record per item in the array
def parseArray(submission_id, entry):
	entry_size = len(entry)

	output = []
	for i in range(entry_size):
		output.append(submission_id + OUTPUTFIELDDELIMITER + stripField(entry[i]))

	return '\n'.join(output)


#process an array in the json file, and appends the parsed to the appropriate file
def processArray(configuration, context, type, entry, fileSuffix):

	if configuration['array'][type]['active'] != 'true':
		return

	filename = getDataFileName(configuration['array'][type], fileSuffix)

	content = parseArray(context[CONTEXT_SUBMISSION_STRING], entry) + '\n'
	if  not appendToFile(filename, content):
		errorLog('problem in appending content to ' + filename)

#given a description a context and an entry returns the output value
def parseValue(description, context, entry):
	ret = description
	if ENTRY_NAME_PREFIX in description and description.index(ENTRY_NAME_PREFIX) == 0:
		description = description[1:]
		e = description.split(FUNCTION_DELIMITER)
		if  not e[0] in entry:
			ret = OUTPUTNULL
		elif len(e) == 1:
			ret = stripField(entry[e[0]])
		else:
			#output field is function of the input entry field
			ret = stripField(globals()[e[1]](entry[e[0]]))

	elif CONTEXT_NAME_DELIMITER in description and description.index(CONTEXT_NAME_DELIMITER) == 0:
		description = description[1:]
		e = description.split(FUNCTION_DELIMITER)
		if not e[0] in context:
			ret = OUTPUTNULL
		elif len(e) == 1:
			ret = context[e[0]]
		else:
			ret = getContext(context, e[0], entry[e[1]])

	if type(ret) == bool:
		if ret == True:
			ret = '1'
		else:
			ret = '0'
	#elif type(ret) == unicode:
	#	ret = ret.encode('ascii', 'ignore')
	#	pass
	else:
		ret = str(ret)

	return ret


# parse a json object according to the description provided
def parseObject(entry, context, description):
	desc_size = len(description)
	output = []
	for d in description:
		output.append(parseValue(d, context, entry))
	output = OUTPUTFIELDDELIMITER.join(output) + OUTPUTRECORDDELIMITER

	return output


#process an entry in the json file, and appends the parsed output to the appropriate file
def processEntry(configuration, context, entry, fileSuffix, conf_type = None):
	type =  entry[JSON_TYPE] if conf_type is None else conf_type

	if not type in configuration['objects'] or configuration['objects'][type]['active'] != 'true':
		return

	filename = getDataFileName(configuration['objects'][type], fileSuffix)
	content = parseObject(entry, context, configuration['objects'][type]['outformat'])

	# if  not appendToFile(filename, content):
	# 	errorLog('problem in appending content to ' + filename)

	if type in ('cdma_cell_location', 'cell_neighbour_tower_data', 'CLOSESTTARGET', 'CPUACTIVITY', 'DATACAP',\
				'gsm_cell_location', 'JHTTPGET', 'JHTTPGETMT', 'JHTTPPOST', 'JHTTPPOSTMT',\
				'location', 'NETACTIVITY', 'net_usage', 'network_data', 'JUDPLATENCY', 'submission'):
		write_to_table(type, content)



def processSubmission(configuration, json, submission_id):
	enterprise_id = getEnterpriseId(json)
	fileSuffix = filesSuffix(enterprise_id, json['_received']);
	context = {}
	context[CONTEXT_SUBMISSION_STRING] = submission_id
	context[CONTEXT_TEST_TIMES] = getTestsTimesAndTypes(configuration, json)
	context[CONTEXT_ENTERPRISE_ID] = getEnterpriseId(json)
	context[CONTEXT_TZOFFSET] = hour2seconds(get(json, 'timezone', 0))
	#main section of the file
	#used to merge the object generating the submission table
	mainSection = {}
	for s, t in configuration['sections'].items():
		if not s in json:
			continue
		if t == 'array':
			processArray(configuration, context, s, json[s], fileSuffix)
		elif t == 'objects':
			entry_len = len(json[s])
			for i in range(entry_len):
				e = json[s][i]
				if not 'type' in e:
					continue

				if e['type'] == 'phone_identity':
					mainSection = dict(list(e.items()) + list(json.items()))
				else:
					context[CONTEXT_INDEX]= i
					processEntry(configuration, context, e, fileSuffix)


	processEntry(configuration, context, mainSection, fileSuffix, 'submission')


def getPgConnection():
	parser = config.Config()
	host = parser['postgres']['host']
	port = parser['postgres']['port']
	dbname = parser['postgres']['dbname']
	user = parser['postgres']['user']
	password = parser['postgres']['password']
	arg_str = 'host=%s port=%s dbname=%s user=%s password=%s' % (host, port, dbname, user, password)
	conn = psycopg2.connect(arg_str)
	cur = conn.cursor()
	return (conn, cur)
	
def get_cma(lat, lon):
	query = """SELECT id FROM fcc_gis.cma_2010 WHERE ST_CONTAINS(geom, ST_GeomFromText('POINT(%s %s)', 4326))""" % (lon, lat)
	cur.execute(query)
	ret = cur.fetchone()
	if ret is None:
		return None
	else:
		return ret[0]

def get_block(lat, lon):
	query = """SELECT geoid10 FROM fcc_gis.block_2010 WHERE ST_CONTAINS(geom, ST_GeomFromText('POINT(%s %s)', 4326))""" % (lon, lat)
	cur.execute(query)
	ret = cur.fetchone()
	if ret is None:
		return None
	else:
		return ret[0]
	


# location of the output files
DATA_DIR = 'logs/data'
# logs directory 
LOG_DIR = 'logs'
# directory storing received json files
JSON_DIR = 'data'
# directory for saving all recieved json files
UNASSIGNED = 'unassinged'
# prefix of the field name in the json file 
ENTRY_NAME_PREFIX = '$' 
# delimiter used in the config file to specify what funtion to apply to a field
FUNCTION_DELIMITER = ':' 
# delimiter telling a field comes from the context not to the entry itself
CONTEXT_NAME_PREFIX = '#'
# date time format for import in the database
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
# missing value for output
OUTPUTNULL = '\\N' 
# field delimiter for the putput file
OUTPUTFIELDDELIMITER = '\t' 
# record delimiter for the output file
OUTPUTRECORDDELIMITER = '\n'
# time accuracy for the output file name, expressed in seconds. Set to be 5 minutes
OUTFILE_NAME_TIME = '300' 
# delimiter for the different part fo file names
OUTFILE_NAME_DELIMITER = '.' 
# value to be used as enterprise_id when a value is missing or cannot be used
NO_ENTERPRISE_ID = 'no_enterprise_id' 
# enterprise_id field name in the json file
ENTERPRISE_ID = 'enterprise_id' 
# value to be used if no sim operator code is reported
NO_SIM = 'no_sim'
# file name for configuration file
CONFIG_FILE = 'config.json' 
# date time format for file name
DATE_FORMAT_FILE = 'YmdHis'
# date format for directory
DATE_FORMAT_DIRECTORY = 'Ymd'
# type index in the json blob
JSON_TYPE = 'type'
# timestamp index in the json blob
JSON_TIMESTAMP = 'timestamp'
# json section containing the tests
JSON_TESTS_SECTION = 'tests'
# context submission string
CONTEXT_SUBMISSION_STRING = 'submission_string'
# context index 
CONTEXT_INDEX = 'index'
# context enty for tests times
CONTEXT_TEST_TIMES = 'test_times'
# context entry for the enterprise_id
CONTEXT_ENTERPRISE_ID = 'enterprise_id'
# context entry for the source ip
CONTEXT_TZOFFSET = 'tzoffset'
# context entry for the IMEI
CONTEXT_IMEI = 'imei'
# context entry for the IMSI
CONTEXT_IMSI = 'imsi'
# context entry for the app_id
CONTEXT_APPID = 'app_id'
# prefix for the entry to be found in the context
CONTEXT_NAME_DELIMITER = '#'
# json entry for the sim operator code
SIM_OPERATOR_CODE = 'sim_operator_code'
# log empty field 
LOG_EMPTY_FIELD = '-'
# database schema name
SCHEMA_NAME = 'oet_mba'
# table name prefix
TABLE_NAME_PREFIX = 'vizmo'

while True:
	#get db connection
	(conn, cur) = getPgConnection()
	conn.autocommit = True

	#setup_dates_table(conn, cur) # for first batch run, commented out during daily run

	configuration = getConfiguration()

	BASE_PATH = config.Config()['postgres']['base_path']
	print(BASE_PATH)


	FIRST_DATE = '20131111'
	TODAY = datetime.datetime.now()
	YESTERDAY = (TODAY - datetime.timedelta(days=1))
	TODAY = TODAY.strftime('%Y%m%d')
	YESTERDAY = YESTERDAY.strftime('%Y%m%d')
	#TODAY = '20131111'
	#YESTERDAY = '2011110'
	last_imported_date = get_date(conn, cur, 'last_imported_date')
	if last_imported_date is None:
		last_imported_date = FIRST_DATE

	all_imported_dates = get_date(conn, cur, 'all_imported_dates')['all_imported_dates']

	dates_to_process = []
	date0 = last_imported_date
	while True:
		date0 = next_date(date0)
		if date0 > TODAY:
			break
		if date0 not in all_imported_dates:
			dates_to_process.append(date0)


	out_str = "%s: Starting processing session.\nNumber of days to process: %s %s\n\n" % (time.ctime(), len(dates_to_process), dates_to_process)
	print(out_str)

	write_log(out_str)

	#drop_tables(conn, cur) #one-time drop all tables before first batch run, comment out during daily run
	#create_tables(conn, cur) #one-time create all tables if not exists, commented out during daily run

	ts_start = time.time()
	for date in dates_to_process:

		out_str = '%s: Start processing %s data: ' % (time.ctime(), date)
		print(out_str)
		write_log(out_str)
		
		date_dir = BASE_PATH + '/' + JSON_DIR + '/' + date
		raw_dir = date_dir + '/raw'
		json_dir = date_dir + '/json'
		if not os.path.exists(raw_dir):
			os.makedirs(raw_dir)
		if not os.path.exists(json_dir):
			os.makedirs(json_dir)
			
		filename = '%s-fcc-android.tar.gz' % date
		outfile_path = raw_dir + '/' + filename
		
		get_tar_file(date)
		
		if os.stat(outfile_path).st_size < 10000:
			out_str = '%s: empty tar file, skipping...\n\n' % (time.ctime())
			print(out_str)
			write_log(out_str)
			continue
		
		t = tarfile.open(outfile_path, 'r:gz')
		n = 0
		num_for_date = len(t.getmembers())
		out_str = '%s JSON files\n\n' % (num_for_date)
		print(out_str)
		write_log(out_str)
		for member_info in t.getmembers():
			json_filename = member_info.name
			if '.json' in json_filename:
				try:
					n += 1
					#print(date, n)
					f = t.extractfile(member_info)
					content = f.read().decode('utf-8')
					json = js.loads(content)
					bname = basename(json_filename)
					submission_id = get_submission_id(bname)
					processSubmission(configuration, json, submission_id)
				except:
					out_str = 'ERROR: ' + str(sys.exc_info()[1])
					print(out_str)
					write_log(out_str)
					
		
		add_date_to_table(conn, cur, date)

		out_str = '%s: End processing %s.\n\n' % (time.ctime(), date)
		print(out_str)
		write_log(out_str)
		#remove tar file if disk space is low
		os.remove(outfile_path)
		
	ts_end = time.time()
	dt = ts_end - ts_start
	minutes = int(dt/60)
	seconds = int(dt - minutes*60)
		
	time_elapse = '%s minutes %s seconds' % (minutes, seconds)

	out_str = """End of processing session: Time used: %s\n======================================\n\n""" % time_elapse
	print(out_str)
	write_log(out_str)

	conn.close()

	#wait 1 hour until next run
	time.sleep(3600)

