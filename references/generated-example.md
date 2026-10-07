# 已填入口教学示例

下面是一份假设的 Go 订单 API + Vue 管理端入口正文，用于说明完成后的形态。所有路径、版本和命令都是假设证据，**不是本仓库事实，也没有运行这个业务项目**。实际 `init` 必须从目标仓库替换；不可把此例原样生成到项目。

---

# 订单管理项目指引

## 项目全景

本项目让运营查询并取消尚未发货的订单。订单 API 负责状态与取消规则；管理端负责操作界面；支付系统负责实际退款，仓储系统负责发货。本项目不实现支付清算与库存调度。

管理端 → HTTP 适配 → order 用例 → Repository 接口 → PostgreSQL 适配。退款请求通过 Payment 接口到外部支付系统；启动入口组装依赖。本文件适用于全仓库。

## 架构铁律

- `cmd/api` 可依赖所有实现以完成组装；HTTP/存储/支付适配可依赖 `internal/order` 的接口与类型。
- `internal/order` 禁止导入 HTTP、PostgreSQL 与支付适配；跨边界仅使用其定义的接口。HTTP 层不得直接执行 SQL，数据库适配不得决定取消是否允许。
- 取消权限在服务端验证。已发货订单拒绝取消；重复取消不能产生第二次退款。
- 本地订单更新与退款意图持久化在一个事务提交；外部退款由任务执行并按业务键去重。失败保持可重试状态，不能把调用失败写成退款成功。

## 实际技术栈（本例假设配置）

| 组件 | 版本口径 | 证据 |
|---|---|---|
| Go | `go 1.23.0` 为声明要求；CI 使用 1.23.x | `go.mod`、`.github/workflows/ci.yml` |
| Vue / TypeScript | 声明范围分别为 `^3.5.0` / `~5.6.0`；实际安装版本看锁文件 | `web/package.json`、`web/package-lock.json` |
| PostgreSQL | 开发镜像主版本 16；生产版本待核实 | `compose.yaml` |

## 权威代码目录与文件归属

```text
cmd/api/main.go                  # 启动与依赖组装
internal/order/                  # 状态、取消用例、Repository/Payment 接口
internal/transport/http/         # 请求校验、身份映射、错误/响应转换
internal/storage/postgres/       # SQL、Repository 实现与事务
internal/integration/payment/    # 外部支付协议与错误映射
internal/jobs/                   # 待退款任务调度与重试
web/src/pages/                   # 路由页面与页面协调
web/src/components/              # 公共展示/交互组件
web/src/api/                     # 类型化 API 调用与错误转换
web/src/styles/                  # token 与基础样式
migrations/                      # 追加式有序 SQL 迁移
scripts/                         # 开发与检查脚本
docs/conventions/                # 项目具体规范
docs/requirements/              # 具体需求与 AC 修订
docs/designs/                   # 具体技术方案与实施状态
docs/adr/                       # 长期决策及替代链
.github/workflows/              # CI 配置
go.mod / go.sum / compose.yaml   # 根构建依赖与开发环境配置
web/package*.json / web/*config* # 前端依赖与构建配置
```

新增订单规则放 `internal/order/`；新增外部适配放 `internal/integration/<system>/`；新领域放 `internal/<domain>/`，接口由使用它的领域定义，并同步本节。协议映射不得放领域目录。

Go 单测与被测文件同目录，后缀 `_test.go`；数据库集成测试放存储适配目录，以测试约定隔离；前端测试与组件相邻，后缀 `.spec.ts`。静态资源放 `web/public/`，构建生成物 `web/dist/` 不手改、不提交。文档/脚本/配置按上表归属，禁止根目录散落业务文件。

## 运行与检查（命令来源核实的示例，均未实际运行）

| 用途 | 命令与工作目录 | 来源/前提 |
|---|---|---|
| API 启动 | 根目录 `go run ./cmd/api` | README；需数据库与环境配置 |
| Go 检查 | 根目录 `go vet ./...`、`go test ./...` | CI；数据库集成测试另需测试环境 |
| 前端启动 | `web/` 下 `npm run dev` | package.json |
| 前端检查 | `web/` 下 `npm run typecheck`、`npm run test -- --run`、`npm run build` | package.json / CI |

不能将这些示例命令记为已通过；真实项目还应填实际运行结果和未验证原因。

## 条件读取

- Go 代码：读 `docs/conventions/language-go.md`；前端 TS：读 `docs/conventions/language-ts.md`。
- 组件、路由、状态、请求：读 `docs/conventions/frontend.md`；页面/交互/视觉再读 `docs/conventions/ui.md`。
- 模型、查询、事务、迁移：读 `docs/conventions/database.md` 及相关迁移。
- 行为变化：读 `docs/conventions/requirements.md` 和该任务具体需求（例如取消主题需求）；先找到实际文件，再引用。
- 跨模块/契约/失败恢复：读 `docs/conventions/technical-design.md` 与相关方案/ADR。
- 所有代码变更的验证：读 `docs/conventions/testing.md`，按影响选择真实检查。

本例假设以上规则文件已经生成；实际项目不可链接不存在的文件。采用通用基线 3.0.0，具体规则按配置与项目决策落地。开发后同步受影响的入口、规则或需求/设计，报告实际结果。
