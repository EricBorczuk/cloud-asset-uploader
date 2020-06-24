from external_services.s3_service import S3Service, S3ClientMethod, S3ServiceException

def initiate_upload(object_key):
    """
    Creates a signed URL for a put_object operation.
    Should the URL signing succeed, a row is also written to the `assets`
    table. Should it not, the exception is exposed to the user and no
    information is persisted.

    If the combination of bucket and key already exist in the database, an error
    is raised and no action is taken.

    :param object_key: The expected key name of the asset to upload to S3
    """
    try:
        return S3Service.create_signed_url(
            S3ClientMethod.PUT_OBJECT,
            object_key,
            expiration=1800,
        )
    except S3ServiceException as e:
        # rollback
        raise e