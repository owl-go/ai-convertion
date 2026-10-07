---
name: ai-project-conventions
description: 从真实项目建立、检查和同步工程规范；生成项目入口、目录及适用的语言、前端、UI、数据库、需求、方案、测试规范。用于 init/sync/check/audit/add；workflow/resume 为可选开发辅助。
---

# AI 项目规范

让项目入口指导文件落位，让适用规范指导具体实现。核心是项目内的 Markdown 文件；生成结果独立于个人技能安装路径与代理 API。

## 操作

```text
$ai-project-conventions init [path]
$ai-project-conventions sync [git-ref]
$ai-project-conventions check [path]
$ai-project-conventions audit [git-ref]
$ai-project-conventions add <kind> [scope]
$ai-project-conventions workflow <task>
$ai-project-conventions workflow resume [task-record]
$ai-project-conventions help
```

这是代理操作语义，本包没有这些独立 CLI。其他工具按实际调用配置使用；加载验证见 [工具适配](references/tool-adapters.md)。仅调用技能而未指定任务：缺规范执行 init，已有规范执行 sync。维护规范不自动实施业务功能；用户要求修改技能本身时编辑技能源文件。

## init：读事实，生成适用文件

先读 [文件契约与模板路由](references/document-system.md)、[通用边界](references/baseline-rules.md)、[工具适配](references/tool-adapters.md)。

1. 核对工作区改动及现有入口/规范；读取代码、配置、测试、CI、需求和有效决策。可用 `scripts/collect_project_evidence.py <repo>` 定位线索，再阅读相关源码。保留无关人工改动。
2. 依据实际工具选择 `AGENTS.md` 或 `CLAUDE.md` 主入口，沿用已有目录。入口填写项目定位、模块/服务全景、架构铁律、真实栈、目录概要、运行/测试/构建命令、任务触发→必须先读的文件。每个命令有配置/源码依据，执行状态单列。
3. 用模板生成目录规范及适用的 `<语言>-standards.md`、frontend/ui/database/requirement/technical-design/testing 规范。每份写范围、具体要求、正确例、错误例、实际检查。目录规范权威维护接口处理、业务逻辑、数据访问、配置、测试、迁移、需求与方案的真实位置及依赖方向；入口只保留概要。
4. 无前端/数据库则不建空文件，多语言按真实代码范围填写；复杂多服务才补服务局部入口，含真实命令、数据、外部依赖/定时任务与增量约定。简单项目用根入口覆盖，不默认建立地图或账本。
5. 核对生成文件、相对引用、归属和命令。未知关键业务规则先澄清；其他未知标待确认，不能编造路径、版本、token 或业务语义。交付实际文件与执行/未执行范围。

规范教写法，具体需求沿用 docs/requirements 或 Issue，方案沿用既有设计目录。大需求写完整需求与方案，中需求简化，小需求一句话加验收。方案围绕模块、各处改动、数据流、接口入出参、失败处理、兼容影响、验证、恢复八问，按实际风险使用。

## check / audit：对照具体规则

先读项目入口，按修改范围必须先读其路由的规范、相关需求和方案。逐条对照适用规则，分别记录编译/lint/文本线索、语义审查、行为测试、人工 UI 检查的证据和盲区。grep 只能定位线索，不能证明行为完整或所有错误路径正确。

`check` 另读 [结构与质量检查](references/project-health-check.md)，运行 `scripts/check_project_health.py <repo>`（汇总质量检查）。保留原结构评分、权重、单文件和 dead code/质量专项：结果有文件/行号、规则、证据、置信状态、建议；未确认候选不得直接删除，覆盖率缺产物记未验证。脚本是辅助，不替代项目规范审查或实际生态工具。

`audit [git-ref]` 按 sync 范围只读核对，报告比较基线、事实/规则/需求与实现冲突、覆盖缺口及建议，不改文件。

## sync：只更新实际影响

读 [维护映射](references/maintenance-workflow.md)。阅读差异、调用方、测试、配置及用户新要求；可运行 `scripts/collect_project_evidence.py <repo> --since <ref>`（比较 ref...HEAD 加工作区变化）。无 ref 说明范围和历史盲区。

- 模块/目录/依赖/栈/命令变化：更新入口相应段落与受影响规范。
- 单个功能规则变化：修订该需求、方案、实现/测试与实际结果；只有通用写法或约定改变才修改规范。
- 每项候选影响给已更新/不适用/待确认结论。区分计划、已实现、已验证，保留必要 AC 修订和 ADR 历史。代码偏离仍有效要求时报告冲突；明确新要求可修订旧文档。

个人技能升级不自动升级业务项目；六类 32 个稳定规则 ID 见 [基线与采用](references/harness.md)。

## add 与可选辅助

`add` 按 [模板路由](references/document-system.md) 补一种明确需要的产物，兼容 kind：agents、project-map/map、glossary、architecture、standard、adr、design、requirement、runbook、exception、gates、impact-map、harness、profile、database、migration、testing、ui、task。`standard` 支持 directory/language/code/frontend/ui/database/requirements/technical-design/testing。database/migration 是具体模型/迁移；testing/ui 是具体策略/规格，区别于规则。help 列操作与类型。

用户需要开发协作或恢复时才读 [可选 workflow/resume](references/development-workflow.md)，短任务沿用需求/Issue/对话；正常已授权工作推进到验收，无需反复确认或强制阶段账本。

完整填实文件及“新增列表筛选→改变筛选条件”的演练见 [教学示例](references/generated-example.md)。交付必须是真实文件与实际检查结果，不能把模板复制、静态校验或拟执行命令当成行为评估。
