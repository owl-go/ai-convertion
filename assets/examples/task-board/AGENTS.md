# 本地任务板工程指引

## 项目全景

这是可运行的教学项目，供同一台机器上的用户创建、查看和完成待办。只绑定 127.0.0.1，不含账户、角色、支付、外部服务或生产部署；不能据此推断其他项目需求。浏览器 → app/http.py → TaskService → SQLiteRepository；app/server.py 负责组装。仅一个服务，根入口已经覆盖服务信息，无独立服务入口。

## 架构铁律

HTTP 负责协议映射，service 负责标题/任务存在性规则，storage 负责参数化 SQL 与事务。server 可以导入三者；http 通过 service 实例调用；service 只依赖传入的 repository 行为，不导入 http/storage。浏览器请求只能从 web/api.mjs 发出。完成操作保持幂等；标题非法或任务不存在不能写入成功结果。本例直接使用 SQLite，不使用 ORM；核心表 tasks 归 storage 所有，迁移在 migrations。外部依赖与定时任务均无（app/server.py、pyproject.toml）。

## 真实技术栈

Python 声明 >=3.11，来自 pyproject.toml，CI 声明 3.11；本轮本机运行 3.14.7，不能称 CI 3.11 已验证。SQLite 来自 Python 标准库，本机 sqlite3.sqlite_version 为 3.53.4，查询命令 python3 -c 'import sqlite3; print(sqlite3.sqlite_version)'；原生浏览器 ES modules，无前端框架、第三方包、锁文件或 npm 命令。Node 仅用于语法检查，CI 声明 24，本机运行 24.14.0（.github/workflows/ci.yml）。

## 全景目录与归属

```text
app/                          # server 组装、http 协议、service 规则、storage 持久化
web/                          # index.html 页面、page.mjs 协调、api.mjs 请求、tokens.css 样式
migrations/                   # SQL 迁移
tests/                        # unittest 行为/HTTP/SQLite 测试
scripts/                      # build.py 编译检查与静态复制
.github/workflows/            # CI 配置
pyproject.toml / .gitignore    # 运行时声明、生成物忽略
docs/conventions/             # 目录与七类规则
docs/requirements/            # 具体需求
docs/designs/                 # 具体方案
dist/ / tasks.sqlite3         # 本机生成物，忽略、不手改
```

详细落位与正反例由 [目录规范](docs/conventions/directory-structure.md) 维护。新增业务领域先说明责任和依赖，更新本树及目录规范；当前没有待迁移目录。

## 运行与检查

全部从根目录运行，命令依据 server 模块、build 脚本、CI。

| 用途 | 实际命令 | 前提与状态 |
|---|---|---|
| 本机启动 | python3 -m app.server | 使用 tasks.sqlite3；本轮启动及 HTTP 冒烟已验证 |
| 行为/协议/数据测试 | python3 -m unittest discover -s tests -v | 内存库隔离；本轮 8 项通过 |
| JS 语法 | node --check web/api.mjs；node --check web/page.mjs | 本机 Node 24；本轮通过 |
| 编译与静态复制 | python3 scripts/build.py | 本轮通过；不是前端打包/生产部署 |

本例没有格式工具、架构自动检查、覆盖率工具或浏览器自动测试。依赖人工核对导入和调用链；UI 人工步骤见对应规范，未执行的视口/读屏检查保持未验证。

## 按任务读取

- 新文件、模块或依赖：读 [directory-structure](docs/conventions/directory-structure.md)。
- app Python 或 web JS：读 [language](docs/conventions/language.md) 的对应范围。
- 页面协调/请求：读 [frontend](docs/conventions/frontend.md)；页面状态/视觉/键盘再读 [ui](docs/conventions/ui.md)。
- SQL/模型/事务/迁移：读 [database](docs/conventions/database.md)。
- 行为变更：读 [requirements 写法](docs/conventions/requirements.md) 和 [任务需求](docs/requirements/tasks.md)。
- 跨模块或接口/数据变化：读 [方案写法](docs/conventions/technical-design.md) 和 [任务方案](docs/designs/tasks.md)。
- 验证：读 [testing](docs/conventions/testing.md)，将真实结果写回具体需求。

本例采用基线 3.1.0；代码与文档快照用于教学，实际项目 init 需重新读其证据。
