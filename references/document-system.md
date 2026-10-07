# 文档体系与选型

只在内容有权威来源、能改变后续工作且可维护时创建长期文档。一个小型单体项目通常只需要实际工具入口、项目地图和质量门禁；复杂度出现后再拆分。

## 选型矩阵

| 文档 | 创建触发条件 | 权威内容 | 不应承载 |
|---|---|---|---|
| `AGENTS.md`/`CLAUDE.md` | 已有相应工具入口或显式 add agents；镜像仅按采用约定 | 项目边界、入口、红线、真实命令、文档路由、目录作用域 | 完整架构说明、重复的语言教程、长检查表 |
| 项目地图 | 多个模块/服务，目录职责不直观 | 模块职责、入口、依赖方向、所有者角色 | 文件清单式目录树 |
| 领域词汇 | 业务术语存在歧义或多个子域 | 统一术语、含义、边界、禁用近义词 | 通用技术名词解释 |
| 架构说明 | 关键边界、数据流或外部系统需要解释 | 当前架构、依赖方向、数据流、一致性边界 | 尚未批准的目标设计 |
| 工程标准 | 某类变化有项目特有约束 | 带 ID 的规则、范围、理由、验证与例外 | 可从格式化器或配置直接查到的默认值全集 |
| 质量门禁 | 项目有多种变更类型或多层检查 | 变更类型到真实检查命令/人工门禁的映射 | 未配置、未验证的理想化命令 |
| 需求 | 行为变化需要跨人/跨阶段确认 | 目标、范围、业务规则、边界和验收条件 | 实现细节堆积 |
| 技术方案 | 跨模块、接口/数据/权限/基础设施或复杂迁移 | 现状证据、方案、数据流、失败处理、验证与恢复 | 已被 ADR 替代的长期决策依据 |
| ADR | 已批准且需要长期解释的架构决策 | 决策、上下文、备选、后果和替代条件 | 仍未决定的方案讨论 |
| 运维手册 | 存在部署、回滚、迁移或事故职责 | 前置条件、验证、观察、恢复和授权边界 | 未演练的生产命令冒充既定流程 |
| 例外记录 | 必须临时偏离一条可识别规则 | 规则 ID、风险、补偿、批准、失效和跟踪项 | 无期限 TODO |
| 文档影响图 | 文档超过三份或经常漂移 | 变化类型、权威文档、联动文档、验证和责任角色 | 复制每份文档的正文 |
| 基线采用记录 | 项目采用/升级通用规范 | 版本、六类适用性、三层来源、升级差异与例外 | 当前业务事实全集 |
| 技术栈补充 | 通用规则需要绑定具体实现/工具 | 规则到配置/命令的映射、验证结果和盲区 | 重复配置中的默认值 |
| 数据模型/迁移计划 | 持久化语义或数据变更 | 当前模型语义/一次迁移与恢复 | 通用数据库规则正文 |
| 测试策略/UI 规格 | 验证策略或页面/交互需要跨阶段维护 | 风险与验证选择/状态与设计验收 | 通用测试/UI 规则正文 |
| 任务账本 | 长期/跨阶段任务或复杂失败恢复 | 进度、AC/规则/门禁证据、失败与交接 | 永久规范正文 |

## 默认结构

按需取用，不要求补齐所有目录。下列为采用兼容双入口的例子；其他工具沿用实际入口：

```text
AGENTS.md
CLAUDE.md
docs/
|-- project-map.md
|-- domain-glossary.md
|-- architecture.md
|-- requirements/
|-- designs/
|-- adr/
|-- standards/
|   |-- engineering.md
|   |-- security.md
|   `-- quality-gates.md
`-- operations/
    |-- deployment.md
    |-- rollback.md
    `-- incident-response.md
