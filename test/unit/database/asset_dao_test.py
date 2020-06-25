import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from database.asset_dao import AssetDao, AssetRow, UploadedStatus

class GetByIdUnitTest(unittest.TestCase):
    def setUp(self):
        self.mock_cursor = MagicMock()
        self.sample_asset_row_tuple = (
            (1, 'a', 'b', 'c', datetime.min)
        )
        self.sample_asset_row_dataclass = AssetRow(
            id=1,
            uploaded_status='a',
            bucket='b',
            object_key='c',
            create_date=datetime.min
        )

    def test_happy_path(self):
        """
        Given:
            The `asset_id` exists in the database
        Then:
            A dataclass with its row's data is returned
        """
        self.mock_cursor.fetchone.return_value = self.sample_asset_row_tuple
        result = AssetDao.get_by_id(1, self.mock_cursor)

        self.mock_cursor.execute.assert_called_once_with(
            'select id,uploaded_status,bucket,object_key,create_date '
            'from asset where id = %s',
            (1,)
        )

        self.assertEqual(result, self.sample_asset_row_dataclass)
    
    def test_not_found(self):
        """
        Given:
            The request asset_id does not exist in the database
        Then:
            `None` is returned
        """
        self.mock_cursor.fetchone.return_value = None
        result = AssetDao.get_by_id(1, self.mock_cursor)

        self.mock_cursor.execute.assert_called_once_with(
            'select id,uploaded_status,bucket,object_key,create_date '
            'from asset where id = %s',
            (1,)
        )

        self.assertIsNone(result)

class GetByBucketAndKeyUnitTest(unittest.TestCase):
    def setUp(self):
        self.mock_cursor = MagicMock()
        self.sample_asset_row_tuple = (
            (1, 'a', 'b', 'c', datetime.min)
        )
        self.sample_asset_row_dataclass = AssetRow(
            id=1,
            uploaded_status='a',
            bucket='b',
            object_key='c',
            create_date=datetime.min
        )
    
    def test_happy_path(self):
        """
        Given:
            The asset row with the given `bucket_id` and `object_key` exists in the database
        Then:
            A dataclass with its row's data is returned
        """
        self.mock_cursor.fetchone.return_value = self.sample_asset_row_tuple
        result = AssetDao.get_by_bucket_and_key('my_bucket', 'my_object_key', self.mock_cursor)

        self.mock_cursor.execute.assert_called_once_with(
            'select id,uploaded_status,bucket,object_key,create_date '
            'from asset where bucket = %s and object_key = %s',
            ('my_bucket', 'my_object_key')
        )

        self.assertEqual(result, self.sample_asset_row_dataclass)
    
    def test_not_found(self):
        """
        Given:
            The asset row with the given `bucket_id` and `object_key` does not exist
            in the database
        Then:
            `None` is returned
        """
        self.mock_cursor.fetchone.return_value = None
        result = AssetDao.get_by_bucket_and_key('my_bucket', 'my_object_key', self.mock_cursor)

        self.mock_cursor.execute.assert_called_once_with(
            'select id,uploaded_status,bucket,object_key,create_date '
            'from asset where bucket = %s and object_key = %s',
            ('my_bucket', 'my_object_key')
        )

        self.assertEqual(result, None)
    
class InsertOneUnitTest(unittest.TestCase):
    def setUp(self):
        self.mock_cursor = MagicMock()
        self.sample_asset_row_tuple = (
            (1, 'a', 'b', 'c', datetime.min)
        )
        self.pre_insert_dataclass = AssetRow(
            id=None,
            uploaded_status='a',
            bucket='b',
            object_key='c',
            create_date=datetime.min
        )
        self.sample_asset_row_dataclass = AssetRow(
            id=1,
            uploaded_status='a',
            bucket='b',
            object_key='c',
            create_date=datetime.min
        )
    
    def test_happy_path(self):
        """
        Given:
            An AssetRow dataclass is supplied to insert
        Then:
            The data is inserted, and a dataclass with its row's data is returned
        """
        self.mock_cursor.fetchone.return_value = self.sample_asset_row_tuple
        result = AssetDao.insert_one(self.pre_insert_dataclass, self.mock_cursor)

        self.mock_cursor.execute.assert_called_once_with(
            'insert into asset(uploaded_status,bucket,object_key,create_date) values('
            '%s,%s,%s,%s) returning id,uploaded_status,bucket,object_key,create_date',
            (
                self.pre_insert_dataclass.uploaded_status,
                self.pre_insert_dataclass.bucket,
                self.pre_insert_dataclass.object_key,
                self.pre_insert_dataclass.create_date,
            )
        )

        self.assertEqual(result, self.sample_asset_row_dataclass)

class UpdateUploadedStatusUnitTest(unittest.TestCase):
    def setUp(self):
        self.mock_cursor = MagicMock()
    
    def test_happy_path(self):
        """
        Given:
            An asset_id and uploaded_status are supplied
        Then:
            A SQL update is performed
        """
        AssetDao.update_uploaded_status(1, UploadedStatus.COMPLETE.value, self.mock_cursor)

        self.mock_cursor.execute.assert_called_once_with(
            'update asset set uploaded_status = %s where id = %s',
            (UploadedStatus.COMPLETE.value, 1)
        )