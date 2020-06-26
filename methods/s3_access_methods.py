from datetime import datetime
from external_services.s3_service import (
    S3Service,
    S3ClientMethod,
    S3ServiceException,
    S3ServiceInvalidArgsException,
    DEFAULT_BUCKET
)
from database.asset_dao import AssetDao, AssetRow, UploadedStatus

"""
"Public" functions that live here essentially map to endpoints 1:1.
"""

class UploadInvalidArgsException(Exception):
    pass

def _check_valid_upload_request(upload_request):
    object_key = upload_request.get('object_key', None)
    expiration = upload_request.get('expires_in', None)

    if object_key is None:
        raise UploadInvalidArgsException('Missing key: object_key')
    if not isinstance(object_key, str):
        raise UploadInvalidArgsException(f'Invalid key: object_key, Value: {object_key} is not a string')
    if expiration is not None and not isinstance(expiration, int):
        raise UploadInvalidArgsException(f'Invalid key: expires_in, Value: {expiration} is not an int')

# resolving function for /api/upload
def initiate_upload(upload_request, cursor):
    """
    Creates a signed URL for a put_object operation.
    Should the URL signing succeed, a row is also written to the `assets`
    table. Should it not, the exception is exposed to the user and no
    information is persisted.

    If the combination of bucket and key already exist in the database, an error
    is raised and no action is taken.

    :param upload_request: a dict with keys `object_key` and `expires_in`, denoting
    the asset's name and the amount of time, in seconds, that the signed URL should last.
    """

    _check_valid_upload_request(upload_request)
    object_key = upload_request['object_key']
    expiration = upload_request.get('expires_in')

    asset = AssetDao.get_by_bucket_and_key(
        DEFAULT_BUCKET,
        object_key,
        cursor,
    )

    if not asset:
        new_asset = AssetRow(
            id=None,
            uploaded_status=UploadedStatus.PENDING.value,
            bucket=DEFAULT_BUCKET,
            object_key=object_key,
            create_date=datetime.utcnow(),
        )
        asset = AssetDao.insert_one(new_asset, cursor)
    elif asset.uploaded_status == UploadedStatus.COMPLETE.value:
        raise UploadInvalidArgsException('Upload already complete, try another object_key.')

    if expiration:
        return {
            'signed_info': S3Service.create_signed_url(
                       S3ClientMethod.POST_OBJECT,
                       upload_request['object_key'],
                       expiration=expiration,
                   ),
            'asset_id': asset.id,
        }

    return {
        'signed_info': S3Service.create_signed_url(
                   S3ClientMethod.POST_OBJECT,
                   upload_request['object_key'],
               ),
        'asset_id': asset.id,
    }

class AccessInvalidArgsException(Exception):
    pass

class AssetNotFoundException(Exception):
    pass

def _check_valid_access_request(access_request):
    asset_id = access_request.get('asset_id', None)
    expiration = access_request.get('expires_in', None)

    if asset_id is None:
        raise AccessInvalidArgsException('Missing key: asset_id')
    try:
        int(asset_id)
    except ValueError:
        raise AccessInvalidArgsException(f'Invalid key: asset_id, Value: {asset_id} is not an int')

    if expiration is not None:
        try:
            int(expiration)
        except ValueError:
            raise AccessInvalidArgsException(f'Invalid key: expires_in, Value: {expiration} is not an int')

# resolving function for /api/access
def initiate_access(access_request, cursor):
    """
    Creates a signed URL for a get_object operation.
    The signed URL can only be created for the asset if its uploaded_status
    is `completed`.

    :param access_request: a dict with keys `asset_id` and `expires_in`, denoting
    the asset's name and the amount of time, in seconds, that the signed URL should last.
    """
    _check_valid_access_request(access_request)
    asset_id = int(access_request['asset_id'])
    expiration = access_request.get('expires_in')
    asset = AssetDao.get_by_id(asset_id, cursor)
    if not asset:
        raise AssetNotFoundException(f'Asset with id {asset_id} not found')

    if asset.uploaded_status != UploadedStatus.COMPLETE.value:
        raise AccessInvalidArgsException('Asset upload is not yet completed.')
    
    if expiration:
        return {
            'url': S3Service.create_signed_url(
                               S3ClientMethod.GET_OBJECT,
                               asset.object_key,
                               bucket_name=asset.bucket,
                               expiration=int(expiration),
                           ),
            'asset_id': asset.id,
        }

    return {
        'url': S3Service.create_signed_url(
                   S3ClientMethod.GET_OBJECT,
                   asset.object_key,
                   bucket_name=asset.bucket,
               ),
        'asset_id': asset.id,
    }



