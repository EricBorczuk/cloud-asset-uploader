import cherrypy
from external_services.s3_service import (
    S3Service, S3ServiceException, S3ClientMethod
)

@cherrypy.expose
class AccessAssetEndpoint:
    def GET(self, asset_id):
        try:
            return S3Service.create_signed_url(
                S3ClientMethod.GET_OBJECT,
                object_key=asset_id,
            ).encode()
        except S3ServiceException as s3e:
            return cherrypy.HTTPError(500, message=str(s3e))
