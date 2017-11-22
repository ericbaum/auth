'''
 This file purpose is to configure Flask with Alchemy
 Also, some generic HTTP formatter functions are provided
 There is also a generic exception class for HTTP errors
 This code should be kept independent of the other modules
 so it can be reused in any Flask + Alchemy project
'''

from flask import Flask
from flask import make_response as fmake_response
import json
from flask_sqlalchemy import SQLAlchemy
from logging.handlers import SysLogHandler
import logging
import conf as dbconf


# Make the initial flask + alchem configuration
app = Flask(__name__)
app.url_map.strict_slashes = False

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')


# create a logger for our application
if dbconf.logMode == 'STDOUT':
    streamLogger = logging.StreamHandler()
    streamLogger.setFormatter(formatter)
    app.logger.addHandler(streamLogger)

elif dbconf.logMode == 'SYSLOG':
    sysLogHandler = SysLogHandler('/dev/log')
    sysLogHandler.setFormatter(formatter)
    app.logger.addHandler(sysLogHandler)

else:
    print('Unknow log mode' + dbconf.logMode + '. Aborting')
    exit(-1)

app.logger.setLevel(logging.DEBUG)

# Select database driver
if (dbconf.dbName == 'postgres'):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres+pypostgresql://' + \
                dbconf.dbUser + ':' + dbconf.dbPdw + '@' + dbconf.dbHost

else:
    LOGGER.error("Currently, there is no suport for database " + dbconf.dbName)
    exit(-1)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class HTTPRequestError(Exception):
    def __init__(self, errorCode, message):
        self.message = message
        self.errorCode = errorCode


# Utility function for HTTP responses
def make_response(payload, status):
    resp = fmake_response(payload, status)
    resp.headers['content-type'] = 'application/json'
    return resp


def formatResponse(status, message=None):
    payload = None
    if message:
        payload = json.dumps({'message': message, 'status': status})
    elif status >= 200 and status < 300:
        payload = json.dumps({'message': 'ok', 'status': status})
    else:
        payload = json.dumps({'message': 'Request failed', 'status': status})
    return make_response(payload, status)


def loadJsonFromRequest(request):
    if request.mimetype != 'application/json':
        raise HTTPRequestError(400, 'invalid mimetype')

    return request.get_json()


# with this function the logger type is transparent for the application
def log():
    return app.logger