```

已有文档结构优先。调整目录只有在现状无法形成清楚的权威边界时才有价值。

## 模板路由

模板位于 `assets/templates/`，按本次文档类型读取：

| 任务 | 模板 |
|---|---|
| 实际工具入口 / `agents` | [project-instructions.md](../assets/templates/project-instructions.md)；双入口兼容用 [AGENTS.md](../assets/templates/AGENTS.md) |
| 模块职责与术语 | [project-map.md](../assets/templates/project-map.md)、[domain-glossary.md](../assets/templates/domain-glossary.md) |
| 当前架构与工程规则 | [architecture.md](../assets/templates/architecture.md)、[standard.md](../assets/templates/standard.md) |
| 质量门禁 | [quality-gates.md](../assets/templates/quality-gates.md) |
| 需求、方案与决策 | [requirement.md](../assets/templates/requirement.md)、[technical-design.md](../assets/templates/technical-design.md)、[adr.md](../assets/templates/adr.md) |
| 运维、规范例外 | [operations-runbook.md](../assets/templates/operations-runbook.md)、[exception.md](../assets/templates/exception.md) |
| 持续回补 / `impact-map` | [document-impact-map.md](../assets/templates/document-impact-map.md) |
| 三层规范采用 / `harness` | [harness-adoption.md](../assets/templates/harness-adoption.md) |
| 技术栈补充 / `profile` | [stack-profile.md](../assets/templates/stack-profile.md) |
| 当前数据模型 / `database` | [database-model.md](../assets/templates/database-model.md) |
| 一次迁移 / `migration` | [migration-plan.md](../assets/templates/migration-plan.md) |
| 测试策略 / `testing` | [test-strategy.md](../assets/templates/test-strategy.md) |
| UI 规格与验收 / `ui` | [ui-spec.md](../assets/templates/ui-spec.md) |
| 任务与交接 / `task` | [task-evidence.md](../assets/templates/task-evidence.md) |

模板是待裁剪的输出骨架，不是项目事实。空白字段、示例行和不适用章节不能进入最终活动文档。

## 工具入口与路由

读取 [工具适配](tool-adapters.md)。按项目实际工具维护短入口；双入口镜像仅在已有约定或显式 `add agents` 时采用。模板路径和规范引用必须对应项目真实文件。

入口的条件路由覆盖六类变化，写明触发条件与目标权威路径；如模块边界→架构、数据结构/迁移→数据库、行为变化→需求/验收、验证/回归→测试、页面/交互→UI。详细规则在项目规范正文中维护。

## 规则记录

关键规则必须包含 ID、等级、范围、要求、理由、验证、失败处理和例外条件；沿用同等完整的项目格式。示例结构：

```yaml
id: SEC-001
level: MUST
scope: all
rule: 日志和持久化产物不得包含凭证
rationale: 凭证泄露会造成越权访问
verification:
  - secret-scan
  - focused-test
on-failure: block
exception: forbidden
owner: security-role
```

级别含义：

- `MUST`：安全、权限、正确性或明确交付要求；违反即阻断或进入例外流程。
- `SHOULD`：默认路径；偏离需要记录理由、影响和补偿。
- `MAY`：可选做法；不作为检查失败条件。

## 元数据与生命周期

长期文档采用项目支持的元数据格式。下面是模板示例，负责人、状态、复查周期须按项目证据填写或删除；文档版本与采用的通用基线版本分开：

```yaml
version: 1.0
status: active
owner: engineering
last-reviewed: YYYY-MM-DD
review-cycle: quarterly
```

文档进入以下任一状态时应处理：

- `active`：当前权威依据。
- `draft`：尚未批准，不得描述为现行规则。
- `superseded`：保留历史，必须指向替代文档。
- `retired`：不再适用；从活动路由中移除。

## 已有专项参考

仅在任务明确涉及跨境 SEO/GEO 增长工作流时，可读 [既有增长工作流参考](cross-border-seo-geo-growth-workflow.md)。这是项目专项示例，不属于通用六类基线，技术事实在采用时重新核实。
