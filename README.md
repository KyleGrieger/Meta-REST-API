# Meta-REST-API

It's a Python 3 Falcon app that uses psycopg2 to connect to various PostgreSQL databases.

## Setup

This is a Python 3 (technically it runs with either right now) app so you'll probably want to run with a python3 virtualenv. You must have 2 postgres databases running one for the Meta API and one for app data.  Your config.yml file must also be set up appropriately. (see sampleConfig.yml) Create a table for routes in your Meta API db.

Use The Query (this is going to change as the meta-rest api grows):
	
	CREATE TABLE routes(id serial,route varchar(255),query varchar(255),type varchar(10)) 

This is the table that will store the routes that you add.

Start a virtual environment:

    virtualenv -p python3 ~/venv3
    source ~/venv3/bin/activate

If the above fails you need to make sure that python3 exists on your machine and that virtualenv is installed as well. 

Once in your virtualenv configure modules/dependencies with pip:

    pip install -r requirements.txt

## Running

It is recommended that you run the app from the virtualenv used during setup. 

With python:

    META_API_PORT=8080 python meta-api.py config.yml

With gunicorn:

    export META_API_PORT=8080 && gunicorn --workers=2 --log-level debug --log-file=- --bind 0.0.0.0:$META_API_PORT 'meta-api:build_app("config.yml")'

Once the API is running try this command:

    curl http://localhost:8080/allRoutes
You should get back some JSON:

    {
        data : []
    }

This means that you have not created any routes yet


## Routes

	GET /allRoutes

Lists all routes in your Rest API


    POST /addRoute

The form should look something like this

	{
		"route" : "/pokemon/type/{type}""
		"query" : "select * from pokemon where type = {type}"
	}

You should get a response:

"Successfully added route!"

This means that you have added the specified route to your api and the data returned will be what is returned from the query specified.

For example:
Now if you were to call

	GET /pokemon/type/water

You would get a response with data about all pokemon in your database with the type water

	POST /addData

The form should look something like this

	{
    "table" : "pokemon",
    "data": [{"column": "id",
            "value" : "6"},
            {"column": "name",
            "value" : "metapod"},
            {"column": "type",
            "value" : "grass"}]
	}

As you might've guessed this adds data to your app database in the table specified with the values specified

You should get a response:

"Sucessfully added data!"
