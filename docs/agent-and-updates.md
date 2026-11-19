# 本机 Agent 接入、打包精简与新版检查

v0.3.1 默认在安装时完成本机 Agent 接入；下方配置仅用于参考和特殊环境排错。

## 自动接入（v0.3.1）

安装器默认选中自动接入，无需用户编辑配置。Claude Code 和 Codex 的用户级
配置会提前建立；即使客户端以后才安装，首次读取用户配置时也能发现服务。
DeepSeek Harness 会检测 `$DSH_HOME/profiles/*/package.json` 下已初始化的 profile，
为各 profile 的 `cordis.patch.yml` 添加独立 MCP 客户端条目。

同时注册当前 Windows 用户的计划任务：登录后检查，并每 2 分钟检测一次后来
出现的 DeepSeek profile。此任务不需要 DDL Reminder 窗口一直运行；关机期间
不执行，系统恢复且用户登录后继续。任务以普通用户权限执行，后台隐藏运行。
设置页可关闭/恢复此检测，也可点击“一键接入 Agent”立即重试。
首次注册客户端后，需要其重载配置或打开新会话；客户端原有审批要求仍生效。

配置修改前备份到原文件同目录的 `*.ddl-backup-*`，保留其他 MCP、模型、
凭据、权限及注释。重复检测不会重复添加或覆盖用户主动停用的 Codex 服务。
同名冲突或损坏配置会跳过并记录报告，不覆盖原文件。
报告为 `%APPDATA%/DDL-Reminder/agent-setup.json`，后台检测状态为
`agent-autoconnect.json`。卸载应用时移除该安装所拥有的检测任务。

自动接入配置仅解决本机 MCP 的发现与连接；Agent 本身仍需已登录且模型可用。
不会修改模型供应商、API 密钥或取消工具权限审批。

官方配置依据：

- [Claude Code 用户级 MCP](https://code.claude.com/docs/en/mcp#user-scope)：`~/.claude.json` 的 `mcpServers`。
- [Codex MCP](https://developers.openai.com/codex/mcp)：`~/.codex/config.toml` 的 `mcp_servers`。
- [DeepSeek Harness MCP 客户端](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/mcp/mcp-client/README.zh.md)：profile patch 内的 `@deepseek-ai/dsh-mcp-client`。

支持标准用户目录，并尊重 `CLAUDE_CONFIG_DIR`、`CODEX_HOME`、`DSH_HOME`。
客户端使用其他账号、容器或 WSL 时，需在其实际运行环境配置可访问的 MCP 入口。

## 本机 MCP 服务

采用官方 MCP Python SDK 1.x（`mcp>=1.28,<2`）的 stdio transport。
提供 `get_local_time`、`create_task`、`list_tasks`、`get_task` 四个工具。
创建时复用 TaskService：标题最多 15 字，日期必须为有效的 YYYY-MM-DD，
时间必须为 00:00–23:59；省略时间默认 23:59。允许创建已经逾期的任务。
接口首版没有编辑、删除、完成任务工具。

安装包将同时包含 `DDL-Reminder.exe` 和 `DDL-Reminder-MCP.exe`，共享
`_internal` 依赖目录，用户不必单独安装 Python。MCP 由 agent 按需启动，
无需先运行桌面程序。不要把图形界面的 exe 配置成 MCP 命令。

支持 stdio MCP 的客户端可使用以下配置，按本机用户名和实际安装路径修改：

```json
{
  "mcpServers": {
    "ddl-reminder": {
      "command": "C:\\Users\\YOUR_NAME\\AppData\\Local\\Programs\\DDL Reminder\\DDL-Reminder-MCP.exe",
      "args": []
    }
  }
}
```

不同客户端的外层配置格式可能不同；核心是 command 指向 MCP exe，args 为空。
该进程按启动它的 Windows 账号访问
`%APPDATA%/DDL-Reminder/tasks.db`，不监听端口。不要为 MCP 使用另一个账号
或重定向 APPDATA，否则会访问另一个用户数据目录。

开发环境安装依赖后，可运行 `ddl-reminder-mcp`，或在仓库设置 PYTHONPATH=src
后执行 `python -m ddl_reminder.mcp_server`。stdout 专用于协议，日志写 stderr。
桌面程序现有 30 秒刷新会读取 MCP 创建的新任务；未运行桌面程序时仅存储任务，
提醒仍由桌面程序负责。SQLite 写锁等待时间为 15 秒，失败会返回工具错误。
收到创建成功结果后不要重复调用；连接中断导致结果不明时应先查询任务避免重复。

## 体积优化

DDL-Reminder.spec 排除未使用的 Qt 模块，并过滤非 QtQuick/QtQml 的 QML 模块、
翻译文件和关联的大型 Qt 运行库。只分发实际使用的 ico，不分发原始大尺寸 PNG。
保留 QtQuick 控件、样式、实现插件和软件 OpenGL 渲染器以兼顾兼容性。
MCP 使用独立 console exe，与 GUI 共用依赖目录。Inno Setup 改为 LZMA2 最大压缩。
升级安装时清理旧 _internal 目录，避免历史依赖残留；用户数据库不在该目录。

MCP SDK 本身会引入新依赖，最终体积需在后续实际构建后测量，不能据配置预估节省值。
后续必须验证所有 QML 窗口、托盘、通知、网络检查和 stdio exe 都可在干净机器运行。

## 新版检测

启动后延迟 3 秒后台检查 GitHub 最新正式版，运行期间每小时检查是否达到间隔，
成功检查后 24 小时内不自动重复请求。发现新版时也显示托盘通知。
设置页支持随时手动检查。网络超时 15 秒，网络异常只展示状态，不阻止任务操作。
使用 packaging.version 按版本语义比较，跳过预发布与开发版。

发现更新显示“下载新版”提示，用户点击后通过浏览器下载对应安装包；找不到匹配
安装包时打开该版本 Release 页面。用户下载后需退出程序并自行运行安装包。
本版没有自动执行下载文件，也没有后台静默升级。仅允许固定仓库的 HTTPS 发布地址。

发布前需同步 pyproject.toml、src/ddl_reminder/version.py 和 installer/DDL-Reminder.iss
中的版本；Release 安装包应命名为 DDL-Reminder-Setup-v<版本>.exe。
当前版本为 0.3.1。

已安装的旧版没有更新检测，用户需要先手动升级一次，之后才有此入口。

参考：[官方 MCP SDK 1.x](https://github.com/modelcontextprotocol/python-sdk/tree/v1.x)、
[GitHub Release API](https://docs.github.com/en/rest/releases/releases#get-the-latest-release)。
