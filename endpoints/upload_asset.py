import logging
import traceback
import cherrypy
from external_services.s3_service import S3ServiceException, S3ServiceInvalidArgsException
from methods.s3_access_methods import initiate_upload, UploadInvalidArgsException

logger = logging.getLogger('upload_asset')

@cherrypy.expose
@cherrypy.tools.json_out()
@cherrypy.tools.json_in()
class UploadAssetEndpoint:
    def POST(self):
        json = cherrypy.request.json

        try:
            signed_url = initiate_upload(json)
            return {
                'url': signed_url,
            }
        except UploadInvalidArgsException as ue:
            logger.error(traceback.format_exc())
            raise cherrypy.HTTPError(400, message=str(ue))
        except S3ServiceInvalidArgsException as s3e:
            logger.error(traceback.format_exc())
            raise cherrypy.HTTPError(400, message=str(s3e))
        except S3ServiceException as s3e:
            logger.error(traceback.format_exc())
            raise cherrypy.HTTPError(500, message=str(s3e))
