import cherrypy


@cherrypy.expose
class CompleteUploadAssetEndpoint:
    def PUT(self, asset_id):
        return b'{"we": "bad"}'
