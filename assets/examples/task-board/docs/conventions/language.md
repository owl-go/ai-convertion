# Python 与 JavaScript 编码规范

## 范围与来源

app/、tests/、scripts/ 使用 pyproject.toml 声明的 Python >=3.11；web/*.mjs 使用原生 ES modules。没有格式/类型工具配置，不能假造 lint 或 typecheck 命令。

## 具体规则

Python 模块/函数用 snake_case、类用 PascalCase，导入保持标准库与本地模块分组；HTTP 外部 JSON 必须先验证对象类型，标题校验由 TaskService 统一执行。ValueError 表达输入错误，LookupError 表达缺失，http.py 映射 400/404；未知错误保持失败，不返回假成功。连接由 server 的 with 关闭；每次 SQL 写入用连接事务，测试连接用 addCleanup。当前无并发任务或异步请求，不新增无生命周期的后台线程。

JS 导出的请求函数用 camelCase，page 的 DOM 文本用 textContent；所有 await 错误在请求或事件边界展示，finally 恢复提交按钮。新增第三方包需要说明用途并建立实际清单/锁定方式，当前仅用标准库和浏览器 API。

## 正确例与反例

正确（app/http.py）：`except ValueError as error: status, result = "400 Bad Request", {"error": str(error)}`。错误：`except ValueError: return success`，调用方会把输入失败当成功。正确（web/page.mjs）：`label.textContent = task.title`；错误：`label.innerHTML = task.title`，用户标题会成为 HTML。

## 检查

根目录运行 python3 scripts/build.py 编译；node --check web/api.mjs 与 web/page.mjs 查语法；unittest 观察非法输入、错误映射、资源隔离。编译/语法不证明业务正确，格式一致性靠针对改动的人工审阅。
