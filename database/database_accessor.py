import psycopg2
import os

CONNECTION_ARGS = 'POSTGRESQL_LIBPQ_CONN_STR'

class DatabaseAccessor:
    connection = None
    def __init__(self):
        raise Exception('Not to be instantiated')
    
    @classmethod
    def connect(cls):
        connection_string = os.getenv(CONNECTION_ARGS)
        if not connection_string:
            raise RuntimeError('Expected a POSTGRESQL_URL env var to be set')
        cls.connection = psycopg2.connect(connection_string)
        
    @classmethod
    def get_connection(cls):
        if not cls.connection:
            raise RuntimeError(
                'Could not find database connection. Did you call connect() first?'
            )
        return cls.connection
