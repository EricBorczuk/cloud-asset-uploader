import cherrypy


@cherrypy.expose
class CompleteUploadAssetEndpoint:
    def PUT(self):
        return b'{"we": "bad"}'
