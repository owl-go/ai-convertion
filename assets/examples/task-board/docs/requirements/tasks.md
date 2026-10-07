# 本机任务创建与完成

状态：代码已实现；下表自动行为已验证，浏览器验收按实际记录。依据：本技能的教学演练目标，不代表真实产品需求。

## 目标与范围

本机用户记录待办并标记完成。列表保留完成任务，便于确认操作结果；只含标题和完成状态。无账户、外部同步、删除、编辑、权限、支付或生产服务。

## 规则与验收

| AC | 给定/动作 | 可观察结果 |
|---|---|---|
| AC-T1 | POST /api/tasks，title 为两端带空白的有效字符串 | 201，返回去空白的 title、整数 id、done=0；GET 可见 |
| AC-T2 | 空白、非字符串或超过 80 字符标题 | 400，列表和数据库不新增 |
| AC-T3 | 对现有任务 POST /api/tasks/{id}/complete，再重复调用 | 200、done=1；重复返回相同对象，不新增任务 |
| AC-T4-v1 | 完成任务后 GET /api/tasks | 返回全部任务，含已完成项，按 id 升序 |
| AC-T5 | 完成不存在的任务或非法 id | 分别 404/400，不改其他数据 |
| AC-T6 | 页面空列表→创建→完成；失败或提交等待 | 显示空/数据/完成文字，等待禁用，失败保留输入与重试 |

## 实施与验证

| AC | 实现位置 | 实际证据/状态 |
|---|---|---|
| T1/T2 | app/service.py、http.py、storage.py | test_create_and_list / test_invalid_title_leaves_data_unchanged，本机通过 |
| T3/T4-v1/T5 | 同上 | complete 幂等、unknown_task 测试通过；含完成项列表由本轮 HTTP 冒烟核对 |
| T6 | web/page.mjs、index.html、tokens.css | 浏览器创建→完成可见、停止服务后失败保留输入与按钮恢复已验证；390 视口/键盘/读屏未验证 |

本机 Python 3.14.7，Node 24.14.0；unittest 8 项、JS 语法、build 通过。CI/部署/覆盖率未运行。相关实现方案见 [tasks](../designs/tasks.md)。
