---
name: ai-project-conventions
description: 为项目建立、审计和持续更新具体工程规范文件；入口包含项目全景、架构铁律、真实技术栈、代码目录归属与命令，按需生成语言、前端、UI、数据库、需求、技术方案、测试规范；支持 init/sync/audit/check/add，workflow/resume 为可选开发辅助。
---

# AI 项目规范

从当前仓库的代码、配置、测试、CI 和有效需求建立能直接指导编码的项目文件；不要求用户先填长篇说明。入口写项目事实与目录归属，具体规范写行动规则、短例和检查。核心不依赖特定代理 API 或安装路径，见 [工具适配](references/tool-adapters.md)。

## 默认用法

首次执行 `init`；日常开发先读项目实际入口，再按任务条件读取具体规范。项目变化后 `sync`，只读审计用 `audit`，结构/质量检查用 `check`。`workflow` / `resume` 是可选辅助，不要求每次任务走阶段框架或保存账本。

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

这些是向代理传达的操作，不是本包独立 CLI；其他工具使用实际调用语法。`kind` 保持兼容：agents、project-map、glossary、architecture、standard、adr、design、requirement、runbook、exception、impact-map、harness、profile、database、migration、testing、ui、task；`standard` 可指定 language/code/frontend/ui/database/requirements/technical-design/testing 等范围。`help` 只列命令与 kind。

仅调用 skill、未给命令或具体开发意图：没有规范则 `init`，已有规范则 `sync`。维护命令不自动实施业务功能。用户要求开发/安装此 skill 本身时修改技能源文件，不初始化示例业务项目。

## 按实际任务读参考

| 变化 | 参考 | 项目权威位置 |
|---|---|---|
| 模块职责、依赖、契约、目录/栈 | [架构](references/architecture.md)、[代码](references/code.md) | 入口全景、铁律、栈、目录与命令 |
| 语言、错误/资源/并发/依赖 | [代码](references/code.md)、[语言落地](references/language-profiles.md) | language 规范 |
| 前端组件/路由/状态/请求/构建 | [前端](references/frontend.md) | frontend 规范 |
| 页面、视觉、交互、可访问性 | [UI](references/ui.md) | ui 规范与具体页面规格 |
| 模型/查询/事务/迁移 | [数据库](references/database.md) | database 规范及具体模型/迁移 |
| 业务行为、验收 | [需求](references/requirements.md) | requirements 规范及该任务需求 |
| 实现方案、跨模块契约 | [架构](references/architecture.md) | technical-design 规范及具体设计/ADR |
| 测试、回归、验证命令 | [测试](references/testing.md) | testing 规范与真实配置/结果 |

六类通用基线保留稳定规则 ID，作为选择依据；前端工程与语言落地是具体补充。采用三层来源与版本说明见 [Harness 参考](references/harness.md)，不强制生成独立采用记录或把完整元数据表搬到项目。

## 执行契约

### `init`

必须读 [默认输出与模板路由](references/document-system.md)、[通用边界](references/baseline-rules.md)、[工具适配](references/tool-adapters.md)，按生成步骤真正创建/合并文件。检查现有文档与未提交改动，可用 `scripts/collect_project_evidence.py <repo>` 收集线索，再阅读相关源码。

- 按实际工具创建 `AGENTS.md` **或** `CLAUDE.md`，沿用现有入口；未知工具按中立入口回退。默认不创建双入口。
- 入口必须有项目用途/业务边界/模块系统关系、允许与禁止依赖和实现边界、真实技术栈及证据、权威目录树与全部受维护文件类别归属、新模块落位、真实命令及验证状态、条件读取。
- 按适用性生成语言、前端、UI、数据库、需求、技术方案、测试规范；复用已有权威路径。每份以直接规则、合理短例、真实检查为主体，未知信息标待确认，无 UI/数据库不建空文件。
- 规范写法与具体需求/设计产物分开；本次没有具体需求/方案，不生成虚构业务文档。默认不生成 project-map/gates/adoption/impact-map/task/eval 文件。
- 核对实际生成文件、目录归属、链接、命令及适用性，删除未填模板提示，交付路径和未验证项。填好的教学入口见 [示例](references/generated-example.md)，不是当前项目事实。

