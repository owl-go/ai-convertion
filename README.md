# AI Project Conventions

可跨工具复用的工程 Harness skill，覆盖架构、代码、数据库、需求、测试、UI，连接规则、门禁、交付证据与长期维护。核心基线采用“通用基线＋技术栈补充＋项目约定”三层，当前版本见 [Harness 采用说明](references/harness.md)。

从代码、配置、测试、批准决策和 Git 变化中收集证据，按适用性创建最小文档集。实际工具入口优先；兼容双入口镜像只在已有约定或显式 `add agents` 时采用。

## 复用与工具适配

源码目录自包含。可将整个目录复制到目标工具实际配置的技能目录：

```bash
cp -R /path/to/ai-convertion /path/to/tool-skills/ai-project-conventions
```

只使用规范核心时，复制 `references/` 和 `assets/templates/`，并在项目实际入口加入按变更条件读取的路由。目标工具的技能发现/调用/重新加载依据其真实配置核实；复制不等于加载验证。可选 `scripts/` 使用 Python 3，`agents/openai.yaml` 仅为 Codex UI 适配。详见 [工具适配边界](references/tool-adapters.md)。

本机可安装到配置的个人技能目录（Codex 使用 `$CODEX_HOME/skills`，未设置时为 `~/.codex/skills`）；更新已有安装时核对差异并保留无关人工内容。

## 快速开始

在需要建立规范的项目中调用 skill；以下保留本机 Codex 的命名调用示例：

```text
$ai-project-conventions init
```

skill 会自动识别项目根目录、语言、技术栈、已有文档和真实工程命令，不要求预先填写长篇项目说明。

## 命令

### 初始化规范

```text
$ai-project-conventions init [path]
```

扫描项目并创建适合当前规模的最小规范体系。省略 `path` 时使用当前工作区。

### 同步规范

```text
$ai-project-conventions sync [git-ref]
```

根据需求/架构决策和代码变化建立文档影响清单，更新已授权权威来源、追踪与链接。指定 `git-ref` 时脚本使用 merge-base 到 HEAD 的已提交差异，加上暂存、未暂存和未跟踪路径：

```text
$ai-project-conventions sync origin/main
```

省略基线时检查当前工作区及用户提供的需求/决策变化，并说明覆盖范围。每项影响判定为已更新、不适用或待确认；需求→实现/测试证据保持可追踪，代码与批准需求冲突保留待决，旧 ADR 用取代关系保留历史。

### 审计规范

```text
$ai-project-conventions audit [git-ref]
```

只读检查文档漂移、冲突、缺口、失效命令、重复规则和待确认事项，不修改项目文件。

### 检测项目结构

```text
$ai-project-conventions check [path]
```

只读检查项目的依赖方向、模块划分、职责边界、变更局部性、耦合度、抽象层次、测试/构建和长期演进健康度，并按 0/3/5 评分表给出加权总分、证据和改进建议。代码质量专项覆盖单文件规模、dead code、代码风格、缺陷与潜在 Bug、安全漏洞、复杂度与可维护性、重复代码、测试覆盖和代码坏味道。该检测不会修改项目；启发式候选必须结合项目真实工具和人工检查确认。

### 增补单类文档

```text
$ai-project-conventions add <kind> [scope]
```

常用示例：

```text
$ai-project-conventions add adr
$ai-project-conventions add standard backend
$ai-project-conventions add runbook deployment
$ai-project-conventions add gates
```

支持的 `kind`：

| kind | 生成内容 |
|---|---|
| `agents` | 同时创建或更新 `AGENTS.md` 与 `CLAUDE.md` |
| `map` | 项目和模块职责地图 |
| `glossary` | 领域词汇表 |
| `architecture` | 当前架构与数据流 |
| `standard` | 带规则 ID 和验证方式的工程规范 |
| `gates` | 按变更类型组织的质量门禁 |
| `requirement` | 可验证的需求文档 |
| `design` | 技术方案 |
| `adr` | 架构决策记录 |
| `runbook` | 部署、回滚或事故处置手册 |
| `exception` | 临时规范例外记录 |
| `impact-map` | 变化类型到权威文档的回补映射 |
| `harness` | 三层规范采用、六类适用性与版本升级差异 |
| `profile` | 技术栈配置、规则实现与真实检查命令 |
| `database` | 当前数据模型与查询/事务依据 |
| `migration` | 一次迁移、旧数据/兼容与恢复计划 |
| `testing` | 风险驱动测试选择、隔离与结果 |
| `ui` | token/组件、状态/交互与视觉验收 |
| `task` | 进度、完成证据、失败恢复与交接 |

### 查看帮助

```text
$ai-project-conventions help
```

直接调用 `$ai-project-conventions` 而不带命令时：缺少 AI 规范的项目执行 `init`，已有规范的项目执行 `sync`。

## 生成结构

skill 会按需创建文件，不要求补齐所有目录。以下为采用兼容双入口时的例子；其他工具使用实际入口：

```text
AGENTS.md                  # AI 协作入口
CLAUDE.md                  # 与 AGENTS.md 完全一致
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

采用镜像约定时 `AGENTS.md` 是编辑源，`CLAUDE.md` 是逐字节镜像；独立作用域入口遵守已有项目配置。规范正文与实际架构、模型、需求、测试和 UI 产物分开，入口只保存短路由与必要约定。

## 更新 skill

将最终源文件更新到实际安装目录，先核对安装内的人工差异。技能更新不自动升级项目基线：先 `audit` 比较版本/规则 ID，按项目批准流程采用，`sync` 更新适用规则与门禁。无需对业务项目自动运行初始化。

## 工作原则

- 以当前代码、配置、测试和实际运行结果作为主要证据。
- 不猜测版本、命令、负责人、业务边界或生产流程。
- 只创建能够指导工作、可以验证且值得持续维护的文档。
- 保留项目已有规则和未提交改动，避免无关重写。
- 只有业务、安全、权限、生产操作或已批准决策无法安全推断时才询问用户。

## 项目内容

- [`SKILL.md`](SKILL.md)：命令入口与执行约束。
- [`references/document-system.md`](references/document-system.md)：文档选型和模板路由。
- [`references/maintenance-workflow.md`](references/maintenance-workflow.md)：持续审计与回补流程。
- [`references/baseline-rules.md`](references/baseline-rules.md)：通用安全、授权和质量基线。
- [`assets/templates/`](assets/templates/)：按需使用的文档模板。
- [`scripts/collect_project_evidence.py`](scripts/collect_project_evidence.py)：只读项目证据采集工具。
- [`scripts/check_project_health.py`](scripts/check_project_health.py)：只读项目结构、单文件规模和 dead code 信号采集工具。
- [`scripts/check_code_quality.py`](scripts/check_code_quality.py)：只读代码风格、缺陷、安全、复杂度、重复、覆盖率和坏味道信号采集工具。

- [references/harness.md](references/harness.md)：三层采用、版本和任务闭环。
- [references/tool-adapters.md](references/tool-adapters.md)：跨工具复用与入口适配。
