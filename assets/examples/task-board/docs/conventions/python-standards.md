# Python 编码规范

## 范围与依据

app/、tests/、scripts/；pyproject.toml 声明 Python >=3.11，CI 配置 3.11。标准库实现，dependencies 为空。实际本机版本以演练命令输出为准，不等同于已验证 CI 版本。

## 具体项目要求

- 模块/函数 snake_case，公开服务为 TaskService；HTTP、业务、SQL 归属见目录规范。
- http.py 解析协议，service.py 校验标题和业务输入，storage.py 绑定 SQL 值；内部类型不能将非法值转成合法结果。
- ValueError/LookupError 在 http.py 映射 400/404 并保留原因。未知异常由运行服务器暴露失败，不返回假成功；本例尚无应用级日志/统一 500 文案，新增相关行为先明确需求。
- server.py 持有并关闭连接；storage.py 的 with connection 负责写操作提交/回滚；测试连接 addCleanup 关闭。当前服务串行，无后台并发任务。
- 新依赖修改真实清单并说明用途；没有锁文件或格式工具，不能编造格式命令或锁定版本。

## 正确例与错误例

正确：`if not isinstance(title, str) or not 1 <= len(title.strip()) <= 80: raise ValueError("标题需为 1–80 字符")`，校验后调用 repository，位置 app/service.py。

错误：`except Exception: return {"done": 1}`，失败被伪装为成功。错误：service.py 导入 HTTP 或自行建立 SQLite 连接，绕过组装与资源所有权。

## 实际检查

| 类型 | 命令/步骤 | 范围 |
|---|---|---|
| 编译/静态/文本 | `python3 scripts/build.py`；无 lint 配置 | 编译与静态复制；导入搜索只是线索 |
| 语义审查 | 阅读 http/service/storage/server 调用链及异常出口 | 验证本次输入/错误与资源责任；不证明全部异常 |
| 行为测试 | `python3 -m unittest discover -s tests -v` | 内存数据库、协议、输入边界和筛选实际场景 |
| 人工 UI | 不适用于纯 Python 规则；跨页面行为依 UI 规范 | 浏览器另行验收 |
