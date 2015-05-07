"""
A REST API that builds itself!

Requirements
- Falcon
- postgres
- psygop2

"""

from wsgiref import simple_server
import os
import sys
import falcon
import psycopg2
import psycopg2.pool
import json
import logging
import requests
import yaml
from core import coreResource
from core import addRouteResource
from core import addDataResource
from core import addTableResource
from core import getAllRoutesResource

fmt = lambda obj: json.dumps(obj, indent=4, sort_keys=True)

PORT=int(os.getenv('META_API_PORT', '8080'))

def cors_header(req, resp):
	""" Set CORs Header in response """
	resp.set_header('Access-Control-Allow-Origin', '*')

def build_app(yml_path):
	with open(yml_path) as data:
		configuration = yaml.safe_load(data)
		app = falcon.API(after=[cors_header])
	try:
		dbconn = psycopg2.pool.ThreadedConnectionPool(1, 20, user=configuration['db']['user'], password=configuration['db']['password'], host=configuration['db']['host'], database=configuration['db']['database'])
		meta_dbconn = psycopg2.pool.ThreadedConnectionPool(1, 20, user=configuration['meta-api-db']['user'], password=configuration['meta-api-db']['password'], host=configuration['meta-api-db']['host'], database=configuration['meta-api-db']['database'])
		meta_dbconn2 = meta_dbconn.getconn()
		cursor = meta_dbconn2.cursor()
		cursor.execute('select * from routes')
		routes = cursor.fetchall()
		for list in routes:
			resource = coreResource(configuration, meta_dbconn, dbconn, list[2] )
			app.add_route(list[1], resource)
		addResource = addRouteResource(configuration, meta_dbconn, dbconn, app)
		app.add_route('/addRoute', addResource)
		adddataResource = addDataResource(configuration, meta_dbconn, dbconn)
		app.add_route('/addData', adddataResource)
		addtableResource = addTableResource(configuration, meta_dbconn, dbconn)
		app.add_route('/addTable', addtableResource)
		listroutesResource = getAllRoutesResource(configuration, meta_dbconn, dbconn)
		app.add_route('/allRoutes', listroutesResource )
	except: 
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		print('exception %s was thrown' % exceptionValue)
	return app

if __name__ == '__main__':
# For testing outside a WSGI like gunicorn
	httpd = simple_server.make_server('0.0.0.0', PORT, build_app(sys.argv[1]))
	httpd.serve_forever()

