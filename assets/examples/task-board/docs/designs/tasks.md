# 任务板实现方案

状态：已实现；本机自动检查已验证，浏览器专项见需求。对应 [任务需求](../requirements/tasks.md) 的 AC-T1 至 T8（T4-v2 替代 v1）。

1. **涉及模块**：app HTTP/service/storage 与 web 页面/API；server 组装。
2. **各处改什么**：http.py 路由/映射；service.py 标题与存在性；storage.py 查询与事务；001_tasks.sql 建表；api.mjs 请求；page.mjs 状态；index.html 结构；tokens.css 样式；test_tasks.py 验收。归属由目录规范维护。
3. **数据流**：浏览器标题 → JSON → service.strip/验证 → storage 参数化插入 → JSON 任务 → DOM。完成把 done 赋 1，GET 默认筛 done=0，include_done=1 按 id 返回全部，页面显示状态。
4. **接口**：GET /api/tasks?include_done=0|1 → [{id,title,done}]；省略为 0，非法/重复参数 400；POST /api/tasks 输入 {title} → 201 任务；POST /api/tasks/{id}/complete 无正文 → 200 任务。非法输入 400 {error}，缺失 404 {error}。
5. **失败处理**：校验失败不写入；未知存储异常不包装成功；事务回滚，连接由 server 关闭。页面显示错误，恢复按钮；本机串行服务不含外部重试/定时任务。
6. **兼容影响**：GET 默认语义由全部改为未完成；同仓页面新增复选框并通过 api.mjs 传参。未知外部调用方待确认，不能称向后兼容。schema 未变，无数据迁移。只执行 001 建表；以后变更不能静默改已采用 SQL。没有账户，不声称对外安全或生产运行能力。
7. **验证方法**：根目录 unittest 10 项、node --check 两模块、build；UI 状态、视口和键盘按 UI 规范，未执行项单列。测试无生产数据。
8. **恢复**：停止本机服务并恢复前一代码快照；保留 tasks.sqlite3。结构或数据恢复需另行备份/验证，此例没有破坏性迁移，不能把应用回退称数据恢复。无灰度平台或发布流程。

实际路径与方案一致，自动验证结果见需求；当前无长期 ADR 决策，无需新建决策文件。

## 本次落地差异

在现有 http/service/storage.list_tasks 增加筛选参数，page/api/index 增加勾选读取；无新目录、无 SQL 迁移。tests 增加默认/显式全部/非法参数用例。恢复为回退这批代码与配套需求/方案，数据库数据保持不变；未做生产发布或数据恢复演练。
