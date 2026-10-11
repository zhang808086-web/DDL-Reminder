# 发布说明 / Release Notes

## v0.2.2

悬浮窗拖动与四边缩入修复版本，不增加业务功能，也不改变数据库结构。

Floating-window drag and four-edge collapse correction release with no new business features and no database schema changes.

### Fixed

- 悬浮窗整个可见区域均可发起拖动，包括固定键、关闭键、任务卡和完成键。
- 短按仍执行原有按钮操作，移动超过拖动阈值后改为拖动窗口。
- 拖动期间暂停窗口位置动画，避免动画与原生系统移动竞争。
- 松开后继续执行左、右、上、下四边吸附、位置保存与自动缩入。

- The entire visible floating window can initiate dragging, including pin, close, task-card, and completion controls.
- Short clicks retain their original actions; movement beyond the drag threshold moves the window.
- Position animation is disabled during dragging so it cannot compete with native system movement.
- Releasing keeps the existing four-edge snap, position persistence, and auto-collapse behavior.

### Verification

- Full-surface pointer tests cover pin, close, completion, and empty surface regions.
- Geometry tests cover left, right, top, and bottom snapping and collapsed positions.
- The SQLite schema and `%APPDATA%/DDL-Reminder/tasks.db` location are unchanged.

## v0.2.1

Qt Quick/QML 界面修复版本，不增加新业务功能，也不改变数据库结构。

Qt Quick/QML interface correction release with no new business features and no database schema changes.

### Fixed

- 已完成任务卡片统一显示绿色“已完成”，不再显示逾期或剩余时间。
- 已完成任务卡片移除重复的完成勾选按钮，恢复操作保留在任务详情中。
- 主窗口任务卡、悬浮窗卡片和详情信息卡统一间距、边框与视觉层级。
- 任务编辑、任务详情、设置和确认弹窗使用可靠的居中定位与内容内边距。
- 主窗口侧栏固定为稳定宽度，防止布局压缩。

- Completed task cards now show a green Completed state instead of overdue or remaining time.
- Removed the redundant completion checkbox from completed cards; restore remains available in task details.
- Aligned spacing, borders, and hierarchy across main, floating, and detail cards.
- Correctly centered all dialogs and applied real content padding.
- Locked the sidebar to a stable width to prevent layout compression.

### Verification

- 117 automated tests pass.
- Real QML screenshots cover active cards, completed cards, floating cards, and completed-task details.
- The SQLite schema and `%APPDATA%/DDL-Reminder/tasks.db` location are unchanged.

## v0.2.0

Qt Quick/QML 全界面迁移版本，同时保留现有 Python 业务逻辑和本地数据。

Full Qt Quick/QML interface migration while preserving the existing Python business logic and local data.

### Changed

- 主窗口、悬浮窗、任务编辑、任务详情、设置和确认界面全部迁移到 QML。
- 新增深海军蓝、青色与紫色组成的现代科技风主题和共享组件。
- 主窗口继续按 `(deadline, created_at)` 排序；悬浮窗继续显示最早的三个未完成任务，并可直接勾选完成。
- 运行入口改用 `QQmlApplicationEngine`，系统托盘仍使用原生 Windows/Qt 菜单。
- 数据库仍位于 `%APPDATA%/DDL-Reminder/tasks.db`，schema 未改变。

- Migrated the main window, floating window, editor, detail, settings, and confirmation surfaces to QML.
- Added a deep-navy, cyan, and violet technology-style theme with shared components.
- Retained `(deadline, created_at)` ordering and the three-item floating list with direct completion.
- Switched runtime composition to `QQmlApplicationEngine`; the system tray keeps its native Qt menu.
- Kept the database at `%APPDATA%/DDL-Reminder/tasks.db` with no schema change.

### Verification

- Real screenshots are generated from the QML application with synthetic in-memory data.
- The automated suite includes QML loading, runtime composition, controller, model, and floating geometry coverage.
- The upgrade procedure backs up and hashes the production database before installation.

## v0.1.4

Windows packaging fix release.

### Fixed

- Removed environment-provided runtime and ICU DLLs from the bundle root so Qt6 can load on supported Windows systems.
- Upgrade installers remove conflicting root-level DLLs left by v0.1.3.

### Verification

- Packaged `Qt6Core.dll`, `Qt6Gui.dll`, and `Qt6Widgets.dll` load successfully in a clean DLL search probe.
- The full automated test suite passes.

## v0.1.3

Task ordering and floating-window completion release.

### Features

- Main-window task lists are sorted by earliest deadline, then creation time
- Added a completion button to floating-window task cards
- Completing a task from the floating window refreshes both task views

### Verification

The current automated test suite includes 93 tests:

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

## v0.1.2

UI polish release focused on the task creation flow.

### Features

- Reworked the task creation dialog to match the task detail dialog style
- Added the same glass panel, rounded shell, custom close button, DDL date/time row, and bottom action bar
- Added lightweight date/time arrows and drag support to the task creation dialog

### Verification

The current automated test suite includes 91 tests:

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
