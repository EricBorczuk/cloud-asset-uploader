import logging
import traceback
import json
import cherrypy
from external_services.s3_service import S3ServiceException, S3ServiceInvalidArgsException
from methods.s3_access_methods import initiate_upload

logger = logging.getLogger('upload_asset')

@cherrypy.expose
class UploadAssetEndpoint:
    def POST(self, object_key):
        try:
            signed_url = initiate_upload(object_key)
            return json.dumps({
                'url': signed_url,
            }).encode()
        except S3ServiceInvalidArgsException as s3e:
            logger.error(traceback.format_exc())
            raise cherrypy.HTTPError(400, message=str(s3e))
        except S3ServiceException as s3e:
            logger.error(traceback.format_exc())
            raise cherrypy.HTTPError(500, message=str(s3e))
