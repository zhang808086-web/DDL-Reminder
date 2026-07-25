# 发布说明 / Release Notes

## v0.1.1

Second release focused on packaging and installation polish.

### Features

- Custom application icon
- Desktop shortcut icon
- System tray icon
- Inno Setup installer
- Autostart launch now shows only the floating DDL window
- Autostart can be toggled from the Settings window

### Verification

The current automated test suite includes 90 tests:

```powershell
python -m pytest
```

### Packaging Command

```powershell
pyinstaller --noconfirm DDL-Reminder.spec
iscc installer\DDL-Reminder.iss
```

Release artifacts:

```text
dist/DDL-Reminder/
installer_dist/DDL-Reminder-Setup.exe
```

## v0.1.0

第一个可用的 Windows 桌面版本。

First usable Windows desktop version.

### 功能 / Features

- 创建、编辑、完成、恢复和删除任务 / Task creation, editing, completion, restore, and deletion
- 进行中、已完成、紧急任务视图 / Active, completed, and urgent task views
- 本地 SQLite 持久化 / Local SQLite persistence
- 显示三个最紧急任务的桌面悬浮窗 / Desktop floating window for the three most urgent tasks
- 悬浮窗位置保存 / Floating window position saving
- 悬浮窗贴边吸附和自动收起 / Floating window edge snapping and auto-hide
- 可从主窗口和悬浮窗编辑任务详情 / Task detail editing from both main window and floating window
- 24 小时提醒 / 24-hour reminder
- 1 小时提醒 / 1-hour reminder
- 逾期提醒 / overdue reminder
- Windows 系统通知 / Windows system notifications
- 防重复提醒 / Duplicate reminder prevention
- 系统托盘集成 / System tray integration
- 单实例锁 / Single-instance lock
- Windows 开机自启 / Windows autostart
- PyInstaller 打包 / PyInstaller packaging

### 验证 / Verification

当前自动化测试包含 88 个测试：

The current automated test suite includes 88 tests:

```powershell
python -m pytest
```

手动验收覆盖：

Manual validation has covered:

- 主任务流程 / Main task workflows
- 悬浮窗行为 / Floating window behavior
- 提醒行为 / Reminder behavior
- 系统托盘行为 / System tray behavior
- 开机自启行为 / Autostart behavior
- 打包后 exe 启动 / Packaged exe launch

### 已知限制 / Known Limitations

- 暂无数据库迁移工具 / No database migration tool yet
- 暂无云同步 / No cloud sync
- 暂无重复任务 / No recurring tasks
- 暂无自定义提醒间隔 / No custom reminder intervals

### 打包命令 / Packaging Command

```powershell
pyinstaller --noconfirm DDL-Reminder.spec
```

发布产物：

Release artifact:

```text
dist/DDL-Reminder/
```

### 安装器 / Installer

Install Inno Setup, then compile:

```powershell
iscc installer\DDL-Reminder.iss
```

Installer artifact:

```text
installer_dist/DDL-Reminder-Setup.exe
```
