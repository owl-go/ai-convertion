# 本机任务创建与完成

状态：代码已实现；下表自动行为已验证，浏览器验收按实际记录。依据：本技能的教学演练目标，不代表真实产品需求。

## 目标与范围

本机用户记录待办并标记完成。默认列表只显示待完成项；勾选显示已完成任务后可查看全部；只含标题和完成状态。无账户、外部同步、删除、编辑、权限、支付或生产服务。

## 规则与验收

| AC | 给定/动作 | 可观察结果 |
|---|---|---|
| AC-T1 | POST /api/tasks，title 为两端带空白的有效字符串 | 201，返回去空白的 title、整数 id、done=0；GET 可见 |
| AC-T2 | 空白、非字符串或超过 80 字符标题 | 400，列表和数据库不新增 |
| AC-T3 | 对现有任务 POST /api/tasks/{id}/complete，再重复调用 | 200、done=1；重复返回相同对象，不新增任务 |
| AC-T4-v2 | 有已完成和未完成项，GET /api/tasks（省略或 include_done=0） | 只返回未完成项，按 id 升序 |
| AC-T7 | GET /api/tasks?include_done=1 | 返回全部任务，含已完成项，按 id 升序 |
| AC-T8 | include_done 为空、其他值或重复传入 | 400 {error}，不写数据 |
| AC-T5 | 完成不存在的任务或非法 id | 分别 404/400，不改其他数据 |
| AC-T6 | 页面空列表→创建→完成；失败或提交等待 | 显示空/数据/完成文字，等待禁用，失败保留输入与重试 |

## 实施与验证

| AC | 实现位置 | 实际证据/状态 |
|---|---|---|
| T1/T2 | app/service.py、http.py、storage.py | test_create_and_list / test_invalid_title_leaves_data_unchanged，本机通过 |
| T3/T4-v2/T5/T7/T8 | 同上 | 完成/缺失测试、test_active_default_and_opt_in_complete、test_invalid_filter；本轮 10 项通过 |
| T6 | web/page.mjs、index.html、tokens.css | 基线创建/完成已复验；扩展条件的失败恢复、390/1280视口与键盘提交已做基础检查，读屏/对比度未验证 |

实际环境与结果见本轮验证记录；unittest 10 项、JS 语法、build 通过。CI/部署/覆盖率未运行。相关实现方案见 [tasks](../designs/tasks.md)。

## 修订（2026-10-07 教学模拟新要求）

AC-T4-v1 的旧结果为 GET 返回全部任务；新要求以 AC-T4-v2 替代，并新增 T7/T8。旧行为保留在这条修订记录；默认语义发生兼容变化，同仓页面随接口更新，未知外部客户端未验证。任务完成后在默认列表消失；勾选“显示已完成任务”再出现。一般需求写法、UI 状态规范和数据库 schema 不变。
