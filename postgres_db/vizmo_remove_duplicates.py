import sys
import psycopg2
import os
import re
import config

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

	
#get db connection
(conn, cur) = getPgConnection()
conn.autocommit = True

print(conn, cur)


table_names = ["vizmo_submission"]

SCHEMA_NAME = 'oet_mba'

for t in table_names:
	query = """SELECT distinct submission_id FROM %s.%s""" % (SCHEMA_NAME, t)
	cur.execute(query)
	rows = cur.fetchall()
	submission_id = []
	for r in rows:
		submission_id.append(r[0])
	
	n = 0
	nn = 0
	for id in submission_id:
		n += 1
		query = """SELECT id FROM %s.%s WHERE submission_id = '%s'""" % (SCHEMA_NAME, t, id)
		cur.execute(query)
		rows = cur.fetchall()
		ids = []
		for r in rows:
			ids.append(r[0])
		if len(ids) > 1:
			nn += 1
			str1 = str(ids[1:])
			str1 = str1.replace('[', '(')
			str1 = str1.replace(']', ')')
			query = """DELETE FROM %s.%s WHERE id IN %s""" % (SCHEMA_NAME, t, str1)
			print(n, nn, ids, query)
			cur.execute(query)
			conn.commit()