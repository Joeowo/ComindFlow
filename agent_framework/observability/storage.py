"""
S4-T8: 可观测性数据存储

提供 SQLite 持久化存储和数据清理功能。
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional


class StorageManager:
    """可观测性数据存储管理器

    使用 SQLite 持久化存储追踪数据、错误记录和指标。
    """

    def __init__(self, db_path: str) -> None:
        """初始化存储管理器

        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None

    def initialize(self) -> None:
        """初始化数据库表"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 创建追踪表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS traces (
                trace_id TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建错误表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS errors (
                error_id TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建指标表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def save_trace(self, trace_id: str, data: Dict[str, Any]) -> None:
        """保存追踪数据

        Args:
            trace_id: 追踪 ID
            data: 追踪数据
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO traces (trace_id, data, created_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (trace_id, json.dumps(data)))

        conn.commit()

    def get_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """获取追踪数据

        Args:
            trace_id: 追踪 ID

        Returns:
            追踪数据，如果不存在返回 None
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT data FROM traces WHERE trace_id = ?
        """, (trace_id,))

        row = cursor.fetchone()
        if row:
            return json.loads(row["data"])
        return None

    def save_error(self, error_data: Dict[str, Any]) -> None:
        """保存错误记录

        Args:
            error_data: 错误数据
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        error_id = error_data.get("error_id")
        if not error_id:
            return

        cursor.execute("""
            INSERT OR REPLACE INTO errors (error_id, data, created_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (error_id, json.dumps(error_data)))

        conn.commit()

    def get_errors(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取错误列表

        Args:
            limit: 最大返回数量

        Returns:
            错误列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT data FROM errors
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))

        errors = []
        for row in cursor.fetchall():
            errors.append(json.loads(row["data"]))

        return errors

    def cleanup_old_data(self, days: int = 7) -> int:
        """清理旧数据

        Args:
            days: 保留天数，超过此天数的数据将被删除

        Returns:
            删除的行数
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cutoff_timestamp = datetime.now() - timedelta(days=days)

        # 清理旧追踪 - 使用数据库的 created_at 字段
        cursor.execute("""
            DELETE FROM traces WHERE datetime(created_at) < datetime(?)
        """, (cutoff_timestamp.isoformat(),))

        deleted_traces = cursor.rowcount

        # 清理旧错误
        cursor.execute("""
            DELETE FROM errors WHERE datetime(created_at) < datetime(?)
        """, (cutoff_timestamp.isoformat(),))

        deleted_errors = cursor.rowcount

        # 清理旧指标
        cursor.execute("""
            DELETE FROM metrics WHERE datetime(timestamp) < datetime(?)
        """, (cutoff_timestamp.isoformat(),))

        deleted_metrics = cursor.rowcount

        conn.commit()

        return deleted_traces + deleted_errors + deleted_metrics

    def close(self) -> None:
        """关闭数据库连接"""
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def __del__(self) -> None:
        """析构函数，确保连接关闭"""
        self.close()
