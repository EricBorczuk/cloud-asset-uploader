from database.asset_dao import UploadedStatus, AssetDao

class ChangeUploadStatusInvalidArgsException(Exception):
    pass

class NotFoundException(Exception):
    pass

def _check_valid_change_upload_status_request(request):
    asset_id = request.get('asset_id', None)
    uploaded_status = request.get('uploaded_status', None)

    if asset_id is None:
        raise ChangeUploadStatusInvalidArgsException('Missing key: asset_id')
    if uploaded_status is None:
        raise ChangeUploadStatusInvalidArgsException('Missing key: uploaded_status')
    if not isinstance(asset_id, int):
        raise ChangeUploadStatusInvalidArgsException(f'Invalid key: asset_id, Value: {asset_id} is not an int')
    
    try:
        UploadedStatus(uploaded_status)
    except ValueError:
        raise ChangeUploadStatusInvalidArgsException(
            f'Invalid key: uploaded_status, Value: {uploaded_status} is not one of {[s.value for s in UploadedStatus]}')
    

def change_asset_upload_status(request, cursor):
    """
    Updates a requested asset to have a new status.

    :param request: a dict with keys `asset_id` and `uploaded_status`, denoting
    the asset's id and the new upload status.
    """
    _check_valid_change_upload_status_request(request)
    asset = AssetDao.get_by_id(request['asset_id'], cursor)

    if not asset:
        raise NotFoundException(f'Asset with id {request["asset_id"]} not found')
    
    AssetDao.update_uploaded_status(request['asset_id'], request['uploaded_status'], cursor)

    return {
        'success': True,
        'uploaded_status': request['uploaded_status'],
    }
