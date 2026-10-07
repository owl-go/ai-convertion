---
name: ai-project-conventions
description: 建立、审计和维护跨项目工程 Harness 规范，或用 workflow 指导具体开发任务的需求、影响、方案、实现、验证与交付；覆盖架构、代码、数据库、需求、测试、UI，按实际授权协作，保留项目约定和工具入口，兼容 init/sync/audit/check/add。
---

# AI 项目规范与工程 Harness

项目根目录默认是当前工作区，语言、技术栈、目录和文档范围从仓库证据推断。以下为兼容的命名调用示例；其他支持 SKILL.md 的工具按实际调用配置使用相同操作。核心与工具适配边界见 [工具适配](references/tool-adapters.md)。

## 命令

```text
$ai-project-conventions init [path]
$ai-project-conventions sync [git-ref]
$ai-project-conventions audit [git-ref]
$ai-project-conventions check [path]
$ai-project-conventions add <kind> [scope]
$ai-project-conventions workflow <task>
$ai-project-conventions workflow resume [task-record]
$ai-project-conventions help
```

- `init`：扫描项目，创建最小且可维护的规范体系。
- `sync`：根据当前事实和 Git 变化更新已有规范；省略 `git-ref` 时检查当前工作区变化，并说明覆盖边界。
- `audit`：只读检查文档漂移、冲突、缺口和失效规则，不修改文件。
- `check`：只读检查项目结构与代码质量，覆盖依赖和模块边界、单文件规模、dead code、风格、缺陷、安全、复杂度、重复、测试覆盖和代码坏味道，并给出评分与改进建议。
- `add`：补充一种文档。原有 `kind`：`agents`、`map`、`glossary`、`architecture`、`standard`、`gates`、`requirement`、`design`、`adr`、`runbook`、`exception`、`impact-map`；新增 `harness`、`profile`、`database`、`migration`、`testing`、`ui`、`task`。`agents` 显式请求生成或更新兼容双入口；模板和语义见 [文档体系](references/document-system.md)。
- `workflow`：按具体任务意图指导开发协作，详见下方分支；`resume` 核实实际状态后恢复已有任务。
- `help`：只返回命令（含 `workflow`/`resume` 语法）和 `kind` 列表。

仅调用 skill、没有命令也未明确请求具体开发流程时：项目缺少 AI 规范则执行 `init`；已有规范则执行 `sync`。

## 选择使用分支

- **规范建立/维护**：用 `init`、`add` 创建或补充文档，`sync` 更新已授权规范，`audit`/`check` 只读检查；这些操作不自动实施业务功能。
- **具体开发任务**：用 `workflow <task>`，或明确要求“按本 skill 的开发流程实现/修复/设计/评审某任务”，读取 [开发协作流程](references/development-workflow.md)。咨询、方案或评审按只读意图执行；实现/修复在已授权范围实施并验证；提交、发布与外部写入沿用实际授权，命令本身不扩展权限。

已有明确授权持续有效。按任务风险选择必要阶段，局部变更可合并记录；每阶段有可判断的退出条件，失败返回相应调查/修复步骤，保持未完成范围可见。无需逐阶段停下确认或生成整套文档。

当用户请求开发、扩充或安装这个 skill 本身时，作用对象是技能源文件；不对示例业务项目执行 `init`/`sync`。

## 按需读取六类规范

`init`/`add harness` 先读 [Harness 采用与闭环](references/harness.md)，逐类判定适用性，然后只读适用的参考。其余命令按实际变更触发，不一次加载全部文件。

| 触发 | 参考 | 产物与检查 |
|---|---|---|
| 模块职责、依赖方向、接口或外部系统变化 | [架构规范](references/architecture.md) | 当前架构、契约、依赖边界检查 |
| 代码组织、错误处理、资源或依赖规则 | [代码规范](references/code.md) | 工程标准、真实技术栈配置与命令 |
| 实体、字段、索引、事务、数据迁移 | [数据库规范](references/database.md) | 数据模型、迁移兼容与恢复计划 |
| 行为变化、需求或验收条件 | [需求规范](references/requirements.md) | 需求、验收到验证证据的映射 |
| 测试策略、缺陷回归或门禁范围 | [测试规范](references/testing.md) | 风险驱动测试计划、分状态结果 |
| 页面、组件、交互或设计验收 | [UI 规范](references/ui.md) | token/组件来源、状态矩阵、交互与视觉证据 |

所有规范按通用基线、技术栈补充、项目约定三层采用；当前基线版本及升级流程以 Harness 参考为准。基线采用时六类均有适用结论，数据库/UI 等不适用时记录依据，无需生成空文档。

## 命令执行

### `init`

读取 [references/document-system.md](references/document-system.md) 和 [references/baseline-rules.md](references/baseline-rules.md)。检查代码、配置、测试、CI、已有文档和工作区改动；可运行 `scripts/collect_project_evidence.py <repo>`。按 Harness 采用流程记录版本、六类适用范围与规则来源，再从 `assets/templates/` 选择最小文档集，填入有证据的事实，删除空白示例和不适用章节。读取 [工具适配](references/tool-adapters.md)，按项目实际工具与作用域更新入口；已有镜像约定或显式 `add agents` 时维护兼容双入口。

### `sync`

