# 目录与依赖规范

## 范围与依据

适用整个任务板，依据 app 的实际导入、web 的模块引用、CI 与 build.py。当前布局即下面的布局，不含计划中的服务拆分。

## 具体归属与依赖

| 路径 | 放什么 | 禁止混放 |
|---|---|---|
| app/server.py | 依赖组装、连接/服务生命周期 | 标题业务校验 |
| app/http.py | HTTP 路由、JSON、状态映射、静态文件白名单 | SQL、任务业务判断 |
| app/service.py | 标题与任务规则、repository 调用 | HTTP/SQLite 导入 |
| app/storage.py | SQL、事务、行映射 | 页面提示、HTTP 状态 |
| web/api.mjs / page.mjs | 请求协议 / DOM 与页面状态 | page 内直接 fetch、API 层操作 DOM |
| web/index.html / tokens.css | 语义结构 / token 与样式 | 服务端规则或凭证 |
| tests/test_*.py | 行为、HTTP、隔离数据库测试 | 生产数据 |
| migrations/NNN_*.sql | 有序结构迁移 | 重写已采用迁移、需求说明 |
| scripts/、.github/workflows/、根配置 | 构建脚本、CI、运行声明 | 业务规则、密钥 |
| docs/conventions/、requirements/、designs/ | 写法规范、具体需求、具体方案 | 同份权威正文复制、多余账本 |
| dist/、tasks.sqlite3、__pycache__/ | 工具生成并忽略 | 手工维护、误提交 |

server → http/service/storage；http → service 实例；service → repository 行为；storage → sqlite3。api.mjs → fetch；page.mjs → api.mjs。反方向不允许。新增模块先确定职责；依赖变化同步根入口概要和本表。

## 正确例与反例

正确：标题 strip/长度校验在 app/service.py，http.py 捕获 ValueError 映射 400。错误：在 storage.py 返回 HTTP 400，或 http.py 拼接 INSERT；它们使业务与协议/存储互相耦合。

## 检查

阅读改动文件导入和调用方，对照上述方向；运行根目录 unittest 与 build.py 检查实际可用性。没有自动依赖门禁，文本 import 扫描只能定位，不能证明动态调用没有越界。
