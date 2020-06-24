from enum import Enum
import boto3
from botocore.exceptions import ClientError


class S3ClientMethod(Enum):
    GET_OBJECT = 'get_object'
    POST_OBJECT = 'post_object'

class S3ServiceException(Exception):
    pass

class S3ServiceInvalidArgsException(Exception):
    pass

DEFAULT_EXPIRATION = 60 # 1 minute
MAX_EXPIRATION_TIME = 60 * 30 # 30 minutes
DEFAULT_BUCKET = 'ericborczuk'

class S3Service():
    s3_client = boto3.client('s3')

    @classmethod
    def create_signed_url(
        cls,
        s3_client_method,
        object_key,
        bucket_name=DEFAULT_BUCKET,
        expiration=DEFAULT_EXPIRATION
    ):
        """Create a signed URL to either get or put an S3 object.

        :param s3_client_method: S3ClientMethod
        :param object_key: The key used in S3 as the name of the asset.
        :param bucket_name: Bucket name in S3.
        :param expiration: Expiration time for the URL, in seconds.  Cannot be more than 30 mins.
        :return: signed URL.
        """ 
        if object_key is None:
            raise S3ServiceInvalidArgsException(
                f'Could not create a signed URL for {s3_client_method.value} request: '
                'object_key is required.'
            )
        
        if expiration > MAX_EXPIRATION_TIME:
            raise S3ServiceInvalidArgsException(
                f'Could not create a signed URL for {s3_client_method.value} request: '
                'expiration time was too long. Try a shorter duration.'
            )

        if isinstance(s3_client_method, S3ClientMethod):
            try:
                params = {
                    'Bucket': bucket_name,
                    'Key': object_key,
                }

                if s3_client_method == S3ClientMethod.POST_OBJECT:
                    return cls.s3_client.generate_presigned_post(
                        bucket_name,
                        object_key,
                        Fields={},
                        Conditions=[],
                        ExpiresIn=expiration
                    )

                return cls.s3_client.generate_presigned_url(
                    s3_client_method.value,
                    Params=params,
                    ExpiresIn=expiration
                )
            except ClientError as ce:
                raise S3ServiceException('Failed to generate signed URL', ce) 
        
        raise S3ServiceException(f'Unrecognized or unsupported S3 Method: {str(s3_client_method)}')
            
