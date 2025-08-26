import asyncpg
import pymysql
import pyodbc
import oracledb
import pytds as tds

from typing import Optional, List, Any
from dependency_injector.wiring import inject, Provide

from Domain.Models.ApplicationConfigurationModels.AppSettingsModel import DataBaseConnectionModel
from Domain.Enums.DataBaseType import DataBaseType
from Domain.Utils import Utils


class DefaultDatabaseAccess:
    @inject
    def __init__(self,
                 utils: Utils = Provide["AppContainer.utils"]):
        self._connection_cache = {}
        self._utils = utils

    @staticmethod
    def _normalize_conn_key(db: DataBaseConnectionModel):
        return f"{db.TYPE}:{db.CONNECTION_STRING}"

    async def connect(self, db: DataBaseConnectionModel):
        key = self._normalize_conn_key(db)
        if key in self._connection_cache:
            return self._connection_cache[key]

        conn = None
        try:
            if db.TYPE == DataBaseType.POSTGRESQL:
                conn = await asyncpg.connect(db.CONNECTION_STRING)
            elif db.TYPE in (DataBaseType.MYSQL, DataBaseType.MARIADB):
                conn = pymysql.connect(**self._utils.parse_mysql(db.CONNECTION_STRING))
            elif db.TYPE == DataBaseType.SQLSERVER:
                conn = pyodbc.connect(db.CONNECTION_STRING)
            elif db.TYPE == DataBaseType.ORACLE:
                conn = oracledb.connect(db.CONNECTION_STRING)
            elif db.TYPE == DataBaseType.FIREBIRD:
                conn = tds.connect(server="localhost", database="...", user="...", password="...")  # adjust
            else:
                raise ValueError(f"Unsupported DB: {db.TYPE}")
        except Exception as e:
            print(f"[DB ERROR] {e}")
            return None

        self._connection_cache[key] = conn
        return conn

    async def query_first(self, db: DataBaseConnectionModel, query: str, params: Optional[dict] = None) -> Optional[Any]:
        conn = await self.connect(db)
        if conn is None:
            return None

        try:
            if db.TYPE == DataBaseType.POSTGRESQL:
                return await conn.fetchrow(query, *params.values()) if params else await conn.fetchrow(query)
            elif db.TYPE in (DataBaseType.MYSQL, DataBaseType.MARIADB, DataBaseType.SQLSERVER):
                cursor = conn.cursor()
                cursor.execute(query, params or {})
                return cursor.fetchone()
            return None
        except Exception as e:
            print(f"[QUERY ERROR] {e}")
            return None

    async def query(self, db: DataBaseConnectionModel, query: str, params: Optional[dict] = None) -> List[Any]:
        conn = await self.connect(db)
        if conn is None:
            return []

        try:
            if db.TYPE == DataBaseType.POSTGRESQL:
                return await conn.fetch(query, *params.values()) if params else await conn.fetch(query)
            elif db.TYPE in (DataBaseType.MYSQL, DataBaseType.MARIADB, DataBaseType.SQLSERVER):
                cursor = conn.cursor()
                cursor.execute(query, params or {})
                return cursor.fetchall()
            return []
        except Exception as e:
            print(f"[QUERY ERROR] {e}")
            return []


