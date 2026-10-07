# 任务板实现方案

状态：已实现；本机自动检查已验证，浏览器专项见需求。对应 [任务需求](../requirements/tasks.md) 的 AC-T1 至 T6。

1. **涉及模块**：app HTTP/service/storage 与 web 页面/API；server 组装。
2. **各处改什么**：http.py 路由/映射；service.py 标题与存在性；storage.py 查询与事务；001_tasks.sql 建表；api.mjs 请求；page.mjs 状态；index.html 结构；tokens.css 样式；test_tasks.py 验收。归属由目录规范维护。
3. **数据流**：浏览器标题 → JSON → service.strip/验证 → storage 参数化插入 → JSON 任务 → DOM。完成把 done 赋 1，GET 按 id 返回全部，页面显示状态。
4. **接口**：GET /api/tasks → [{id,title,done}]；POST /api/tasks 输入 {title} → 201 任务；POST /api/tasks/{id}/complete 无正文 → 200 任务。非法输入 400 {error}，缺失 404 {error}。
5. **失败处理**：校验失败不写入；未知存储异常不包装成功；事务回滚，连接由 server 关闭。页面显示错误，恢复按钮；本机串行服务不含外部重试/定时任务。
6. **兼容影响**：这是初始接口/表，无旧版本迁移。只执行 001 建表；以后变更不能静默改已采用 SQL。没有账户，不声称对外安全或生产运行能力。
7. **验证方法**：根目录 unittest 8 项、node --check 两模块、build；UI 状态、视口和键盘按 UI 规范，未执行项单列。测试无生产数据。
8. **恢复**：停止本机服务并恢复前一代码快照；保留 tasks.sqlite3。结构或数据恢复需另行备份/验证，此例没有破坏性迁移，不能把应用回退称数据恢复。无灰度平台或发布流程。

实际路径与方案一致，自动验证结果见需求；当前无长期 ADR 决策，无需新建决策文件。
