import sqlite3
from pathlib import Path


class SQLiteRepository:
    def __init__(self, connection):
        self.connection = connection
        self.connection.row_factory = sqlite3.Row

    def migrate(self):
        schema = Path(__file__).resolve().parents[1] / "migrations/001_tasks.sql"
        self.connection.executescript(schema.read_text())

    def create(self, title):
        with self.connection:
            cursor = self.connection.execute("INSERT INTO tasks(title) VALUES (?)", (title,))
        return self.get(cursor.lastrowid)

    def get(self, task_id):
        row = self.connection.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return dict(row) if row else None

    def list_tasks(self):
        return [dict(row) for row in self.connection.execute("SELECT id, title, done FROM tasks ORDER BY id")]

    def complete(self, task_id):
        with self.connection:
            self.connection.execute("UPDATE tasks SET done = 1 WHERE id = ?", (task_id,))
        return self.get(task_id)
