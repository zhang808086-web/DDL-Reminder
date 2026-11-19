# 本机 Agent 接入、打包精简与新版检查

v0.3.0 提供本机 MCP 服务、依赖精简和新版检测。安装后在 agent 中配置下列入口即可调用。

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
不自动修改 agent 配置。该进程按启动它的 Windows 账号访问
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
当前版本为 0.3.0。

已安装的旧版没有更新检测，用户需要先手动升级一次，之后才有此入口。

参考：[官方 MCP SDK 1.x](https://github.com/modelcontextprotocol/python-sdk/tree/v1.x)、
[GitHub Release API](https://docs.github.com/en/rest/releases/releases#get-the-latest-release)。
