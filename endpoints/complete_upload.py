import logging
import traceback
import cherrypy
from database.database_accessor import DatabaseAccessor
from methods.asset_methods import (
    change_asset_upload_status, ChangeUploadStatusInvalidArgsException, AssetNotFoundException
)

logger = logging.getLogger('complete_upload')

@cherrypy.expose
@cherrypy.tools.json_out()
@cherrypy.tools.json_in()
class CompleteUploadAssetEndpoint:
    def PUT(self):
        json = cherrypy.request.json
        with DatabaseAccessor.get_connection() as c:
            try:
                with c.cursor() as cursor:
                    return change_asset_upload_status(json, cursor)
            except AssetNotFoundException as e:
                raise cherrypy.HTTPError(404, message=str(e))
            except ChangeUploadStatusInvalidArgsException as e:
                logger.error(traceback.format_exc())
                raise cherrypy.HTTPError(400, message=str(e))
