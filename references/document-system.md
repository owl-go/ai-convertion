# 项目文件生成契约

`init` 的默认产物是一个实际工具入口和项目适用的具体规范文件。生成由代理依据下面的路由和模板执行；本包没有独立的文件生成 CLI。先读配置、代码、测试、已有文档，复用现有权威路径，不能仅复制模板或列出拟建文件就报告完成。

## 默认输出与模板路由

以下路径用于没有既有约定的项目；有约定时映射到现有路径，保持内容边界。

| 输出 | 何时生成 / 权威内容 | 模板 |
|---|---|---|
| `AGENTS.md` **或** `CLAUDE.md` | 按实际工具选一个；全景、架构铁律、真实技术栈、代码目录归属、命令、条件读取 | [project-instructions.md](../assets/templates/project-instructions.md)；已有双入口约定使用 [AGENTS.md](../assets/templates/AGENTS.md) |
| `docs/conventions/directory-structure.md` | 代码/配置/测试/迁移/需求/方案归属、依赖方向、新模块落位、正反例与检查；入口保留概要树并链接此处 | [directory-standard.md](../assets/templates/directory-standard.md) |
| 服务子入口（沿用项目作用域） | 有独立职责/构建/数据/外部依赖/定时任务/特有约定时；引用根入口 | [service-instructions.md](../assets/templates/service-instructions.md) |
| `docs/conventions/<语言>-standards.md` | 有业务代码；实际语言的命名、类型、错误、资源、并发、依赖、格式与检查 | [language-standard.md](../assets/templates/language-standard.md) |
| `docs/conventions/frontend-standards.md` | 有前端工程；组件/路由/状态/API/构建边界与代码落位 | [frontend-standard.md](../assets/templates/frontend-standard.md) |
| `docs/conventions/ui-standards.md` | 有页面/交互；组件与 token 来源、交互状态、布局与视觉验收 | [ui-standard.md](../assets/templates/ui-standard.md) |
| `docs/conventions/database-standards.md` | 有持久化数据；模型命名、约束、索引、事务、迁移与恢复规则 | [database-standard.md](../assets/templates/database-standard.md) |
| `docs/conventions/requirement-standards.md` | 有行为需求；如何写范围、规则、边界与可验证验收 | [requirements-standard.md](../assets/templates/requirements-standard.md) |
| `docs/conventions/technical-design-standards.md` | 如何记录实现方案；按复杂度选择短方案或独立设计，必答问题 | [technical-design-standard.md](../assets/templates/technical-design-standard.md) |
| `docs/conventions/testing-standards.md` | 有代码；测试位置、边界、隔离、回归选择与真实命令 | [testing-standard.md](../assets/templates/testing-standard.md) |
| `docs/requirements/<topic>.md` | 本次确有需求要记录；具体目标、业务规则、AC 和修订 | [requirement.md](../assets/templates/requirement.md) |
| `docs/designs/<topic>.md` | 本次需要独立方案；具体路径、契约、失败处理、兼容与验证 | [technical-design.md](../assets/templates/technical-design.md) |

所有 `conventions` 文件是**规则**；`requirements/`、`designs/` 是**具体产物**，没有具体任务不生成示例需求/方案。多语言项目按需拆成 `go-standards.md`、`java-standards.md` 等，入口按路径条件读取，避免让无关栈规则进入上下文。架构规则默认在入口；复杂架构现有说明可链接，但入口仍包含明确铁律。

### `init` 必须执行的生成步骤

1. 确定有效入口及作用域：沿用项目工具证据；只生成所用工具的一个入口。工具未知时使用工具中立 `PROJECT-CONVENTIONS.md` 暂存完整入口内容，标记接入待确认；不猜测客户端。双入口仅有已有约定或明确要求时同步。
2. 从清单/锁文件/构建与 CI 配置提取实际栈、版本口径、启动和检查命令；阅读关键入口、模块调用、测试与已有约定，写出项目全景和依赖边界。
3. 用入口模板写完整内容。目录树列出**全部受维护代码与文件类别的归属**：每个目录职责、允许文件类型、新模块放置点、测试/配置/脚本/文档/生成物位置。现状与期望不同，分别标明，不把尚未迁移的树描述为现状；未经授权不重排业务代码。
4. 逐项判断上表规范是否适用，在入口路由说明依据；从对应模板写成项目规则，绑定真实路径、配置、合理短例及检查方式。删除不适用段落、空值和教学提示；未知关键事实明确待确认，不能编造。
5. 路由只指向实际存在的权威文件。逐条核对目录归属、依赖规则、示例与真实代码是否相符，核实命令来源；执行已授权的适当检查，报告执行/未执行状态。生成后交付实际文件清单及未决项。

