import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from methods.asset_methods import (
    change_asset_upload_status, ChangeUploadStatusInvalidArgsException, AssetNotFoundException
)
from database.asset_dao import AssetDao, UploadedStatus, AssetRow

class ChangeAssetUploadStatusUnitTest(unittest.TestCase):
    def setUp(self):
        self.mock_cursor = MagicMock()

    @patch.object(AssetDao, 'update_uploaded_status')
    @patch.object(AssetDao, 'get_by_id')
    def test_happy_path(self, get_by_id_mock, update_uploaded_status_mock):
        json = {
            'asset_id': 1,
            'uploaded_status': UploadedStatus.COMPLETE.value
        }

        get_by_id_mock.return_value = AssetRow(
            id=1,
            uploaded_status=UploadedStatus.PENDING.value,
            bucket='',
            object_key='',
            create_date=datetime.utcnow()
        )

        result = change_asset_upload_status(json, self.mock_cursor)
        get_by_id_mock.assert_called_once_with(
            1, self.mock_cursor
        )
        update_uploaded_status_mock.assert_called_once_with(
            1, UploadedStatus.COMPLETE.value, self.mock_cursor
        )

        self.assertEqual(result, {
            'success': True,
            'uploaded_status': UploadedStatus.COMPLETE.value,
        })
    
    def test_invalid_request(self):
        json = {
            'uploaded_status': UploadedStatus.COMPLETE.value,
        }

        with self.assertRaises(ChangeUploadStatusInvalidArgsException) as ctx:
            change_asset_upload_status(json, self.mock_cursor)
        self.assertEqual(str(ctx.exception), 'Missing key: asset_id')

        json = {
            'asset_id': 1,
        }

        with self.assertRaises(ChangeUploadStatusInvalidArgsException) as ctx:
            change_asset_upload_status(json, self.mock_cursor)
        self.assertEqual(str(ctx.exception), 'Missing key: uploaded_status')

        json = {
            'asset_id': 'some string?',
            'uploaded_status': UploadedStatus.COMPLETE.value,
        }

        with self.assertRaises(ChangeUploadStatusInvalidArgsException) as ctx:
            change_asset_upload_status(json, self.mock_cursor)
        self.assertEqual(
            str(ctx.exception),
            'Invalid key: asset_id, Value: some string? is not an int'
        )

        json = {
            'asset_id': 1,
            'uploaded_status': 'hello',
        }

        with self.assertRaises(ChangeUploadStatusInvalidArgsException) as ctx:
            change_asset_upload_status(json, self.mock_cursor)
        self.assertEqual(
            str(ctx.exception),
            "Invalid key: uploaded_status, Value: hello is not one of ['pending', 'complete']"
        )
    
    @patch.object(AssetDao, 'get_by_id')
    def test_invalid_asset_id(self, get_by_id_mock):
        get_by_id_mock.return_value = None

        json = {
            'asset_id': 1,
            'uploaded_status': UploadedStatus.COMPLETE.value,
        }

        with self.assertRaises(AssetNotFoundException) as ctx:
            change_asset_upload_status(json, self.mock_cursor)
        self.assertEqual(str(ctx.exception), 'Asset with id 1 not found')
