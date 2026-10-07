# 本地任务板工程指引

## 项目定位与全景

教学项目供同机用户创建、查看、完成待办和筛选列表。Python 本地服务绑定 127.0.0.1；浏览器 → http → TaskService → SQLiteRepository，server 组装与关闭连接。只有一个服务，tasks 表归 storage 管理；无 ORM、外部服务或定时任务（依据 app/server.py、pyproject.toml）。

## 架构铁律

HTTP 做协议映射，service 校验业务输入，storage 做参数化 SQL 与事务；service 只调用传入 repository 行为，不导入 HTTP/SQLite。page.mjs → api.mjs → fetch，页面不直接请求。标题非法不写入，完成赋 done=1 保持幂等。详细文件归属与允许/禁止依赖以 [目录规范](docs/conventions/directory-structure.md) 为权威。

## 真实技术栈与目录摘要

pyproject.toml 声明 Python >=3.11、无第三方依赖；CI 声明 Python 3.11 与 Node 24。存储为标准库 sqlite3，前端为原生 HTML/CSS/JS modules，无框架或 npm 命令。本机实测版本见演练记录，与 CI 声明分开。

```text
app/                       # server 组装、http 协议、service 业务、storage 数据
web/                       # index.html、page.mjs、api.mjs、tokens.css
migrations/                # SQL；启动目前只执行 001_tasks.sql
tests/                     # test_*.py 行为/协议/隔离数据库
scripts/                   # build.py 编译与静态复制
.github/workflows/         # CI
pyproject.toml/.gitignore   # 运行声明/忽略配置
docs/conventions/          # 目录及适用规范
docs/requirements/         # 功能需求
docs/designs/              # 功能方案
dist/ / tasks.sqlite3      # 本机生成物，忽略
```

## 真实命令

都在项目根目录执行；依据 server.py、build.py 和 CI。

| 用途 | 命令 | 验证范围 |
|---|---|---|
| 启动 | `python3 -m app.server` | 本机服务；读取/写入 tasks.sqlite3 |
| 行为测试 | `python3 -m unittest discover -s tests -v` | 内存连接隔离；新增筛选基线 10 项 |
| JS 语法 | `node --check web/api.mjs`、`node --check web/page.mjs` | 语法，不证明 UI |
| 编译/静态复制 | `python3 scripts/build.py` | 无前端打包或生产部署 |

没有 lint、自动依赖门禁、覆盖率产物。实际结果写到具体需求/演练记录，不从命令存在推断通过。

## 任务触发 → 必须先读

- 新文件/目录/模块依赖：[目录规范](docs/conventions/directory-structure.md)。
- app/tests/scripts 的 Python：[Python](docs/conventions/python-standards.md)；web 的 JS：[JavaScript](docs/conventions/javascript-standards.md)。
- 前端组织/请求：[前端](docs/conventions/frontend-standards.md)；页面视觉/状态/键盘：[UI](docs/conventions/ui-standards.md)。
- 模型/SQL/事务/迁移：[数据库](docs/conventions/database-standards.md)。
- 新增列表筛选或改变条件：先读 [前端](docs/conventions/frontend-standards.md)、[UI](docs/conventions/ui-standards.md)、[需求写法](docs/conventions/requirement-standards.md)、[测试](docs/conventions/testing-standards.md) 与 [具体筛选需求](docs/requirements/list-filter.md)；然后按影响读目录/语言/数据库与 [方案写法](docs/conventions/technical-design-standards.md)、[具体方案](docs/designs/list-filter.md)。
- 其他行为：[需求写法](docs/conventions/requirement-standards.md)、[基本任务需求](docs/requirements/tasks.md)；跨模块/契约变化读 [方案规范](docs/conventions/technical-design-standards.md)。
- 验证/回归：[测试规范](docs/conventions/testing-standards.md)。

本例采用基线 3.2.0。关键未知业务规则先澄清；同步区分计划/已实现/已验证。功能条件变化通常改具体需求、方案、测试；通用约定改变才改规范，保留修订历史。
