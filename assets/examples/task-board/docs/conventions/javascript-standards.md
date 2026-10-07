# JavaScript 编码规范

## 范围与依据

web/api.mjs 与 web/page.mjs；index.html 使用浏览器 ES modules。无框架、npm 清单或第三方依赖。Node 语法检查来自 .github/workflows/ci.yml，CI 声明 Node 24；浏览器运行能力单独验收。

## 具体项目要求

- 导出函数 camelCase，模块使用具名 import；page 负责 DOM，api 负责 fetch/协议，沿目录规范依赖方向。
- 外部响应先检查 response.ok；error 字段转为 Error。页面显示失败并恢复按钮，输入只在创建成功后清空。
- 布尔筛选通过 API 参数序列化为 0/1；页面不拼接业务 URL，不复制服务端任务状态。
- 用户标题用 textContent 渲染；事件使用原生 label/input/button，所有 Promise 的失败可见。新增并发读取时核对过期响应与恢复状态，不能只靠语法通过。
- 本例无构建依赖；若引入依赖先明确清单与构建方式，不添加不存在的 npm 命令。

## 正确例与错误例

正确：`listTasks(includeDone.checked)` 在 page.mjs 调用 API，api.mjs 将它序列化为查询参数；`span.textContent = task.title` 展示用户内容。

错误：页面直接 fetch 并吞掉错误，或 `span.innerHTML = task.title`，绕过协议边界或把用户文本当 HTML。

## 实际检查

| 类型 | 命令/步骤 | 范围 |
|---|---|---|
| 静态/文本 | `node --check web/api.mjs`、`node --check web/page.mjs`；无 lint | 仅语法；fetch 搜索用于定位 |
| 语义审查 | 阅读请求、事件和 finally 路径；核对状态所有者 | 当前调用链与响应顺序 |
| 行为测试 | Python unittest 验证服务端协议；本例未配置 JS 行为自动测试 | HTTP 通过不证明 DOM 操作 |
| 人工 UI | 启动服务器按 UI 规范操作筛选、失败/重试及键盘 | 记录实际操作范围；未执行保持未验证 |
