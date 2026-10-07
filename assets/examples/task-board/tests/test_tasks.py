import io
import json
import sqlite3
import unittest
from app.http import Application
from app.service import TaskService
from app.storage import SQLiteRepository


class TaskTests(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.addCleanup(self.connection.close)
        self.repository = SQLiteRepository(self.connection)
        self.repository.migrate()
        self.service = TaskService(self.repository)
        self.app = Application(self.service)

    def request(self, method, path, body=None, query=""):
        raw = json.dumps(body).encode() if body is not None else b""
        status = []
        environ = {"REQUEST_METHOD": method, "PATH_INFO": path, "CONTENT_LENGTH": str(len(raw)), "QUERY_STRING": query, "wsgi.input": io.BytesIO(raw)}
        response = self.app(environ, lambda value, headers: status.append(value))
        return status[0], json.loads(b"".join(response))

    def test_create_and_list(self):
        status, task = self.request("POST", "/api/tasks", {"title": "  补规范  "})
        self.assertEqual(status, "201 Created")
        self.assertEqual(task["title"], "补规范")
        self.assertEqual(self.request("GET", "/api/tasks")[1], [task])

    def test_invalid_title_leaves_data_unchanged(self):
        for title in [" ", "x" * 81, None, 3]:
            self.assertEqual(self.request("POST", "/api/tasks", {"title": title})[0], "400 Bad Request")
        self.assertEqual(self.service.list_tasks(), [])

    def test_complete_is_idempotent(self):
        task = self.service.create("验收")
        first = self.request("POST", f"/api/tasks/{task['id']}/complete")
        self.assertEqual(first[0], "200 OK")
        self.assertEqual(first[1]["done"], 1)
        self.assertEqual(self.request("POST", f"/api/tasks/{task['id']}/complete"), first)

    def test_active_default_and_opt_in_complete(self):
        done = self.service.create("已做")
        active = self.service.create("待做")
        self.service.complete(done["id"])
        self.assertEqual(self.request("GET", "/api/tasks")[1], [active])
        all_tasks = self.request("GET", "/api/tasks", query="include_done=1")[1]
        self.assertEqual([task["id"] for task in all_tasks], [done["id"], active["id"]])
        self.assertEqual(all_tasks[0]["done"], 1)

    def test_invalid_filter(self):
        for query in ["include_done=yes", "include_done=", "include_done=1&include_done=0"]:
            self.assertEqual(self.request("GET", "/api/tasks", query=query)[0], "400 Bad Request")

    def test_unknown_task_and_bad_id(self):
        self.assertEqual(self.request("POST", "/api/tasks/999/complete")[0], "404 Not Found")
        self.assertEqual(self.request("POST", "/api/tasks/no/complete")[0], "400 Bad Request")

    def test_malformed_json_and_nonobject(self):
        environ = {"REQUEST_METHOD": "POST", "PATH_INFO": "/api/tasks", "CONTENT_LENGTH": "1", "wsgi.input": io.BytesIO(b"{")}
        status = []
        self.app(environ, lambda value, headers: status.append(value))
        self.assertEqual(status, ["400 Bad Request"])
        self.assertEqual(self.request("POST", "/api/tasks", ["title"])[0], "400 Bad Request")

    def test_database_constraints_and_migration_repeat(self):
        self.repository.migrate()
        with self.assertRaises(sqlite3.IntegrityError):
            self.repository.create(" ")
        with self.assertRaises(sqlite3.IntegrityError):
            self.connection.execute("INSERT INTO tasks(title, done) VALUES (?, ?)", ("bad", 2))
        self.assertEqual(self.repository.list_tasks(), [])

    def test_sql_like_title_is_data(self):
        title = "x'); DROP TABLE tasks; --"
        task = self.service.create(title)
        self.assertEqual(self.repository.get(task["id"])["title"], title)
        self.assertEqual(len(self.service.list_tasks()), 1)

    def test_static_and_unknown_path(self):
        status = []
        body = self.app({"REQUEST_METHOD": "GET", "PATH_INFO": "/"}, lambda value, headers: status.append(value))
        self.assertEqual(status, ["200 OK"])
        self.assertIn(b"<!doctype html>", body[0])
        self.assertEqual(self.request("GET", "/unknown")[0], "404 Not Found")
