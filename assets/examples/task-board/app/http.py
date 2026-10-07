import json
from pathlib import Path
from urllib.parse import parse_qs


class Application:
    def __init__(self, service):
        self.service = service

    def __call__(self, environ, start_response):
        method, path = environ["REQUEST_METHOD"], environ["PATH_INFO"]
        status, content_type = "200 OK", "application/json; charset=utf-8"
        try:
            if method == "GET" and path == "/api/tasks":
                query = parse_qs(environ.get("QUERY_STRING", ""), keep_blank_values=True)
                values = query.get("include_done", ["0"])
                if len(values) != 1 or values[0] not in {"0", "1"}:
                    raise ValueError("include_done 需为 0 或 1")
                result = self.service.list_tasks(include_done=values[0] == "1")
            elif method == "POST" and path == "/api/tasks":
                length = int(environ.get("CONTENT_LENGTH") or 0)
                if not 0 < length <= 4096:
                    raise ValueError("请求体长度无效")
                payload = json.loads(environ["wsgi.input"].read(length))
                if not isinstance(payload, dict):
                    raise ValueError("请求体需为对象")
                result = self.service.create(payload.get("title"))
                status = "201 Created"
            elif method == "POST" and path.startswith("/api/tasks/") and path.endswith("/complete"):
                result = self.service.complete(int(path.split("/")[3]))
            elif method == "GET" and path in {"/", "/api.mjs", "/page.mjs", "/tokens.css"}:
                filename = "index.html" if path == "/" else path[1:]
                content_type = {"html": "text/html", "mjs": "text/javascript", "css": "text/css"}[filename.split(".")[-1]] + "; charset=utf-8"
                body = (Path(__file__).resolve().parents[1] / "web" / filename).read_bytes()
                start_response(status, [("Content-Type", content_type)])
                return [body]
            else:
                raise LookupError("路径不存在")
        except ValueError as error:
            status, result = "400 Bad Request", {"error": str(error)}
        except LookupError as error:
            status, result = "404 Not Found", {"error": str(error)}
        body = json.dumps(result, ensure_ascii=False).encode()
        start_response(status, [("Content-Type", content_type)])
        return [body]
