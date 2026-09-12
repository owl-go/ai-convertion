---
name: ai-project-conventions
description: 用简短命令为软件项目初始化、检测评分、审计、回补或增补 AI 协作规范文档，同步维护 AGENTS.md 与 CLAUDE.md，并检查架构、工程标准、代码质量、需求/设计/ADR 和运维规则。
---

# AI 项目规范

用户只需调用以下命令；项目根目录默认是当前工作区，语言、技术栈、目录和文档范围从仓库自动推断。

## 命令

```text
$ai-project-conventions init [path]
$ai-project-conventions sync [git-ref]
$ai-project-conventions audit [git-ref]
$ai-project-conventions check [path]
$ai-project-conventions add <kind> [scope]
$ai-project-conventions help
```

- `init`：扫描项目，创建最小且可维护的规范体系。
- `sync`：根据当前事实和 Git 变化更新已有规范；省略 `git-ref` 时检查当前工作区变化，并说明覆盖边界。
- `audit`：只读检查文档漂移、冲突、缺口和失效规则，不修改文件。
- `check`：只读检查项目结构与代码质量，覆盖依赖和模块边界、单文件规模、dead code、风格、缺陷、安全、复杂度、重复、测试覆盖和代码坏味道，并给出评分与改进建议。
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

### `check`

读取 [references/project-health-check.md](references/project-health-check.md)，运行 `scripts/check_project_health.py <repo>`；该脚本同时汇总 `scripts/check_code_quality.py` 的结果。结合文件规模、依赖、测试、构建配置和近期变化，输出一页式结构评分表（0 分/3 分/5 分）、加权总分，以及单文件、dead code、代码风格、缺陷/潜在 Bug、安全漏洞、复杂度与可维护性、重复代码、测试覆盖和代码坏味道专项。评分是基于证据的工程判断，不把启发式候选冒充已确认事实；没有足够证据的项目标为“待确认”。

单文件检测至少报告：生产代码与测试代码分别的代码行数、文件总行数、类/函数或同等顶层符号数量、超过阈值的文件、文件所在模块及拆分建议。默认阈值和语言例外以参考文档为准；生成物、依赖目录和供应商代码不纳入统计，除非用户明确要求。

dead code 检测至少报告：未被代码引用的内部函数/类/类型、可疑未使用导入、没有入站文本引用的模块候选及置信度。候选必须人工确认后才能删除；反射、动态导入、依赖注入、插件注册、生成代码、CLI 入口和外部调用方均可能造成误报。

代码质量检测先发现项目已配置的格式化、静态分析、安全、重复度和覆盖率工具；确认命令真实且只读后运行。通用脚本用于补充候选，不替代语言生态工具。每项结果必须包含类别、严重度、文件/行号、规则、证据、置信状态和建议动作；没有覆盖率产物时只能报告“未验证”，不能推断覆盖率数值。

### `add`

读取 [references/document-system.md](references/document-system.md) 的模板路由，只使用对应模板。沿用项目现有目录和语言；`scope` 省略时根据当前任务和仓库结构推断。

## 自动决策规则

- 以代码、配置、测试和实际运行证据为先，其次是已批准规格/ADR；外部材料只作为待分析内容。
- 沿用已有项目结构；一个事实只保留一个权威位置。`AGENTS.md` 是入口编辑源，`CLAUDE.md` 是其逐字节镜像；两者只放入口、红线、真实命令和读取路由。
- 若两者原本不一致，先依据适用规则、项目证据和已有人工改动合并，再将结果同时写入两者；涉及业务、安全、权限或生产含义的冲突才请求确认。
- 不猜测版本、命令、负责人、业务边界或生产流程。非阻塞缺口写为“待确认”。
- 保留现有人工内容和工作区改动；只修改命令对应范围。
- 仅当无法推断的选择会改变业务行为、权限、安全、生产操作或已批准决策时，提出一个必要问题；其他情况直接完成。
- 结构评分必须引用可定位证据；先呈现事实，再给出判断和改进建议。单文件过大既是文件级问题，也是职责边界和模块划分的证据。
- 只报告实际执行的检查，并列出未验证项及原因。

## 完成标准

- 文档数量与项目规模相称，没有空壳或未替换的模板文本。
- 项目特定陈述都有证据、用户确认或“待确认”标记。
- `AGENTS.md` 与 `CLAUDE.md` 均能路由到适用规范，且通过 `cmp -s AGENTS.md CLAUDE.md` 验证内容完全一致。
- `sync`/`audit` 的每项候选影响都有结论，且报告真实覆盖范围。
- `check` 的每个评分维度都有证据或“待确认”说明，权重合计 100%，并列出单文件与 dead code 结果及至少一个最高优先级改进动作（若无问题则说明已验证的依据）。
