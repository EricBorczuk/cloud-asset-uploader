import cherrypy
import argparse
from unittest.mock import patch
from external_services.s3_service import S3Service
from database.database_accessor import DatabaseAccessor
from endpoints.upload_asset import UploadAssetEndpoint
from endpoints.update_status import UpdateAssetStatusEndpoint
from endpoints.access_asset import AccessAssetEndpoint

class CloudAssetManagerServer:
    pass

CHERRY_TREE_CONFIG = {
    '/upload': {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
        'tools.response_headers.on': True,
        'tools.response_headers.headers': [('Content-Type', 'application/json')],
    },
    '/status': {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
        'tools.response_headers.on': True,
        'tools.response_headers.headers': [('Content-Type', 'application/json')],
    },
    '/access': {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
        'tools.response_headers.on': True,
        'tools.response_headers.headers': [('Content-Type', 'application/json')],
    }
}

def setup_cherry_tree(port=8080):
    # Don't show traceback as HTML to the client on error
    # Run as if we're in production (so no 'debug' mode)
    cherrypy.config.update({
        'server.socket_port': port,
        'environment': 'production',
        'log.screen': False,
        'show_tracebacks': False,
    })
    service = CloudAssetManagerServer()
    service.upload = UploadAssetEndpoint()
    service.status = UpdateAssetStatusEndpoint()
    service.access = AccessAssetEndpoint()
    return service

def startup_server():
    DatabaseAccessor.connect()
    try:
        # Three endpoints, defined here:
        # /api/upload
        # /api/status
        # /api/access
        service = setup_cherry_tree()
        print('Server running on port 8080')
        cherrypy.quickstart(service, '/api', CHERRY_TREE_CONFIG)
    finally:
        DatabaseAccessor.connection.close()

if __name__ == '__main__':
    startup_server()
