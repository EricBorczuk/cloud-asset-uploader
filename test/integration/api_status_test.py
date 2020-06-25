import unittest
import json
from datetime import datetime
from database.asset_dao import AssetDao, AssetRow, UploadedStatus
from external_services.s3_service import DEFAULT_BUCKET
from .base_integration_test import BaseIntegrationTest
from .test_utils import run_server

class ApiUploadIntegrationTest(BaseIntegrationTest):
    def test_updates_status_complete(self):
        existing_asset_row = AssetRow(
            id=None,
            uploaded_status=UploadedStatus.PENDING.value,
            bucket=DEFAULT_BUCKET,
            object_key='abc',
            create_date=datetime.now()
        )
        with self.connection.cursor() as cur:
            existing_asset_row = AssetDao.insert_one(existing_asset_row, cur)
        
        with run_server():
            response = self.request(
                'put',
                '/status',
                data=json.dumps({
                    'asset_id': existing_asset_row.id,
                    'uploaded_status': UploadedStatus.COMPLETE.value
                })
            )

            self.assertEqual(response.status_code, 200)
            response_body = json.loads(response.content)

            with self.connection.cursor() as cur:
                updated_asset_row = AssetDao.get_by_id(existing_asset_row.id, cur)

            self.assertEqual(updated_asset_row.uploaded_status, UploadedStatus.COMPLETE.value)

            self.assertEqual(response_body, {
                'success': True,
                'uploaded_status': UploadedStatus.COMPLETE.value,
            })
    
    def test_update_status_fails_invalid_asset(self):
        with run_server():
            response = self.request(
                'put',
                '/status',
                data=json.dumps({
                    'asset_id': 1337,
                    'uploaded_status': UploadedStatus.COMPLETE.value
                })
            )

            self.assertEqual(response.status_code, 404)
            self.assertTrue('Asset with id 1337 not found' in response.content.decode())

    # This test simply documents that it's not explicitly disallowed to un-complete
    # a completed upload, you can set the asset back to pending currently.
    # In a future world we might want to make completing a one-way state change, which
    # would mean deleting this test.
    def test_updates_status_pending(self):
        existing_asset_row = AssetRow(
            id=None,
            uploaded_status=UploadedStatus.COMPLETE.value,
            bucket=DEFAULT_BUCKET,
            object_key='abc',
            create_date=datetime.now()
        )
        with self.connection.cursor() as cur:
            existing_asset_row = AssetDao.insert_one(existing_asset_row, cur)
        
        with run_server():
            response = self.request(
                'put',
                '/status',
                data=json.dumps({
                    'asset_id': existing_asset_row.id,
                    'uploaded_status': UploadedStatus.PENDING.value
                })
            )

            self.assertEqual(response.status_code, 200)
            response_body = json.loads(response.content)

            with self.connection.cursor() as cur:
                updated_asset_row = AssetDao.get_by_id(existing_asset_row.id, cur)

            self.assertEqual(updated_asset_row.uploaded_status, UploadedStatus.PENDING.value)

            self.assertEqual(response_body, {
                'success': True,
                'uploaded_status': UploadedStatus.PENDING.value,
            })