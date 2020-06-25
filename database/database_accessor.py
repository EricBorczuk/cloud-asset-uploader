import psycopg2
import os

CONNECTION_ARGS = 'POSTGRESQL_LIBPQ_CONN_STR'
TEST_DB_CONN_ARGS = 'host=localhost port=5432 dbname=test_db'

class DatabaseAccessor:
    connection = None
    def __init__(self):
        raise Exception('Not to be instantiated')
    
    @classmethod
    def connect(cls, testing=False):
        connection_string = TEST_DB_CONN_ARGS if testing else os.getenv(CONNECTION_ARGS)
        if not connection_string:
            raise RuntimeError('Expected a POSTGRESQL_LIBPQ_CONN_STR env var to be set')
        if cls.connection is not None:
            # Don't allow reconnects...should probably warn here,
            # as it means a developer made a mistake
            return
        cls.connection = psycopg2.connect(connection_string)
        
    @classmethod
    def get_connection(cls):
        if not cls.connection:
            raise RuntimeError(
                'Could not find database connection. Did you call connect() first?'
            )
        return cls.connection
