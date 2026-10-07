# SQLite 数据库规范

## 范围与依据

app/storage.py、migrations/001_tasks.sql；标准库 sqlite3，无 ORM。tasks.sqlite3 是本机运行数据，测试使用内存连接；tasks(id,title,done) 归 storage 所有。

## 具体规则

表/列 snake_case，id 为整数主键，title 非空且 trim 后 1–80 字符，done 只允许 0/1 默认 0（schema 兜底，service 提供可读错误）。当前无时间/金额/敏感字段，新增时写单位、时区、空值和访问边界。SQL 值用 execute 的占位参数；动态结构先白名单，service/http 不执行 SQL。每个写操作由 storage 的 with connection 提交/回滚。完成用赋值 done=1 保持幂等，当前串行本机服务不声称并发扩展已验证。

列表按主键 id 排序，目前没有额外索引；新增索引需要实际过滤/查询计划证据。新增迁移追加 NNN_*.sql，不能改已采用 001；当前启动只执行 001，新增迁移先实现版本执行机制。迁移评估旧数据、重跑、中断、兼容、备份恢复；没有验证的恢复不能写已通过。

## 正确例与反例

正确：`connection.execute("UPDATE tasks SET done = 1 WHERE id = ?", (task_id,))`。错误：把用户标题拼进 INSERT 字符串；先做页面校验就省略数据库约束。

## 检查

根目录 unittest 覆盖非法标题/状态约束、迁移重跑、SQL 样式标题作为数据、完成幂等。schema 未变化时不新建迁移。文件数据库损坏恢复、真实多进程并发和生产数据迁移未验证。