不默认生成项目地图、质量门禁、采用记录、影响图、任务账本或 eval 文件。采用版本及适用性可用入口中的简短说明；脚本或 CI 已维护的检查直接引用。规范以可执行条目、短例和验证为主体，不要求给每条规则填八字段元数据表。

## 输出长什么样

文件位置示意（目录和栈仅说明写法；生成时以目标项目事实替换）：

```text
AGENTS.md
cmd/api/                         # 服务启动/组装
internal/order/                  # 订单规则与用例
internal/transport/http/         # HTTP 输入/响应适配
internal/storage/postgres/       # 持久化适配
web/src/{pages,components,api}/   # 页面、公共组件、网络适配
migrations/                      # 有序数据库迁移
scripts/                         # 开发/检查脚本
docs/
  conventions/
    directory-structure.md
    <语言>-standards.md
    frontend-standards.md
    ui-standards.md
    database-standards.md
    requirement-standards.md
    technical-design-standards.md
    testing-standards.md
  requirements/                  # 有需求时才新增文件
  designs/                       # 有独立方案时才新增文件
```

完整填好的入口、适用规则、具体需求/方案和原始代码见 [generated-example.md](generated-example.md)。示例不作为新项目默认栈；真实生成结果由项目证据决定。

## 可选 `add` 兼容路由

原有 kind 均保留，不由 `init` 自动补齐。`standard <scope>` 优先用上表对应规则模板（`directory` 对应目录规则，`code` 对应语言规则，`design` 对应方案规则）；未知专项才用 [standard.md](../assets/templates/standard.md)。`add agents` 默认更新实际入口，不能仅凭此命令推断要求双入口。

| kind | 模板 / 用途 |
|---|---|
| `architecture` | [architecture.md](../assets/templates/architecture.md)：复杂当前架构，与入口铁律互相链接 |
| `adr` | [adr.md](../assets/templates/adr.md)：长期决策历史 |
| `requirement` / `design` | 上表具体产物模板 |
| `project-map` / `map` / `glossary` | [project-map.md](../assets/templates/project-map.md)、[domain-glossary.md](../assets/templates/domain-glossary.md) |
| `exception` / `runbook` | [exception.md](../assets/templates/exception.md)、[operations-runbook.md](../assets/templates/operations-runbook.md) |
| `gates` / `impact-map` | [quality-gates.md](../assets/templates/quality-gates.md)、[document-impact-map.md](../assets/templates/document-impact-map.md) |
| `harness` / `profile` | [harness-adoption.md](../assets/templates/harness-adoption.md)、[stack-profile.md](../assets/templates/stack-profile.md) |
| `database` / `migration` | [database-model.md](../assets/templates/database-model.md)、[migration-plan.md](../assets/templates/migration-plan.md)：模型与一次迁移，分开于数据库规则 |
| `testing` / `ui` | [test-strategy.md](../assets/templates/test-strategy.md)、[ui-spec.md](../assets/templates/ui-spec.md)：具体策略/页面规格 |
| `task` | [task-evidence.md](../assets/templates/task-evidence.md)：确有交接需要时使用 |

## 更新与历史

入口和规则描述现行约定；未实现设计明确“计划”，验证结果明确“已实现/已验证/未验证”。需求 AC 与 ADR 保留可追踪修订；被替代的 ADR 指向新决策，不篡改历史。使用项目已有状态格式，不强加 owner、review-cycle、指标或版本账本。明确用户新要求可以修订旧规范；仍有效要求与代码的冲突必须显式报告。

仅在涉及跨境 SEO/GEO 专项时读取 [增长工作流参考](cross-border-seo-geo-growth-workflow.md)。
