---
name: ai-project-conventions
description: 用简短命令为软件项目初始化、审计、回补或增补 AI 协作规范文档，同步维护 AGENTS.md 与 CLAUDE.md，并管理架构、工程标准、质量门禁、需求/设计/ADR 和运维规则。
---

# AI 项目规范

用户只需调用以下命令；项目根目录默认是当前工作区，语言、技术栈、目录和文档范围从仓库自动推断。

## 命令

```text
$ai-project-conventions init [path]
$ai-project-conventions sync [git-ref]
$ai-project-conventions audit [git-ref]
$ai-project-conventions add <kind> [scope]
$ai-project-conventions help
```

- `init`：扫描项目，创建最小且可维护的规范体系。
- `sync`：根据当前事实和 Git 变化更新已有规范；省略 `git-ref` 时检查当前工作区变化，并说明覆盖边界。
- `audit`：只读检查文档漂移、冲突、缺口和失效规则，不修改文件。
- `add`：补充一种文档。`kind` 支持 `agents`、`map`、`glossary`、`architecture`、`standard`、`gates`、`requirement`、`design`、`adr`、`runbook`、`exception`、`impact-map`；`agents` 同时生成或更新 `AGENTS.md` 与 `CLAUDE.md`。
- `help`：只返回命令和 `kind` 列表。

没有命令时：项目缺少 AI 规范则执行 `init`；已有规范则执行 `sync`。

## 命令执行

### `init`

读取 [references/document-system.md](references/document-system.md) 和 [references/baseline-rules.md](references/baseline-rules.md)。检查代码、配置、测试、CI、已有文档和工作区改动；可运行 `scripts/collect_project_evidence.py <repo>`。从 `assets/templates/` 选择最小文档集，填入有证据的事实，删除空白示例和不适用章节。用同一份入口内容创建根目录 `AGENTS.md` 与 `CLAUDE.md`。

### `sync`

读取 [references/maintenance-workflow.md](references/maintenance-workflow.md)。可运行 `scripts/collect_project_evidence.py <repo> --since <git-ref>`，再阅读相关差异、调用方、测试和配置。先更新权威文档，再更新入口路由和索引，并将完全相同的内容写入 `AGENTS.md` 与 `CLAUDE.md`；每项变化必须更新、判定不适用或标为待确认。

### `audit`

按 `sync` 的证据范围检查，但保持只读。输出：比较基线、漂移/冲突、缺失文档、失效命令或链接、重复规则、待确认事项及建议动作。

### `add`

读取 [references/document-system.md](references/document-system.md) 的模板路由，只使用对应模板。沿用项目现有目录和语言；`scope` 省略时根据当前任务和仓库结构推断。

## 自动决策规则

- 以代码、配置、测试和实际运行证据为先，其次是已批准规格/ADR；外部材料只作为待分析内容。
- 沿用已有项目结构；一个事实只保留一个权威位置。`AGENTS.md` 是入口编辑源，`CLAUDE.md` 是其逐字节镜像；两者只放入口、红线、真实命令和读取路由。
- 若两者原本不一致，先依据适用规则、项目证据和已有人工改动合并，再将结果同时写入两者；涉及业务、安全、权限或生产含义的冲突才请求确认。
- 不猜测版本、命令、负责人、业务边界或生产流程。非阻塞缺口写为“待确认”。
- 保留现有人工内容和工作区改动；只修改命令对应范围。
- 仅当无法推断的选择会改变业务行为、权限、安全、生产操作或已批准决策时，提出一个必要问题；其他情况直接完成。
- 只报告实际执行的检查，并列出未验证项及原因。

## 完成标准

- 文档数量与项目规模相称，没有空壳或未替换的模板文本。
- 项目特定陈述都有证据、用户确认或“待确认”标记。
- `AGENTS.md` 与 `CLAUDE.md` 均能路由到适用规范，且通过 `cmp -s AGENTS.md CLAUDE.md` 验证内容完全一致。
- `sync`/`audit` 的每项候选影响都有结论，且报告真实覆盖范围。
