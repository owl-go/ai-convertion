# AI Project Conventions

为软件项目初始化、审计和持续回补 AI 协作规范的 Codex skill。

它会从当前代码、配置、测试、CI 和 Git 变化中收集证据，按项目规模创建最小文档集，并保持根目录的 `AGENTS.md` 与 `CLAUDE.md` 内容完全一致。详细规范默认放在 `docs/` 下。

## 安装

Codex 会从用户级 `~/.agents/skills` 和项目级 `.agents/skills` 目录发现 skill。安装后若未出现，可重启 Codex。

### 用户级安装

适合在所有项目中使用：

```bash
mkdir -p ~/.agents/skills
git clone https://github.com/owl-go/ai-convertion.git \
  ~/.agents/skills/ai-project-conventions
```

### 本地开发软链接

已经克隆本仓库时，可以链接到用户级 skill 目录：

```bash
mkdir -p ~/.agents/skills
ln -s /path/to/ai-convertion ~/.agents/skills/ai-project-conventions
```

Codex 官方安装与发现规则见 [Build skills](https://learn.chatgpt.com/docs/build-skills)。

## 快速开始

在需要建立规范的项目中启动 Codex，然后执行：

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

根据代码、配置和 Git 变化回补已有文档。指定 `git-ref` 时以该引用为比较基线：

```text
$ai-project-conventions sync origin/main
```

省略基线时检查当前工作区变化，并在结果中说明覆盖范围。

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

### 查看帮助

```text
$ai-project-conventions help
```

直接调用 `$ai-project-conventions` 而不带命令时：缺少 AI 规范的项目执行 `init`，已有规范的项目执行 `sync`。

## 生成结构

skill 会按需创建文件，不要求补齐所有目录。典型结构如下：

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

`AGENTS.md` 是入口编辑源，`CLAUDE.md` 是逐字节镜像。详细规则只在 `docs/` 中维护，入口文件保存项目边界、红线、真实命令和文档路由。

## 更新 skill

通过 Git 克隆安装时，可以运行：

```bash
git -C ~/.agents/skills/ai-project-conventions pull --ff-only
```

通过软链接安装时，只需在本仓库拉取最新版本。

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
