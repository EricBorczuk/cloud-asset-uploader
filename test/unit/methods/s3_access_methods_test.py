import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from freezegun import freeze_time
from methods.s3_access_methods import initiate_upload, UploadInvalidArgsException
from database.asset_dao import AssetDao, UploadedStatus, AssetRow
from external_services.s3_service import (
    S3Service, DEFAULT_BUCKET, DEFAULT_EXPIRATION, S3ClientMethod
)

class InitiateUploadUnitTest(unittest.TestCase):
    def setUp(self):
        self.mock_cursor = MagicMock()
        # Sample response from boto's generate_presigned_post
        self.sample_presigned_post = {
            'url': 'some sick URL', 
            'fields': {
                'key': 'ABCDE.txt',
                'AWSAccessKeyId': 'BLAHBLAHBLAHBLAH',
                'policy': 'HONESTY',
                'signature': 'asdfghjkl'
            }
        }

        self.asset_row_from_db = AssetRow(
            id=1,
            uploaded_status=UploadedStatus.PENDING.value,
            bucket=DEFAULT_BUCKET,
            object_key='important_secrets.txt',
            create_date=datetime.utcnow()
        )

    @patch.object(S3Service, 'create_signed_url')
    @patch.object(AssetDao, 'insert_one')
    @patch.object(AssetDao, 'get_by_bucket_and_key')
    def test_happy_path(self, bucket_key_mock, insert_one_mock, create_signed_url_mock):
        """
        Given:
            The object key and bucket don't already correspond to a row in the database
        Then:
            A new Asset row is inserted and an S3 signed URL is generated
        """
        bucket_key_mock.return_value = None
        create_signed_url_mock.return_value = self.sample_presigned_post

        upload_request = {
            'object_key': 'important_secrets.txt'
        }

        with freeze_time(datetime.utcnow()):
            row_to_be_inserted = AssetRow(
                id=None,
                uploaded_status=UploadedStatus.PENDING.value,
                bucket=DEFAULT_BUCKET,
                object_key='important_secrets.txt',
                create_date=datetime.utcnow()
            )

            insert_one_mock.return_value = self.asset_row_from_db

            result = initiate_upload(upload_request, self.mock_cursor)

        insert_one_mock.assert_called_once_with(
            row_to_be_inserted, self.mock_cursor
        )
        create_signed_url_mock.assert_called_once_with(
            S3ClientMethod.POST_OBJECT,
            'important_secrets.txt',
        )
        
        self.assertEqual(result, {
            'signed_info': self.sample_presigned_post,
            'asset_id': self.asset_row_from_db.id,
        })

    @patch.object(S3Service, 'create_signed_url')
    @patch.object(AssetDao, 'insert_one')
    @patch.object(AssetDao, 'get_by_bucket_and_key')   
    def test_happy_path_existing_asset(self, bucket_key_mock, insert_one_mock, create_signed_url_mock):
        """
        Given:
            The object key and bucket already correspond to a row in the database that is
            in the `pending` state
        Then:
            An S3 signed URL is generated, and no row is inserted
        """
        bucket_key_mock.return_value = self.asset_row_from_db
        create_signed_url_mock.return_value = self.sample_presigned_post

        upload_request = {
            'object_key': 'important_secrets.txt'
        }

        result = initiate_upload(upload_request, self.mock_cursor)

        insert_one_mock.assert_not_called()
        create_signed_url_mock.assert_called_once_with(
            S3ClientMethod.POST_OBJECT,
            'important_secrets.txt',
        )
        
        self.assertEqual(result, {
            'signed_info': self.sample_presigned_post,
            'asset_id': self.asset_row_from_db.id,
        })
    
    @patch.object(S3Service, 'create_signed_url')
    @patch.object(AssetDao, 'insert_one')
    @patch.object(AssetDao, 'get_by_bucket_and_key')
    def test_happy_path_with_expiration(self, bucket_key_mock, insert_one_mock, create_signed_url_mock):
        """
        Given:
            A request is made with an expiry time
        Then:
            An S3 signed URL is generated with the expiry time
        """
        bucket_key_mock.return_value = self.asset_row_from_db
        create_signed_url_mock.return_value = self.sample_presigned_post

        upload_request = {
            'object_key': 'important_secrets.txt',
            'expiration': 30 # seconds
        }

        result = initiate_upload(upload_request, self.mock_cursor)

        create_signed_url_mock.assert_called_once_with(
            S3ClientMethod.POST_OBJECT,
            'important_secrets.txt',
            expiration=30,
        )
        
        self.assertEqual(result, {
            'signed_info': self.sample_presigned_post,
            'asset_id': self.asset_row_from_db.id,
        })
    
    def test_invalid_request(self):
        """
        Given:
            The request is missing keys, or the values have invalid types
        Then:
            An applicable error is thrown
        """
        data = {}

        with self.assertRaises(UploadInvalidArgsException) as ctx:
            initiate_upload(data, self.mock_cursor)
        self.assertEqual(str(ctx.exception), 'Missing key: object_key')

        data = {
            'object_key': 1
        }

        with self.assertRaises(UploadInvalidArgsException) as ctx:
            initiate_upload(data, self.mock_cursor)
        self.assertEqual(str(ctx.exception), 'Invalid key: object_key, Value: 1 is not a string')

        data = {
            'object_key': 'sick_name.txt',
            'expiration': 'mamajama'
        }

        with self.assertRaises(UploadInvalidArgsException) as ctx:
            initiate_upload(data, self.mock_cursor)
        self.assertEqual(str(ctx.exception), 'Invalid key: expiration, Value: mamajama is not an int')
    
    @patch.object(AssetDao, 'get_by_bucket_and_key')
    def test_completed_asset_invalid(self, bucket_and_key_mock):
        """
        Given:
            The request uses a bucket and object_key for an asset that already exists
            in the database, and the asset has an uploaded_status of `complete`  
        Then:
            An applicable error is thrown
        """
        bucket_and_key_mock.return_value = AssetRow(
            id=1,
            uploaded_status=UploadedStatus.COMPLETE.value,
            bucket=DEFAULT_BUCKET,
            object_key='something',
            create_date=datetime.utcnow()
        )

        data = {
            'object_key': 'sick_name.txt',
        }

        with self.assertRaises(UploadInvalidArgsException) as ctx:
            initiate_upload(data, self.mock_cursor)
        self.assertEqual(str(ctx.exception), 'Upload already complete, try another object_key.')





        
