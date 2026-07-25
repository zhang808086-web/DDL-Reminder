# 架构说明 / Architecture

DDL Reminder 使用分层结构。主要目标是让领域规则独立于 PySide6 和 SQLite，这样核心逻辑可以在不启动 UI、不访问真实数据库的情况下测试。

DDL Reminder uses a layered structure. The main goal is to keep domain rules independent from PySide6 and SQLite, so core behavior can be tested without starting the UI or touching a real database.

## 分层 / Layers

```text
src/ddl_reminder/
  domain/          # 领域模型、DDL 规则、领域异常 / Domain model, deadline rules, exceptions
  ports/           # Repository 和 Notifier 接口 / Repository and notifier interfaces
  application/     # 用例服务 / Use case services
  infrastructure/  # SQLite、SQLAlchemy、通知、自启 / SQLite, SQLAlchemy, notification, autostart
  ui/              # PySide6 窗口和对话框 / PySide6 windows and dialogs
  main.py          # 组合根 / Composition root
```

## 领域层 / Domain

领域层负责任务状态和 DDL 时间规则。

The domain layer owns task state and deadline rules.

主要职责：

Important responsibilities:

- 校验任务标题 / Validate task titles
- 将日期和时间规范化为 deadline / Normalize date and time into a deadline
- 判断 DDL 分类 / Classify deadlines
- 格式化剩余或逾期时间 / Format remaining or overdue time
- 记录提醒状态 / Track notification flags

领域层不导入 PySide6 或 SQLAlchemy。

The domain layer does not import PySide6 or SQLAlchemy.

## 应用层 / Application

应用层编排用例。

The application layer coordinates use cases.

`TaskService` 负责任务操作：创建、更新、完成、恢复、删除、查询进行中任务、查询已完成任务、查询紧急任务。

`TaskService` handles task operations: create, update, complete, restore, delete, list active tasks, list completed tasks, and get urgent tasks.

`ReminderService` 判断当前应该发送哪些提醒，并更新任务的提醒标记。

`ReminderService` checks which reminders should be emitted and updates notification flags.

`ReminderRunner` 调用提醒服务，通过通知接口发送通知，并在通知失败时记录日志而不是让应用崩溃。

`ReminderRunner` calls the reminder service, sends notifications through a notifier, and logs notification failures without crashing the app.

## 接口层 / Ports

接口层定义边界：

Ports define boundaries:

- `TaskRepository`：持久化边界 / persistence boundary
- `Notifier`：通知边界 / notification boundary

这让应用层依赖接口，而不是直接依赖 SQLite 或桌面通知实现。

This allows the application layer to depend on interfaces instead of concrete SQLite or desktop notification code.

## 基础设施层 / Infrastructure

基础设施层实现外部细节：

Infrastructure implements external details:

- `SQLAlchemyTaskRepository`
- `InMemoryTaskRepository`
- SQLite engine/session setup
- Windows desktop notification
- Windows autostart registry entry
- Single instance lock
- AppData path management

生产数据库保存在：

The production database is stored under:

```text
%APPDATA%/DDL-Reminder/tasks.db
```

## UI 层 / UI

UI 层使用 PySide6 实现。

The UI layer is built with PySide6.

主要界面：

Main UI pieces:

- `MainWindow`：任务列表、筛选、任务操作、设置入口 / task list, filters, task actions, settings entry
- `TaskDialog`：创建任务 / create task
- `TaskDetailDialog`：查看和更新任务详情 / view and update task details
- `FloatingWindow`：置顶紧急任务悬浮窗 / always-on-top urgent task window
- `TaskCard`：悬浮窗中的任务卡片 / compact floating-window task item
- `SettingsDialog`：设置页，目前包含开机自启 / app settings, currently including autostart

UI 之间通过信号同步状态。例如，从悬浮窗更新任务后，会通过 `tasks_changed` 信号刷新主窗口。

UI changes emit signals so related windows refresh immediately. For example, when a task is updated from the floating window, the main window refreshes through a `tasks_changed` signal.

## 组合根 / Composition Root

`main.py` 负责组装整个应用：

`main.py` wires everything together:

- 创建 `QApplication` / Creates `QApplication`
- 应用字体和主题 / Applies font and theme setup
- 获取单实例锁 / Acquires single-instance lock
- 初始化 SQLite / Initializes SQLite
- 创建 repository 和 services / Creates repository and services
- 创建主窗口和悬浮窗 / Creates main window and floating window
- 创建托盘图标和菜单 / Creates tray icon and menu
- 启动提醒定时器 / Starts reminder timer
- 根据普通启动或开机自启决定显示行为 / Decides startup behavior for normal launch vs autostart launch

## 测试 / Testing

测试覆盖：

The test suite includes:

- 领域单元测试 / Domain unit tests
- 服务单元测试 / Service unit tests
- 内存 repository 测试 / In-memory repository tests
- SQLAlchemy repository 集成测试 / SQLAlchemy repository integration tests
- 提醒运行器测试 / Reminder runner tests
- 使用 fake registry 的开机自启测试 / Autostart tests with fake registry behavior
- 悬浮窗信号同步回归测试 / Floating window signal regression test

测试命令：

Test command:

```powershell
python -m pytest
```
