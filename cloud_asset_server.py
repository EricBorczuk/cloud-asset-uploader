import cherrypy
from database.database_accessor import DatabaseAccessor
from endpoints.upload_asset import UploadAssetEndpoint
from endpoints.update_status import UpdateAssetStatusEndpoint
from endpoints.access_asset import AccessAssetEndpoint

class CloudAssetManagerServer:
    pass

if __name__ == '__main__':
    conf = {
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
    service = CloudAssetManagerServer()
    DatabaseAccessor.connect()
    try:
        # Three endpoints, defined here:
        # /api/upload
        # /api/status
        # /api/access
        service.upload = UploadAssetEndpoint()
        service.status = UpdateAssetStatusEndpoint()
        service.access = AccessAssetEndpoint()
        cherrypy.quickstart(service, '/api', conf)
    finally:
        DatabaseAccessor.connection.close()
