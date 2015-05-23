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
import sqlite3
import json
import logging
import requests
import yaml
from core import coreResource
from core import addRouteResource
from core import addDataResource
from core import addTableResource
from core import getAllRoutesResource
from core import deleteRoutesResource
from core import initMetaDBResource
from core import initPokemonResource

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
		dbconn = sqlite3.connect(configuration['db']['database'])
		meta_dbconn = sqlite3.connect(configuration['meta-api-db']['database'])
		cursor = meta_dbconn.cursor()
		try:
			cursor.execute('select * from routes')
			routes = cursor.fetchall()
			for list in routes:
				resource = coreResource(configuration, meta_dbconn, dbconn, list[2] )
				app.add_route(list[1], resource)
		except: 
			exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
			print('exception %s was thrown' % exceptionValue)
		addResource = addRouteResource(configuration, meta_dbconn, dbconn, app)
		app.add_route('/addRoute', addResource)
		adddataResource = addDataResource(configuration, meta_dbconn, dbconn)
		app.add_route('/addData', adddataResource)
		addtableResource = addTableResource(configuration, meta_dbconn, dbconn)
		app.add_route('/addTable', addtableResource)
		listroutesResource = getAllRoutesResource(configuration, meta_dbconn, dbconn)
		app.add_route('/allRoutes', listroutesResource )
		deleteroutesResource = deleteRoutesResource(configuration, meta_dbconn, dbconn)
		app.add_route('/deleteRoute/id/{id}', deleteroutesResource )
		initResource = initMetaDBResource(configuration, meta_dbconn, dbconn)
		app.add_route('/init', initResource )
		initpokemonResource = initPokemonResource(configuration, meta_dbconn, dbconn)
		app.add_route('/Pokemoninit', initpokemonResource )
	except: 
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		print('exception %s was thrown' % exceptionValue)
	return app

if __name__ == '__main__':
# For testing outside a WSGI like gunicorn
	httpd = simple_server.make_server('0.0.0.0', PORT, build_app(sys.argv[1]))
	httpd.serve_forever()

