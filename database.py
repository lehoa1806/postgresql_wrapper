from typing import Any, Dict, Iterable, Iterator, Tuple

import psycopg2

from .connection import Connection
from .table import Table


class Database:
    def __init__(
        self,
        connection: Connection,
    ) -> None:
        self.connection = connection

    @classmethod
    def create_db_connection(
        cls,
        config: Dict[str, str],
    ) -> Connection:
        connection = psycopg2.connect(
            host=config['host'],
            user=config['user'],
            password=config['password'],
            dbname=config['dbname'],
            port=config['port'],
        )
        return Connection(psycopg2_client=connection)

    @classmethod
    def load_database(
        cls,
        config: Dict[str, str],
    ) -> 'Database':
        database_connection = cls.create_db_connection(config)
        return cls(database_connection)

    def get_tables(self) -> Iterable[Tuple[str, Table]]:
        query = 'SELECT tablename FROM pg_catalog.pg_tables'
        for result in self.query(query, ('table',)):
            name = result['table']
            yield name, Table(connection=self.connection, table_name=name)

    def load_table(self, table_name: str) -> Table:
        return Table(connection=self.connection, table_name=table_name)

    # PostgresSQL Functions
    def show_processlist(self) -> Iterator[Dict[str, Any]]:
        query = 'SELECT * FROM pg_stat_activity;'
        keys = ('datid', 'datname', 'procipd', 'usename', 'current_query',
                'query_start')
        yield from self.connection.query(query, keys)

    def execute(
        self,
        command: str,
        params: Iterable[Any] = None,
    ) -> None:
        self.connection.execute(command=command, params=params)

    def query(
        self,
        query: str,
        keys: Tuple,
    ) -> Iterator[Dict[str, str]]:
        yield from self.connection.query(query, keys)
