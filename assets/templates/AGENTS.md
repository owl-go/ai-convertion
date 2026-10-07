# 入口兼容模板

本模板用于已有 AGENTS.md / CLAUDE.md 双入口镜像约定的项目。完整入口正文按 [project-instructions.md](project-instructions.md) 填写：项目全景、架构铁律、技术栈、权威目录及文件归属、真实命令、条件读取均不可省略。

生成时将填好的正文写入约定的编辑源，再写入镜像；删除本模板提示，使用 `cmp -s AGENTS.md CLAUDE.md` 验证逐字节一致。各入口有独立作用域时按既有规则分别维护，不强行镜像。没有双入口约定时只生成实际工具入口。
