from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class UploadedStatus(Enum):
    PENDING = 'pending'
    COMPLETE = 'complete'

@dataclass
class AssetRow:
    id: int
    uploaded_status: str
    bucket: str
    object_key: str
    create_date: datetime

ALL_COLUMN_NAMES = ['id', 'uploaded_status', 'bucket', 'object_key', 'create_date']
NON_PK_COLS = ALL_COLUMN_NAMES[1:]

class AssetDao:
    def _convert_to_asset_row(result_row):
        return AssetRow(*result_row)

    @staticmethod
    def get_by_id(asset_id, cursor):
        """
        Fetch an asset by its ID.
        Returns an AssetRow if it exists.
        Returns None if the asset does not exist.
        """
        cursor.execute(
            f'select {",".join(ALL_COLUMN_NAMES)} from asset '
            'where id = %s',
            (asset_id,)
        )
        result = cursor.fetchone()
        if result is None:
            return None
        return AssetDao._convert_to_asset_row(result)
    
    @staticmethod
    def get_by_bucket_and_key(
        bucket,
        object_key,
        cursor
    ):
        """
        Fetch an asset by a bucket and object key.
        Returns an AssetRow if it exists.
        Returns None if the asset does not exist.
        """
        cursor.execute(
            f'select {",".join(ALL_COLUMN_NAMES)} from asset '
            'where bucket = %s and object_key = %s',
            (bucket, object_key)
        )
        result = cursor.fetchone()
        if result is None:
            return None
        return AssetDao._convert_to_asset_row(result)
    
    @staticmethod
    def insert_one(asset_row, cursor):
        """
        Insert a new asset row.
        Ignores any id that is set on asset_row.
        Returns the created AssetRow (with id populated) if successful.
        """

        cursor.execute(
            f'insert into asset({",".join(NON_PK_COLS)}) values('
            f'{",".join(["%s"] * len(NON_PK_COLS))}) returning {",".join(ALL_COLUMN_NAMES)}',
            (asset_row.uploaded_status, asset_row.bucket, asset_row.object_key, asset_row.create_date)
        )
        result = cursor.fetchone()
        return AssetDao._convert_to_asset_row(result)
    
    @staticmethod
    def update_uploaded_status(asset_id, new_status, cursor):
        """
        Updates the asset with id `asset_id` to have the status `new_status`
        """
        cursor.execute(
            'update asset set uploaded_status = %s where id = %s',
            (new_status, asset_id)
        )

