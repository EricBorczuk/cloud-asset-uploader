import cherrypy

class CloudAssetManagerServer:
    pass

@cherrypy.expose
class UploadAssetEndpoint:
    def POST(self):
        return b'{"we": "good"}'

@cherrypy.expose
class CompleteUploadAssetEndpoint:
    def PUT(self, asset_id):
        return b'{"we": "bad"}'

@cherrypy.expose
class AccessAssetEndpoint:
    def GET(self, asset_id):
        return f'{{"we": "{asset_id}"}}'.encode()

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