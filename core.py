import sys
import psycopg2
import psycopg2.extras
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
    		dbconn = self.dbconn.getconn()
    		cursor = dbconn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    		if len(variabs) > 0:
    			cursor.execute(self.get_vars(variabs))
    		elif len(variabs) == 0:
    			cursor.execute(self.query)
    		dbconn.commit()
    		queryResult = cursor.fetchall()
    		return queryResult
    	except:
    		return queryResult
    	finally:
    		self.dbconn.putconn(dbconn)

    def get_vars(self, variabs):
    	try:
    		dbconn = self.dbconn.getconn()
    		cursor = dbconn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    		editedQuery = self.query
    		if len(variabs.values()) > 0:
    			for key, value in variabs.items():
    				editedQuery = editedQuery.replace('{'+key +'}', "'" + value + "'", 1)
    		return editedQuery
    	finally:
    		self.dbconn.putconn(dbconn)

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
            meta_dbconn = self.meta_dbconn.getconn()
            cursor = meta_dbconn.cursor()
            resource = self.coreResource(self.config, self.meta_dbconn, self.dbconn, stuff['query'])
            self.app.add_route(stuff['route'], resource)
            cursor.execute("""INSERT INTO routes (route, query) VALUES (%s, %s);""", (stuff['route'] ,stuff['query'] ))
            meta_dbconn.commit()
            resp.status = falcon.HTTP_201
            resp.body = fmt('Sucessfully added route!')
        except:
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            print('exception %s was thrown' % exceptionValue)
            raise falcon.HTTPBadRequest('Missing thing','A thing must be submitted in the request body.')
        #resource = self.coreResouce(self.config, self.meta_dbconn, self.dbconn, doc['query'], list[2] )
        #app.add_route(doc['route', resource)

class addDataResource(object):

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
            print(stuff['data'])
            dbconn = self.dbconn.getconn()
            cursor = dbconn.cursor()
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
            dbconn.commit()
            resp.status = falcon.HTTP_201
            resp.body = fmt('Sucessfully added data!')
        except:
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            print('exception %s was thrown' % exceptionValue)
            raise falcon.HTTPBadRequest('exception %s was thrown' % exceptionValue)
        finally:
            self.dbconn.putconn(dbconn)


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
            dbconn = self.dbconn.getconn()
            cursor = dbconn.cursor()
            cursor.execute("Create Table %s %s " (stuff['name'], stuff['table_params']))
            dbconn.commit()
            resp.status = falcon.HTTP_201
            resp.body = fmt('Sucessfully added table!')
        except:
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            print('exception %s was thrown' % exceptionValue)
            raise falcon.HTTPBadRequest('exception %s was thrown' % exceptionValue)
        finally:
            self.dbconn.putconn(dbconn)

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
            meta_dbconn = self.meta_dbconn.getconn()
            cursor = meta_dbconn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
            cursor.execute("select * from routes")
            routes = cursor.fetchall()
            print(routes)
            return routes
        finally:
            self.meta_dbconn.putconn(meta_dbconn)
