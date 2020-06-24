from external_services.s3_service import (
    S3Service, S3ClientMethod, S3ServiceException, S3ServiceInvalidArgsException
)

"""
Here lies all actions that our endpoints carry out.
Functions that live here essentially map to endpoints 1:1.
"""

class UploadInvalidArgsException(Exception):
    pass

def _check_valid_upload_request(upload_request):
    object_key = upload_request.get('object_key', None)
    expiration = upload_request.get('expiration', None)

    if object_key is None:
        raise UploadInvalidArgsException('Missing key: object_key')
    if expiration is None:
        raise UploadInvalidArgsException('Missing key: expiration')
    if not isinstance(object_key, str):
        raise UploadInvalidArgsException(f'Invalid key: object_key, Value: {object_key} is not a string')
    if not isinstance(expiration, int):
        raise UploadInvalidArgsException(f'Invalid key: expiration, Value: {object_key} is not an int')

def initiate_upload(upload_request):
    """
    Creates a signed URL for a put_object operation.
    Should the URL signing succeed, a row is also written to the `assets`
    table. Should it not, the exception is exposed to the user and no
    information is persisted.

    If the combination of bucket and key already exist in the database, an error
    is raised and no action is taken.

    :param upload_request: a dict with keys `object_key` and `expiration`, denoting
    the asset's name and the expiration time of the signed URL.
    """
    _check_valid_upload_request(upload_request)
    try:
        return S3Service.create_signed_url(
            S3ClientMethod.PUT_OBJECT,
            upload_request['object_key'],
            expiration=upload_request['expiration']
        )
    except (S3ServiceException, S3ServiceInvalidArgsException) as e:
        # rollback
        raise e
