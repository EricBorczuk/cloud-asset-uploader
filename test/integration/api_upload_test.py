import unittest
import json
from datetime import datetime
from database.asset_dao import AssetDao, AssetRow, UploadedStatus
from external_services.s3_service import DEFAULT_BUCKET
from .base_integration_test import BaseIntegrationTest
from .test_utils import run_server

class ApiUploadIntegrationTest(BaseIntegrationTest):
    def setUp(self):
        super().setUp()
        self.post_object_url_response = {
            'url': 'yay://a.url.com', 
            'fields': {
                'key': 'ABCDE.txt',
                'AWSAccessKeyId': 'BLAHBLAHBLAHBLAH',
                'policy': 'HONESTY',
                'signature': 'asdfghjkl'
            }
        }
        self.s3_client_mock.generate_presigned_post.return_value = self.post_object_url_response

    def test_upload_writes_asset_properly(self):
        with run_server():
            response = self.request(
                'post',
                '/upload',
                data=json.dumps({ 'object_key': 'abc' }),
            )

            dict_data = json.loads(response.content)

            with self.connection.cursor() as cur:
                asset_row = AssetDao.get_by_bucket_and_key(DEFAULT_BUCKET, 'abc', cur)

            self.assertEqual(dict_data, {
                'signed_info': self.post_object_url_response,
                'asset_id': asset_row.id,
            })

            self.assertEqual(asset_row.uploaded_status, UploadedStatus.PENDING.value)
    
    def test_upload_using_existing_pending_asset(self):
        pending_asset_row = AssetRow(
            id=None,
            uploaded_status=UploadedStatus.PENDING.value,
            bucket=DEFAULT_BUCKET,
            object_key='abc',
            create_date=datetime.now(),
        )
        with self.connection.cursor() as cur:
            pending_asset_row = AssetDao.insert_one(pending_asset_row, cur)
        
        with run_server():
            response = self.request(
                'post',
                '/upload',
                data=json.dumps({ 'object_key': 'abc', 'expires_in': 50 }),
            )

            dict_data = json.loads(response.content)

            self.assertEqual(dict_data, {
                'signed_info': self.post_object_url_response,
                'asset_id': pending_asset_row.id,
            })

            self.assertEqual(pending_asset_row.uploaded_status, UploadedStatus.PENDING.value)
    
    def test_upload_existing_completed_asset_fails(self):
        completed_asset_row = AssetRow(
            id=None,
            uploaded_status=UploadedStatus.COMPLETE.value,
            bucket=DEFAULT_BUCKET,
            object_key='abc',
            create_date=datetime.now(),
        )
        with self.connection.cursor() as cur:
            AssetDao.insert_one(completed_asset_row, cur)

        with run_server():
            response = self.request(
                'post',
                '/upload',
                data=json.dumps({ 'object_key': 'abc' }),
            )

            self.assertEqual(response.status_code, 400)
            self.assertTrue('Upload already complete, try another object_key.' in response.content.decode())
