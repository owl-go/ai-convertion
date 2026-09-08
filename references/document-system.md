# 文档体系与选型

只在内容有权威来源、能改变后续工作且可维护时创建长期文档。一个小型单体项目通常只需要同步入口 `AGENTS.md`/`CLAUDE.md`、项目地图和质量门禁；复杂度出现后再拆分。

## 选型矩阵

| 文档 | 创建触发条件 | 权威内容 | 不应承载 |
|---|---|---|---|
| `AGENTS.md`/`CLAUDE.md` | 任何长期使用 AI 的项目；两文件内容完全相同 | 项目边界、入口、红线、真实命令、文档路由、目录作用域 | 完整架构说明、重复的语言教程、长检查表 |
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

## 默认结构

按需取用，不要求补齐所有目录：

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
| 项目入口与 AI 指引 | `AGENTS.md` 模板；同一结果同时写入 `AGENTS.md` 与 `CLAUDE.md` |
| 模块职责与术语 | `project-map.md`、`domain-glossary.md` |
| 当前架构与工程规则 | `architecture.md`、`standard.md` |
| 质量门禁 | `quality-gates.md` |
| 需求、方案与决策 | `requirement.md`、`technical-design.md`、`adr.md` |
| 运维、规范例外 | `operations-runbook.md`、`exception.md` |
| 持续回补 | `document-impact-map.md` |

模板是待裁剪的输出骨架，不是项目事实。空白字段、示例行和不适用章节不能进入最终活动文档。

## `AGENTS.md`/`CLAUDE.md` 的同步与路由职责

以 `AGENTS.md` 为编辑源，`CLAUDE.md` 为逐字节镜像。初始化、回补和 `add agents` 都同时写入两者，完成前运行 `cmp -s AGENTS.md CLAUDE.md`。若原文件内容不同，先保留并合并有证据的人工规则，再同步结果，不以任一文件静默覆盖另一文件。

两者保持短小，并为每个指针写明读取条件。例如：

```markdown
- 修改公共 API、事件或兼容策略前，阅读 `docs/standards/api.md`。
- 涉及模块边界、数据流或新依赖时，阅读 `docs/architecture.md` 和适用 ADR。
- 发布、迁移或生产恢复任务，阅读 `docs/operations/` 下对应手册并遵守人工授权门禁。
```

弱指针如“更多信息见 docs”不能可靠触发读取。指针应包含分支触发词，同时避免复制目标文档内容。

## 规则记录

长期强制规则建议使用以下结构；项目已有格式时沿用：

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

长期文档采用项目支持的元数据格式。没有既有约定时可使用：

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
