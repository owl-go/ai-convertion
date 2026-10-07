# AI Project Conventions

把项目工程约定写成 AI 能直接使用的文件：一个完整项目入口，加少量具体规范。入口包含项目全景、架构铁律、真实技术栈、权威代码目录与文件归属、运行检查命令和条件读取；规范以行动条目、短例和实际检查为主体。

对外介绍见 [公众号文章稿](docs/wechat-harness-skill.md)；已填入口与生成目录见 [教学示例](references/generated-example.md) 和 [默认文件契约](references/document-system.md)。教学示例不代表当前仓库事实。

## 快速使用

在目标项目调用（下面是支持命名调用的代理语法示例，并非独立 CLI）：

```text
$ai-project-conventions init
$ai-project-conventions sync origin/main
$ai-project-conventions audit origin/main
$ai-project-conventions check
```

`init [path]` 从代码/配置/测试/CI 和已有需求读取证据，真正创建或合并适用文件；省略路径用当前工作区。按实际工具选择 `AGENTS.md` **或** `CLAUDE.md`，不默认两份；未知工具使用完整中立入口并标记接入待确认。保留既有人工约定和工作区改动。

`sync [git-ref]` 更新实际受影响的入口段落、规则或具体需求/设计。指定 ref 的证据脚本比较 `<ref>...HEAD`，并纳入暂存/未暂存/未跟踪路径；无 ref 则说明当前范围及历史盲区。需求/决策变化也是输入。明确新要求可修订旧规范；当前/计划、实施/验证分开，AC/ADR 历史与冲突保持可见。

`audit [git-ref]` 只读核对事实、目录归属、规范、链接、命令与需求实现差异；`check [path]` 只读检查结构和质量，报告证据、评分、单文件规模及 dead code 候选。候选需确认后才可删除。

## 默认生成内容

假设带前端和数据库的项目（按真实适用性裁剪，不创建空文件）：

```text
AGENTS.md                     # 或 CLAUDE.md，实际工具入口
docs/
  conventions/
    language.md               # 语言、错误、资源、并发、依赖与检查
    frontend.md               # 组件/路由/状态/请求/构建边界
    ui.md                     # 组件/token、交互状态、视觉验收
    database.md               # 模型、约束、查询、事务、迁移规则
    requirements.md           # 需求与 AC 怎样写
    technical-design.md       # 实现方案怎样写
    testing.md                # 测试位置、选择、隔离与真实命令
  requirements/               # 有具体需求时新增文件
  designs/                    # 有具体方案时新增文件
```

多语言按目录拆语言文件；无前端/数据库不生成相应规则。已有权威文档优先复用路径。入口是项目事实与架构/目录约定的权威位置；具体规范不是入口的重复全文，需求与方案产物不是规范的副本。不默认生成地图、门禁、采用记录、影响图、任务账本或 eval 文件。

所有项目新增代码和文件遵循入口树与归属表：业务模块、启动、适配、前端、测试、配置、脚本、文档、生成物都要有位置；新增模块时同步树。实际目录与批准目标不同分别记录，不能把未迁移的目录说成现状。

## 补充类型与可选辅助

```text
$ai-project-conventions add <kind> [scope]
$ai-project-conventions help
```

| kind | 内容 |
|---|---|
| `agents` | 补充实际入口；双入口仅按既有约定或明确要求 |
| `standard` | 具体规则；scope 可用 code/language/frontend/ui/database/requirements/technical-design/testing 等 |
| `requirement` / `design` | 一次具体需求/方案 |
| `architecture` / `map` / `glossary` | 确需单独维护的架构/模块地图/术语 |
| `adr` / `runbook` / `exception` | 决策历史/运行恢复/明确例外 |
| `gates` / `impact-map` / `harness` / `profile` | 明确需要时的检查映射/影响图/采用记录/栈补充 |
| `database` / `migration` | 当前模型/一次迁移，区别于数据库规则 |
| `testing` / `ui` / `task` | 具体测试策略/页面规格/交接记录 |

日常只需先读入口再提出需求；需要协作辅助时可用 `workflow <task>` / `workflow resume [record]`。辅助流程见 [development-workflow.md](references/development-workflow.md)，不作为默认阶段/账本系统。只调用 skill 且未明确任务时，缺规范执行 init，已有规范执行 sync。实现、提交、发布分别沿任务实际授权。

## 安装与跨工具复用

整个目录自包含，可复制到目标工具实际配置的技能目录：

```bash
cp -R /path/to/ai-convertion /path/to/tool-skills/ai-project-conventions
```

目标工具的发现/调用/重载方式依其真实配置核实；复制不是加载验证。核心是 `SKILL.md`、`references/`、`assets/templates/`，辅助 `scripts/` 用 Python 3，`agents/openai.yaml` 仅为客户端 UI 适配。仅复用规范时可携带 references 与 templates，并在项目入口接入。详见 [工具适配](references/tool-adapters.md)。

本机个人技能目录按实际配置选择；更新前核对并保留无关人工差异。通用基线为 **3.0.0**：默认完整入口与具体规范替代旧的短索引和附加记录集合，六类 32 个稳定规则 ID 保留；[采用/升级说明](references/harness.md)。安装更新不会自动升级业务项目。

## 资源

- [SKILL.md](SKILL.md)：执行契约与命令。
- [文件契约与全部模板路由](references/document-system.md)：生成什么、何时生成、如何填写。
- [维护映射](references/maintenance-workflow.md)：变化具体更新哪个文件。
- [语言落地](references/language-profiles.md)：Go / Java 的配置、短例与检查依据。
- [证据采集](scripts/collect_project_evidence.py)、[结构检查](scripts/check_project_health.py)、[质量检查](scripts/check_code_quality.py)：可选只读辅助；不代替项目实际工具。
