import cherrypy

from endpoints.upload_asset import UploadAssetEndpoint
from endpoints.complete_upload import CompleteUploadAssetEndpoint
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
        '/complete': {
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

    # Three endpoints, defined here:
    # /api/upload
    # /api/complete
    # /api/access
    service.upload = UploadAssetEndpoint()
    service.complete = CompleteUploadAssetEndpoint()
    service.access = AccessAssetEndpoint()
    
    cherrypy.quickstart(service, '/api', conf)