### `sync`

读 [维护映射与步骤](references/maintenance-workflow.md)。可运行 `scripts/collect_project_evidence.py <repo> --since <git-ref>`，阅读差异、调用方、测试、配置及用户需求变化。目录/架构/栈/命令变化更新入口对应段落；语言、前端、UI、数据库、需求、设计、测试变化更新对应权威规则或具体产物及链接。

明确新用户要求作为合法修订依据，不能因旧文档不同永久等待；代码偏离仍有效要求则显式报告。区分当前/计划、已实现/已验证；旧 ADR/AC 修订保留关联。每项候选影响给已更新/不适用/待确认结论，无需新建影响图或任务账本。

### `audit`

按 `sync` 范围只读核对：入口事实/目录归属与代码是否相符，规范是否可执行，需求/设计与实现是否冲突，路径/命令是否有效；输出基线、覆盖范围、缺口与建议。

### `check`

读取 [references/project-health-check.md](references/project-health-check.md)，运行 `scripts/check_project_health.py <repo>`；该脚本同时汇总 `scripts/check_code_quality.py` 的结果。结合文件规模、依赖、测试、构建配置和近期变化，输出一页式结构评分表（0 分/3 分/5 分）、加权总分，以及单文件、dead code、代码风格、缺陷/潜在 Bug、安全漏洞、复杂度与可维护性、重复代码、测试覆盖和代码坏味道专项。评分是基于证据的工程判断，不把启发式候选冒充已确认事实；没有足够证据的项目标为“待确认”。

单文件检测至少报告：生产代码与测试代码分别的代码行数、文件总行数、类/函数或同等顶层符号数量、超过阈值的文件、文件所在模块及拆分建议。默认阈值和语言例外以参考文档为准；生成物、依赖目录和供应商代码不纳入统计，除非用户明确要求。

dead code 检测至少报告：未被代码引用的内部函数/类/类型、可疑未使用导入、没有入站文本引用的模块候选及置信度。候选必须人工确认后才能删除；反射、动态导入、依赖注入、插件注册、生成代码、CLI 入口和外部调用方均可能造成误报。

代码质量检测先发现项目已配置的格式化、静态分析、安全、重复度和覆盖率工具；确认命令真实且只读后运行。通用脚本用于补充候选，不替代语言生态工具。每项结果必须包含类别、严重度、文件/行号、规则、证据、置信状态和建议动作；没有覆盖率产物时只能报告“未验证”，不能推断覆盖率数值。

### `add`

按 [模板路由](references/document-system.md) 选择单个类型与相关参考。`standard code` 使用语言模板，`standard frontend` 等使用具体规范模板；不覆盖已有约定。`database` 是模型、`migration` 是一次迁移，`testing` / `ui` 是具体策略/页面规格，分别区别于 `standard` 规则。

### 可选 `workflow` / `resume`

仅在用户需要开发协作辅助时读 [开发流程](references/development-workflow.md)：读代码与调用方、明确 AC/拟改路径、实施、真实检查/修正、同步受影响文档与交付。短任务沿用现有需求/Issue 或对话，不强制账本。恢复先核实实际工作区与已完成检查。咨询/评审按只读意图，实现/修复推进到已授权结果；提交/发布沿用实际授权。

## 完成标准

- 真正生成/更新少量适用文件；入口六项内容完整，目录覆盖受维护文件归属，条件读取指向实际文件。
- 项目事实有配置/代码/有效决策依据；示例清楚标注，计划与现状、实施与验证分开，不把拟命令当已通过。
- 规则直接指导动作、有短例与验证方式；不重复配置、不默认建立元数据/指标/账本系统。
- `sync` / `audit` 每项影响有结论与覆盖范围，需求/ADR 历史和冲突可见；兼容镜像仅按约定维护并核对。
- `check` 评分有证据/待确认、权重合计 100%，报告单文件与 dead code 结果；只报告实际运行检查。
- 保留无关人工修改与既有命令语义；具体实现达到实际验收或说明未完成/未验证/待决范围。
