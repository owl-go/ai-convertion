# 前端工程规范

## 范围与依据

web/index.html + page.mjs + api.mjs；无框架、路由库、store 或前端包管理器，模块职责由实际源码确定。生产构建工具尚无，本地 build.py 只复制静态资源。

## 具体规则

page.mjs 持有当前页面状态并调用 api.mjs；api.mjs 统一 fetch、JSON 与非 2xx 错误。列表每次读取服务端事实，不把任务状态复制到另一个长期缓存。提交/完成等待期间禁用对应按钮，失败恢复按钮并保留输入。显示服务端内容用 textContent；静态资源仅通过 http.py 白名单服务。当前只用于本机单用户，无路由/鉴权；引入用户时需同时定义服务端权限，不能只隐藏按钮。

## 正确例与反例

正确：page 调用 `await createTask(input.value)`，api 定义 POST 与 JSON。错误：page 到处 `fetch('/api/tasks')` 或在 api 内 `document.querySelector(...)`，两处职责混合。

## 检查

根目录运行两条 node --check 与 python3 scripts/build.py；核对 page 只有模块请求调用、api 不操作 DOM。HTTP 测试覆盖协议，浏览器行为另按 [UI 规范](ui.md) 检查；语法通过不能当成交互通过。
