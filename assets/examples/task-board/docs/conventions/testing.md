# 测试与验证规范

## 范围与真实命令

tests/test_tasks.py 使用 unittest，CI 来源 .github/workflows/ci.yml；根目录 python3 -m unittest discover -s tests -v。JS 语法用 node --check web/api.mjs 与 web/page.mjs，编译/静态复制用 python3 scripts/build.py。无覆盖率、格式、安全扫描配置。

## 具体规则

业务变化测可观察成功/拒绝/边界，HTTP 变化测状态与 JSON，数据变化测约束与事务，UI 另测状态/输入恢复/键盘。每个测试创建内存库并 addCleanup 关闭，禁止依赖测试顺序或运行库。缺陷回归先复现触发，不只检查内部方法调用。执行结果记具体需求，不新增大型测试账本；CI 未运行保持未验证。

## 正确例与反例

正确：非法标题 POST 返回 400，随后 GET 列表仍为空（test_invalid_title_leaves_data_unchanged）。错误：只搜索 `except` 就宣布所有错误已处理，或只断言 create 方法被调用。关键词扫描提供线索，业务场景须用外部结果证明。

## 检查与结果

本轮本机 8 项 unittest、两条 JS 语法、build 通过。需求中的验证表按 AC 记录；浏览器未执行项、CI Python 3.11、覆盖率、生产部署均不由这些结果推断。
