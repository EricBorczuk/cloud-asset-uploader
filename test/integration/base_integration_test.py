import unittest
from unittest.mock import patch
import requests
import cherrypy
import psycopg2
from yoyo import read_migrations
from yoyo import get_backend
from database.database_accessor import DatabaseAccessor
from cloud_asset_server import setup_cherry_tree, CHERRY_TREE_CONFIG
from external_services.s3_service import S3Service

class BaseIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cherrypy.tree.mount(setup_cherry_tree(), '/api', CHERRY_TREE_CONFIG)
    
    # This is run before each test case and is _incredibly_ slow.
    # There are quite a few ways to make this faster, just for the
    # scale/number of tests I have, I felt it was premature to optimize.
    def _set_up_database_schema(self):
        # Start with a clean state...really naively
        conn = psycopg2.connect('host=localhost port=5432')
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute('drop database if exists test_db')
            cur.execute('create database test_db')

        backend = get_backend('postgresql://localhost:5432/test_db')
        migrations = read_migrations('../../migrations', 'migrations')
        with backend.lock():
            # Apply migrations
            backend.apply_migrations(backend.to_apply(migrations))

    def setUp(self):
        self._set_up_database_schema()
        DatabaseAccessor.connect(testing=True)

        self.api_url = 'http://localhost:8080/api'
        self.headers = {
            'content-type': 'application/json',
        }
        self.patcher = patch.object(S3Service, 's3_client')
        self.s3_client_mock = self.patcher.start()
        self.connection = DatabaseAccessor.get_connection()

    def request(self, method, uri, data=None, headers={}):
        return getattr(requests, method)(
            self.api_url + uri,
            data=data,
            headers={**headers, **self.headers}
        )

    def tearDown(self):
        # drop and recreate the database to get a clean state
        DatabaseAccessor.get_connection().close()
        DatabaseAccessor.connection = None
        self.patcher.stop()
