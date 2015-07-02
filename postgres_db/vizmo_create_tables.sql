--cdmacelllocation
DROP TABLE IF EXISTS oet_mba.vizmo_cdmacelllocation;
COMMIT;
CREATE TABLE IF NOT EXISTS oet_mba.vizmo_cdmacelllocation (
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
		);
COMMIT;


--cellneighbourtower
DROP TABLE IF EXISTS oet_mba.vizmo_cellneighbourtower;
COMMIT;
CREATE TABLE IF NOT EXISTS oet_mba.vizmo_cellneighbourtower (
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
		);
COMMIT;


--closesttarget
DROP TABLE IF EXISTS oet_mba.vizmo_closesttarget;
COMMIT;
CREATE TABLE IF NOT EXISTS oet_mba.vizmo_closesttarget (
		id serial primary key,
		ix smallint NOT NULL DEFAULT 0::smallint,
		submission_id character(32) NOT NULL DEFAULT ''::bpchar,
		dtime timestamp without time zone NOT NULL,
		localdtime timestamp without time zone NOT NULL,
		target character varying(100) DEFAULT NULL::character varying,
		ipaddress character varying(46) DEFAULT NULL::character varying
		);
COMMIT;


--closesttarget
DROP TABLE IF EXISTS oet_mba.vizmo_cpuactivity;
COMMIT;
CREATE TABLE IF NOT EXISTS oet_mba.vizmo_cpuactivity (
		id serial primary key,
		ix smallint NOT NULL DEFAULT 0::smallint,
		submission_id character(32) NOT NULL DEFAULT ''::bpchar,
		dtime timestamp without time zone NOT NULL,
		localdtime timestamp without time zone NOT NULL,
		success smallint DEFAULT 0::smallint,
		max_average integer DEFAULT 0,
		read_average integer DEFAULT 0
		);
COMMIT;


--datacap
DROP TABLE IF EXISTS oet_mba.vizmo_datacap;
COMMIT;
CREATE TABLE IF NOT EXISTS oet_mba.vizmo_datacap (
		id serial primary key,
		ix smallint NOT NULL DEFAULT 0::smallint,
		submission_id character(32) NOT NULL DEFAULT ''::bpchar,
		dtime timestamp without time zone NOT NULL,
		localdtime timestamp without time zone NOT NULL,
		success smallint
		);
COMMIT;


--gsmcelllocation
DROP TABLE IF EXISTS oet_mba.vizmo_gsmcelllocation;
COMMIT;
CREATE TABLE IF NOT EXISTS oet_mba.vizmo_gsmcelllocation (
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
		);
COMMIT;
		

--httpget
DROP TABLE IF EXISTS oet_mba.vizmo_httpget;
COMMIT;
CREATE TABLE IF NOT EXISTS oet_mba.vizmo_httpget (
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
		);
COMMIT;		


--httppost
DROP TABLE IF EXISTS oet_mba.vizmo_httppost;
COMMIT;
CREATE TABLE IF NOT EXISTS oet_mba.vizmo_httppost (
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
		);
COMMIT;


--location
DROP TABLE IF EXISTS oet_mba.vizmo_location;
COMMIT;
CREATE TABLE IF NOT EXISTS oet_mba.vizmo_location (
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
		);
COMMIT;


--netactivity
DROP TABLE IF EXISTS oet_mba.vizmo_netactivity;
COMMIT;
CREATE TABLE IF NOT EXISTS oet_mba.vizmo_netactivity (
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
		);
COMMIT;


--netusage
DROP TABLE IF EXISTS oet_mba.vizmo_netusage;
COMMIT;
CREATE TABLE IF NOT EXISTS oet_mba.vizmo_netusage (
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
		);
COMMIT;


--vizmo_networkdata
DROP TABLE IF EXISTS oet_mba.vizmo_networkdata;
COMMIT;
CREATE TABLE IF NOT EXISTS oet_mba.vizmo_networkdata (
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
		);
COMMIT;

--vizmo_udplatency
DROP TABLE IF EXISTS oet_mba.vizmo_udplatency;
COMMIT;
CREATE TABLE IF NOT EXISTS oet_mba.vizmo_udplatency (
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
		);
COMMIT;


--vizmo_submission
DROP TABLE IF EXISTS oet_mba.vizmo_submission;
COMMIT;
CREATE TABLE IF NOT EXISTS oet_mba.vizmo_submission (
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
		);
COMMIT;

--vismo_dates
DROP TABLE IF EXISTS oet_mba.vizmo_dates;
COMMIT;
CREATE TABLE oet_mba.vizmo_dates (
	id serial primary key,
	last_imported_date character varying(8),
	all_imported_dates json
	);
COMMIT;
	
INSERT INTO oet_mba.vizmo_dates (last_imported_date, all_imported_dates)
				VALUES (null, '{"all_imported_dates": []}');
COMMIT;


