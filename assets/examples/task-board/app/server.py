import sqlite3
from contextlib import closing
from wsgiref.simple_server import make_server

from app.http import Application
from app.service import TaskService
from app.storage import SQLiteRepository


def main():
    with closing(sqlite3.connect("tasks.sqlite3")) as connection:
        repository = SQLiteRepository(connection)
        repository.migrate()
        app = Application(TaskService(repository))
        with make_server("127.0.0.1", 8765, app) as server:
            server.serve_forever()


if __name__ == "__main__":
    main()
