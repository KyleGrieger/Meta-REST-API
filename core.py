import sys
import sqlite3
import json
import logging
import falcon

fmt = lambda obj: json.dumps(obj, indent=4, sort_keys=True)

class coreResource(object):

    def __init__(self, config, meta_dbconn, dbconn, query, **kwargs):

        self.logger = logging.getLogger(__name__)
        self.configuration = config
        self.meta_dbconn = meta_dbconn
        self.dbconn = dbconn
        self.query = query

    def on_get(self, req, resp, **kwargs):
    	variabs = kwargs
    	result = {}
    	result['data'] = self.run_query(variabs)
    	self.logger.debug('run query' + self.query)
    	resp.set_header('Content-Type', 'application/json')
    	resp.status = falcon.HTTP_200
    	resp.body = fmt(result)

    def run_query(self, variabs):
    	result = []
    	try:
    		queryResult = []
    		cursor = self.dbconn.cursor()
    		if len(variabs) > 0:
    			cursor.execute(self.get_vars(variabs))
    		elif len(variabs) == 0:
    			cursor.execute(self.query)
    		self.dbconn.commit()
    		queryResult = cursor.fetchall()
    		return queryResult
    	except:
    		return queryResult

    def get_vars(self, variabs):
    	try:
    		cursor = self.dbconn.cursor()
    		editedQuery = self.query
    		if len(variabs.values()) > 0:
    			for key, value in variabs.items():
    				editedQuery = editedQuery.replace('{'+key +'}', "'" + value + "'", 1)
    		return editedQuery
    	except:
    		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
    		print('exception %s was thrown' % exceptionValue)
    		raise falcon.HTTPBadRequest('exception %s was thrown' % exceptionValue)
                  
class addRouteResource(object):

    def __init__(self, config, meta_dbconn, dbconn, app ):
        self.logger = logging.getLogger(__name__)
        self.config= config
        self.meta_dbconn = meta_dbconn
        self.dbconn = dbconn
        self.coreResource = coreResource
        self.app = app

    def on_post(self, req, resp):
        try:
            response = req.stream.read().decode("utf-8")
            stuff = json.loads(response)
            print(stuff['route'])
            cursor = self.meta_dbconn.cursor()
            resource = self.coreResource(self.config, self.meta_dbconn, self.dbconn, stuff['query'])
            self.app.add_route(stuff['route'], resource)
            cursor.execute("""INSERT INTO routes (route, query) VALUES (?, ?);""", (stuff['route'] ,stuff['query'] ))
            self.meta_dbconn.commit()
            resp.status = falcon.HTTP_201
            resp.body = fmt('Sucessfully added route!')
        except:
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            print('exception %s was thrown' % exceptionValue)
            raise falcon.HTTPBadRequest('exception %s was thrown' % exceptionValue)
        #resource = self.coreResouce(self.config, self.meta_dbconn, self.dbconn, doc['query'], list[2] )
        #app.add_route(doc['route', resource)

class addDataResource(object):

    def __init__(self, config, meta_dbconn, dbconn):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.meta_dbconn = meta_dbconn
        self.dbconn = dbconn
        self.coreResource = coreResource

    def on_post(self, req, resp):
        try:
            response = req.stream.read().decode("utf-8")
            stuff = json.loads(response)
            print(stuff['data'])
            cursor = self.dbconn.cursor()
            columns = '('
            values = '('
            for list in stuff['data']:
                columns = columns + '%s,' % list['column']
                if list['column'] == 'id':
                    values = values + "%s," % list['value']
                else:
                    values = values + "'%s'," % list['value']
            columns = columns[:-1] + ')'
            values = values[:-1] + ')'
            print(columns)
            print(values)
            cursor.execute("INSERT INTO "+ stuff['table'] +   columns  +" VALUES " + values )
            self.dbconn.commit()
            resp.status = falcon.HTTP_201
            resp.body = fmt('Sucessfully added data!')
        except:
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            print('exception %s was thrown' % exceptionValue)
            raise falcon.HTTPBadRequest('exception %s was thrown' % exceptionValue)


class addTableResource(object):
    def __init__(self, config, meta_dbconn, dbconn):
        self.logger = logging.getLogger(__name__)
        self.config= config
        self.meta_dbconn = meta_dbconn
        self.dbconn = dbconn
        self.coreResource = coreResource

    def on_post(self, req, resp):
        try:
            response = req.stream.read().decode("utf-8")
            stuff = json.loads(response)
            print(stuff['route'])
            cursor = self.dbconn.cursor()
            cursor.execute("Create Table ? ? " (stuff['name'], stuff['table_params']))
            self.dbconn.commit()
            resp.status = falcon.HTTP_201
            resp.body = fmt('Sucessfully added table!')
        except:
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            print('exception %s was thrown' % exceptionValue)
            raise falcon.HTTPBadRequest('exception %s was thrown' % exceptionValue)

class getAllRoutesResource(object):

    def __init__(self, config, meta_dbconn, dbconn):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.meta_dbconn = meta_dbconn
        self.dbconn = dbconn
        self.coreResource = coreResource

    def on_get(self, req, resp, **kwargs):
        variabs = kwargs
        result = {}
        result['data'] = self.get_routes()
        self.logger.debug('get routes')
        resp.set_header('Content-Type', 'application/json')
        resp.status = falcon.HTTP_200
        resp.body = fmt(result)

    def get_routes(self):
        try:
            cursor = self.meta_dbconn.cursor()
            cursor.execute("select * from routes")
            routes = cursor.fetchall()
            return routes
        except:
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            print('exception %s was thrown' % exceptionValue)
            raise falcon.HTTPBadRequest('exception %s was thrown' % exceptionValue)

class deleteRoutesResource(object):

    def __init__(self, config, meta_dbconn, dbconn):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.meta_dbconn = meta_dbconn
        self.dbconn = dbconn
        self.coreResource = coreResource

    def on_get(self, req, resp, id):
        self.id = id
        result = self.delete_route()
        self.logger.debug('Delete route by id')
        resp.set_header('Content-Type', 'application/json')
        resp.status = falcon.HTTP_200
        resp.body = fmt(result)

    def delete_route(self):
        try:
            cursor = self.meta_dbconn.cursor()
            cursor.execute("DELETE FROM routes where id = ?",  self.id)
            self.meta_dbconn.commit()
            return "Sucessfully deleted route!"
        except:
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            print('exception %s was thrown' % exceptionValue)
            return "Oops something went wrong. Maybe there isn't a route with that id"
            
