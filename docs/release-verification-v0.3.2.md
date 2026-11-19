# v0.3.2 验证记录

## 修复范围

v0.3.1 已撤回为草稿。其周期任务启动 PowerShell，可能短暂显示命令行窗口。
v0.3.2 改为直接启动独立无窗口程序 `DDL-Reminder-Agent-Setup.exe`，不加载 Qt，不通过 shell 或 MCP 控制台子进程注册客户端。升级时清理旧任务。
保留 Claude Code、Codex、DeepSeek Harness 接入。

## 测试与打包

- 164 项测试通过，包含打包后的 MCP 验证和后台入口成功、失败场景。
- Windows 隔离安装、覆盖升级、旧依赖清理、GUI 启动、卸载及数据库保留检查通过。
- 安装后的 1902 个文件与打包输出校验一致。
- 后台可执行文件 PE Subsystem 为 2（Windows GUI）。
- 不附加隐藏参数，连续普通启动 5 次，无后台可见窗口及控制台窗口事件。

## 本机升级与周期任务

- 本机已覆盖安装 v0.3.2，GUI、MCP、后台注册程序与构建产物哈希一致。
- 定时任务直接执行安装目录中的 `DDL-Reminder-Agent-Setup.exe`，无命令行参数。
- 以 Windows 窗口事件钩子连续观察 150 秒，任务运行记录为 `2026-11-20 00:25:23+00:00`、`00:25:40+00:00`、`00:27:41+00:00`；时间字符串保留任务接口原始表示。
- 任务结果码为 0，可见后台窗口和控制台窗口事件均为空。
- `agent-setup.json` 报告三种客户端均已接入。
- 生产数据库包含 29 项任务，升级前后 SHA256 一致，SQLite 完整性检查为 `ok`。
- 数据库备份：`%APPDATA%\DDL-Reminder\backups\tasks-pre-v0.3.2-20261120-002420.db`。
- 数据库 SHA256：`4B210D60D5CB155AD138BB8759DF31A55CDCB8ACD78C4A6F62E72975BF14EDBD`。

窗口事件检查记录本次观察结果；检查工具为 `tools/verify_no_console.py`。

## 发布产物

- 文件：`DDL-Reminder-Setup-v0.3.2.exe`
- 大小：66,900,784 字节（63.80 MiB）
- SHA256：`040900100AC1AD26976E45747F92A182EB32EBB9F3534D6430AF61B39B6B8613`
