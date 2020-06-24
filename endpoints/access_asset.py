import logging
import traceback
import cherrypy
from database.database_accessor import DatabaseAccessor
from methods.s3_access_methods import (
    initiate_access, AssetNotFoundException, AccessInvalidArgsException
)
from external_services.s3_service import S3ServiceException, S3ServiceInvalidArgsException

logger = logging.getLogger('access_asset')

@cherrypy.expose
@cherrypy.tools.json_out()
class AccessAssetEndpoint:
    def GET(self, asset_id=None, expires_in=None):
        with DatabaseAccessor.get_connection() as c:
            try:
                with c.cursor() as cursor:
                    return initiate_access({
                        'asset_id': asset_id,
                        'expires_in': expires_in,
                    }, cursor)
            except S3ServiceInvalidArgsException as s3e:
                logger.error(traceback.format_exc())
                raise cherrypy.HTTPError(400, message=str(s3e))
            except S3ServiceException as s3e:
                logger.error(traceback.format_exc())
                raise cherrypy.HTTPError(500, message=str(s3e))
            except AssetNotFoundException as e:
                raise cherrypy.HTTPError(404, message=str(e))
            except AccessInvalidArgsException as e:
                logger.error(traceback.format_exc())
                raise cherrypy.HTTPError(400, message=str(e))