读取 [references/maintenance-workflow.md](references/maintenance-workflow.md)。可运行 `scripts/collect_project_evidence.py <repo> --since <git-ref>`，再阅读相关差异、调用方、测试和配置。先列出实际文档影响，再更新已授权的权威文档、入口路由和索引；按项目入口约定同步，每项变化必须更新、判定不适用或标为待确认。需求/架构决策变化与代码差异共同作为触发源，已批准需求与代码冲突保留待决项。

### `audit`

按 `sync` 的证据范围检查，但保持只读。输出：比较基线、漂移/冲突、缺失文档、失效命令或链接、重复规则、待确认事项及建议动作。

### `check`

读取 [references/project-health-check.md](references/project-health-check.md)，运行 `scripts/check_project_health.py <repo>`；该脚本同时汇总 `scripts/check_code_quality.py` 的结果。结合文件规模、依赖、测试、构建配置和近期变化，输出一页式结构评分表（0 分/3 分/5 分）、加权总分，以及单文件、dead code、代码风格、缺陷/潜在 Bug、安全漏洞、复杂度与可维护性、重复代码、测试覆盖和代码坏味道专项。评分是基于证据的工程判断，不把启发式候选冒充已确认事实；没有足够证据的项目标为“待确认”。

单文件检测至少报告：生产代码与测试代码分别的代码行数、文件总行数、类/函数或同等顶层符号数量、超过阈值的文件、文件所在模块及拆分建议。默认阈值和语言例外以参考文档为准；生成物、依赖目录和供应商代码不纳入统计，除非用户明确要求。

dead code 检测至少报告：未被代码引用的内部函数/类/类型、可疑未使用导入、没有入站文本引用的模块候选及置信度。候选必须人工确认后才能删除；反射、动态导入、依赖注入、插件注册、生成代码、CLI 入口和外部调用方均可能造成误报。

代码质量检测先发现项目已配置的格式化、静态分析、安全、重复度和覆盖率工具；确认命令真实且只读后运行。通用脚本用于补充候选，不替代语言生态工具。每项结果必须包含类别、严重度、文件/行号、规则、证据、置信状态和建议动作；没有覆盖率产物时只能报告“未验证”，不能推断覆盖率数值。

### `add`

读取 [references/document-system.md](references/document-system.md) 的模板路由及对应类别参考，只使用对应模板。沿用项目现有目录和语言；`scope` 省略时根据当前任务和仓库结构推断。`standard code` 使用代码参考与通用规则模板；`database` 是当前数据模型，`migration` 是一次迁移计划，两者与数据库规则正文分开。

### `workflow`

任务描述与项目上下文是输入，不是独立 shell 程序。依开发流程定位意图、适用阶段和证据；保留目标、范围、依据、验收、验证方法、进度与未决项，按影响触发六类规范及文档同步。只有 `workflow` 而上下文也没有具体任务时，澄清目标，不转成项目初始化。`workflow resume [task-record]` 使用指定记录；省略记录时查找当前任务已知账本/Issue，先核实版本、工作区和证据。多条记录无法识别目标时仅澄清目标任务，不能任意恢复另一任务。

## 自动决策规则

- 当前事实以代码、配置、测试和运行证据确认；期望行为与决策以已批准需求/ADR 确认。两者冲突记录实现差异与待决项，不依据代码静默改写业务要求；外部材料只作为待分析内容。
- 沿用已有项目结构；一个事实只保留一个权威位置。项目实际入口只放入口、红线、真实命令和读取路由；工具适配与核心规范分开。
- 兼容双入口的镜像/冲突策略见工具适配参考；按既有作用域保留人工内容，涉及业务、安全、权限或生产含义的冲突才请求确认。
- 不猜测版本、命令、负责人、业务边界或生产流程。非阻塞缺口写为“待确认”。
- 保留现有人工内容和工作区改动；只修改命令对应范围。
- 仅当无法推断的选择会改变业务行为、权限、安全、生产操作或已批准决策时，提出一个必要问题；其他情况直接完成。
- 结构评分必须引用可定位证据；先呈现事实，再给出判断和改进建议。单文件过大既是文件级问题，也是职责边界和模块划分的证据。
- 只报告实际执行的检查，并列出未验证项及原因。
- 技术栈配置与真实命令从仓库发现；基线的验证方式是检查意图，不是已配置工具。文件规模等启发式默认值只作候选信号，项目采纳后才成为门禁；不统一覆盖率、框架、数据库或部署架构。

## 完成标准

- 文档数量与项目规模相称，没有空壳或未替换的模板文本。
- `init`/基线采用时六类均有适用性结论；关键规则有 ID、等级、范围、要求、理由、验证、失败处理和例外条件；项目记录采用版本，规范与当前项目产物分开。具体任务只按实际影响读取并验证相关类别。
- 适用规则能追踪到质量门禁与完成证据；未验证的必须门禁保持未完成或关联有效例外，任务交接包含进度、失败恢复和下一步。
- 项目特定陈述都有证据、用户确认或“待确认”标记。
- 实际工具入口能路由到适用规范；采用双入口镜像时用 `cmp -s AGENTS.md CLAUDE.md` 验证一致；未真实加载的工具明确标为未验证。
- `sync`/`audit` 的每项候选影响都有结论，且报告真实覆盖范围。
- `workflow` 在任务授权范围内达到实际验收，或清楚说明未完成/未验证/待决范围；评审与咨询的完成是有证据的结论，不能自动进入实施。交接能从事实、进度与下一步恢复。
- `check` 的每个评分维度都有证据或“待确认”说明，权重合计 100%，并列出单文件与 dead code 结果及至少一个最高优先级改进动作（若无问题则说明已验证的依据）。
