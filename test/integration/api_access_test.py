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
        self.get_object_url_response = 'yay://a.url.com'
        self.s3_client_mock.generate_presigned_url.return_value = self.get_object_url_response

    def test_access_request_completed_asset(self):
        completed_asset_row = AssetRow(
            id=None,
            uploaded_status=UploadedStatus.COMPLETE.value,
            bucket=DEFAULT_BUCKET,
            object_key='abc',
            create_date=datetime.now(),
        )
        with self.connection.cursor() as cur:
            completed_asset_row = AssetDao.insert_one(completed_asset_row, cur)

        with run_server():
            response = self.request(
                'get',
                f'/access?asset_id={completed_asset_row.id}',
            )

            dict_data = json.loads(response.content)

            self.assertEqual(dict_data, {
                'url': self.get_object_url_response,
                'asset_id': completed_asset_row.id
            })
    
    def test_access_request_incomplete_asset_disallowed(self):
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
                'get',
                f'/access?asset_id={pending_asset_row.id}',
            )

            self.assertEqual(response.status_code, 400)
            self.assertTrue(
                'Asset upload is not yet completed.' in response.content.decode()
            )
