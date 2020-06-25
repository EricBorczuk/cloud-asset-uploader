import unittest
from unittest.mock import patch
from botocore.exceptions import ClientError
from external_services.s3_service import (
    S3Service, S3ClientMethod, DEFAULT_BUCKET, DEFAULT_EXPIRATION,
    S3ServiceInvalidArgsException, S3ServiceException
)

class CreateSignedUrlUnitTest(unittest.TestCase):
    def setUp(self):
        self.get_object_url_response = 'yay://a.url.com'
        self.post_object_url_response = {
            'url': 'yay://a.url.com', 
            'fields': {
                'key': 'ABCDE.txt',
                'AWSAccessKeyId': 'BLAHBLAHBLAHBLAH',
                'policy': 'HONESTY',
                'signature': 'asdfghjkl'
            }
        }

    @patch.object(S3Service, 's3_client')
    def test_happy_path_get_object(self, mock_client):
        """
        Given:
            A valid request to create_signed_url, using all default parameters and a get_object
            request
        Then:
            The applicable S3 service should be called, and a signed URL is returned
        """
        mock_client.generate_presigned_url.return_value = self.get_object_url_response

        signed_url = S3Service.create_signed_url(
            S3ClientMethod.GET_OBJECT,
            'some_key'
        )

        mock_client.generate_presigned_url.assert_called_once_with(
            S3ClientMethod.GET_OBJECT.value,
            Params={
                'Bucket': DEFAULT_BUCKET,
                'Key': 'some_key',
            },
            ExpiresIn=DEFAULT_EXPIRATION,
        )
    
    @patch.object(S3Service, 's3_client')
    def test_happy_path_post_object(self, mock_client):
        """
        Given:
            A valid request to create_signed_url, using all default parameters and a get_object
            request
        Then:
            The applicable S3 service should be called, and a signed URL is returned
        """
        mock_client.generate_presigned_post.return_value = self.post_object_url_response

        signed_url = S3Service.create_signed_url(
            S3ClientMethod.POST_OBJECT,
            'some_key'
        )

        mock_client.generate_presigned_post.assert_called_once_with(
            DEFAULT_BUCKET,
            'some_key',
            Fields={},
            Conditions=[],
            ExpiresIn=DEFAULT_EXPIRATION,
        )

    @patch.object(S3Service, 's3_client')
    def test_happy_path_with_provided_bucket(self, mock_client):
        """
        Given:
            A valid request to create_signed_url, using all default parameters except for `bucket_name`
        Then:
            The applicable S3 service should be called with that `bucket_name`, and a signed URL is returned
        """
        mock_client.generate_presigned_post.return_value = self.post_object_url_response
        mock_client.generate_presigned_url.return_value = self.get_object_url_response

        signed_url = S3Service.create_signed_url(
            S3ClientMethod.POST_OBJECT,
            'some_key',
            bucket_name='my_cool_bucket'
        )

        mock_client.generate_presigned_post.assert_called_once_with(
            'my_cool_bucket',
            'some_key',
            Fields={},
            Conditions=[],
            ExpiresIn=DEFAULT_EXPIRATION,
        )

        signed_url = S3Service.create_signed_url(
            S3ClientMethod.GET_OBJECT,
            'some_key',
            bucket_name='my_cool_bucket'
        )

        mock_client.generate_presigned_url.assert_called_once_with(
            S3ClientMethod.GET_OBJECT.value,
            Params={
                'Bucket': 'my_cool_bucket',
                'Key': 'some_key',
            },
            ExpiresIn=DEFAULT_EXPIRATION,
        )
    
    @patch.object(S3Service, 's3_client')
    def test_happy_path_with_provided_expiration(self, mock_client):
        """
        Given:
            A valid request to create_signed_url, using all default parameters except for a valid `expiration`
        Then:
            The applicable S3 service should be called with that `expiration`, and a signed URL is returned
        """
        mock_client.generate_presigned_post.return_value = self.post_object_url_response
        mock_client.generate_presigned_url.return_value = self.get_object_url_response

        signed_url = S3Service.create_signed_url(
            S3ClientMethod.POST_OBJECT,
            'some_key',
            expiration=1800 # This is the fencepost acceptable threshold (30 min)
        )

        mock_client.generate_presigned_post.assert_called_once_with(
            DEFAULT_BUCKET,
            'some_key',
            Fields={},
            Conditions=[],
            ExpiresIn=1800,
        )

        signed_url = S3Service.create_signed_url(
            S3ClientMethod.GET_OBJECT,
            'some_key',
            expiration=1800
        )

        mock_client.generate_presigned_url.assert_called_once_with(
            S3ClientMethod.GET_OBJECT.value,
            Params={
                'Bucket': DEFAULT_BUCKET,
                'Key': 'some_key',
            },
            ExpiresIn=1800,
        )

    def test_invalid_parameters(self):
        """
        Given:
            Parameters are provided that are not valid, or are missing when required
        Then:
            An applicable error is raised
        """

        with self.assertRaises(S3ServiceInvalidArgsException) as ctx:
            S3Service.create_signed_url(
                S3ClientMethod.POST_OBJECT,
                None
            )
        self.assertEqual(str(ctx.exception),
            'Could not create a signed URL for post_object request: '
            'object_key is required.'
        )

        with self.assertRaises(S3ServiceInvalidArgsException) as ctx:
            S3Service.create_signed_url(
                S3ClientMethod.POST_OBJECT,
                'some_valid_key',
                expiration=999999999999,
            )
        self.assertEqual(str(ctx.exception),
            'Could not create a signed URL for post_object request: '
            'expiration time was too long. Try a shorter duration.'
        )

        with self.assertRaises(S3ServiceInvalidArgsException) as ctx:
            S3Service.create_signed_url(
                'some_strange_invalid_method',
                'some_valid_key',
            )
        self.assertEqual(str(ctx.exception),
            'Unrecognized or unsupported S3 Method: some_strange_invalid_method'
        )
    
    @patch.object(S3Service, 's3_client')
    def test_s3_failure_raises_our_exception(self, mock_client):
        """
        Given:
            The S3 Service's external call throws a ClientError
        Then:
            An applicable S3ServiceException is raised
        """
        client_error = ClientError(
            { 
                'Error': {
                    'Message': 'Why did you do that??'
                }
            },
            'put_object'
        )
        mock_client.generate_presigned_url.side_effect = client_error

        with self.assertRaises(S3ServiceException) as ctx:
            signed_url = S3Service.create_signed_url(
                S3ClientMethod.GET_OBJECT,
                'some_key'
            )
        self.assertEqual(
            ctx.exception.args,
            ('Failed to generate signed URL', client_error)
        )



    

