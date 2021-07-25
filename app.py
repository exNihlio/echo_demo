#!/usr/bin/env python3

## Imports
import logging as log
import sys
from json import dumps

from os import environ as env

## Python3 does not include bottle in the stdlib
## so we want to fail gracefully and log it as such
## if we have not run pip install botttle
try:
    from bottle import route, default_app, request, response
except ImportError as e:
    log.fatal(e)
    sys.exit(1)

####################
## CONFIG OPTIONS ##
####################
## Opinion: When containerizing, env variables are preferable.

cow = """
^__^
(oo)\_______
(__)\       )\/\\
    ||----w |
    ||     ||
"""
#######################
## Application Logic ##
#######################
## Our API server
@route('/', method=['GET'])
def index():
    response.status = 200
    return cow

@route('/api/echo', method=['POST', 'PUT'])
def index():
    ## Return 415, because this must have a Content-Type of application/json
    if request.content_type != "application/json":
        response.status = 415
        response.content_type = "application/json"
        return dumps({"error": "Content-Type must be application/json",
                      "http_error_code": response.status})

    if request.method not in ['POST', 'PUT']:
        response.status = 405

    ## Validate that we have valid JSON
    try:
        json_post = request.json
    except:
        response.status = 400
        response.content_type = "application/json"
        return dumps({"error": "Invalid JSON",
                      "http_error_code": response.status})

    try:
        if json_post['echoed'] == True:
            ## Return 400 for Bad Request, as this has already been echoed.
            response.status = 400
            response.content_type = "application/json"
            return dumps({"error": "this has been echoed",
                          "http_error_code": response.status})
    except:
        pass

    ## Return our JSON body with appended value
    json_post['echoed'] = True
    response.status = 200
    response.content_type = "application/json"
    return json_post
    
app = default_app()