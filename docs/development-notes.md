# 开发记录 / Development Notes

这个项目按阶段完成，用来练习 Python 工程开发能力。开发过程强调小步推进、先定义边界、代码评审、测试验证，再进入下一层。

This project was built in stages as Python engineering practice. The process emphasized small steps, explicit boundaries, code review, and test verification before moving to the next layer.

## Phase 1：领域逻辑 / Domain Logic

第一阶段专注于纯 Python 逻辑：

The first phase focused on pure Python logic:

- `Task`
- DDL 规范化 / deadline normalization
- DDL 分类 / deadline classification
- 剩余时间格式化 / remaining time formatting
- 领域异常 / domain exceptions
- 提醒边界规则 / reminder boundary rules

关键原则是：领域逻辑不依赖 PySide6、SQLAlchemy，也不在需要确定性测试时直接依赖系统当前时间。

The important rule was that domain logic should not depend on PySide6, SQLAlchemy, or system time directly when tests need determinism.

## Phase 2：Repository 和 Service / Repository And Service

第二阶段引入应用边界：

The second phase introduced the application boundary:

- `TaskRepository` 接口 / interface
- `InMemoryTaskRepository`
- `TaskService`

Service 通过依赖注入接收 repository，这让测试更简单，也让持久化实现可以替换。

The service receives a repository through dependency injection, which makes tests simple and keeps persistence replaceable.

这一阶段的一个修正点是：更新任务不能直接绕过领域校验，更新时应该保持和创建时一致的规则。

One design correction in this phase was avoiding direct mutation that bypasses domain validation. Task updates need to preserve the same rules as task creation.

## Phase 3：SQLite 持久化 / SQLite Persistence

第三阶段加入 SQLAlchemy 和 SQLite：

The third phase added SQLAlchemy and SQLite:

- SQLAlchemy model
- 数据库 engine/session factory / database engine/session factory
- `SQLAlchemyTaskRepository`
- 使用临时 SQLite 的集成测试 / integration tests with temporary SQLite databases

这一阶段把领域对象 `Task` 和数据库行 `TaskModel` 分离开。

This phase separated domain `Task` objects from database `TaskModel` rows.

## Phase 4：主窗口 / Main Window

第四阶段实现第一个 PySide6 UI：

The fourth phase built the first PySide6 UI:

- 进行中任务 / Active tasks
- 已完成任务 / Completed tasks
- 创建任务 / Task creation
- 任务详情更新 / Task detail update
- 完成、恢复和删除操作 / Complete, restore, and delete actions
- 确认对话框 / Confirmation dialogs

第一版 UI 先保证可用，后续再进行视觉优化。

The first UI version was intentionally simple, then later redesigned visually.

## Phase 5：悬浮窗 / Floating Window

悬浮窗成为这个应用最重要的差异点：

The floating window became the app's main differentiator:

- 显示最紧急的三个任务 / Shows the three most urgent tasks
- 始终置顶 / Always on top
- 直接打开任务详情 / Opens task details directly
- 定时刷新 / Refreshes on timer
- 任务变化后立即刷新 / Refreshes immediately after task changes
- 保存位置 / Saves position
- 支持贴边吸附和自动收起 / Supports edge snapping and auto-hide

视觉方向是轻量磨砂玻璃面板、紧凑任务卡片和小面积状态色。

The visual direction was a light glass panel with compact task cards and small status colors.

## Phase 6：提醒系统 / Reminder System

提醒阶段加入：

The reminder phase added:

- 24 小时提醒 / 24-hour reminder
- 1 小时提醒 / 1-hour reminder
- 逾期提醒 / overdue reminder
- 防重复提醒 / duplicate prevention
- 通知失败日志 / notification failure logging

一个关键修正是：新增独立的 `notified_overdue` 字段，而不是复用 `notified_1h`。

A key correction was adding a separate `notified_overdue` flag instead of reusing `notified_1h`.

## Phase 7：Windows 集成 / Windows Integration

Windows 集成加入：

Windows integration added:

- 系统托盘 / System tray
- 关闭时隐藏而不是退出 / hide instead of close
- 托盘双击显示主窗口 / tray double-click to show the main window
- 单实例锁 / single-instance lock
- 通过 Windows Run 注册表实现开机自启 / autostart through the Windows Run registry key

开机自启使用 `--autostart` 参数，这样可以只显示悬浮窗，不主动弹出主窗口。

Autostart uses a `--autostart` argument so the app can start with only the floating window visible.

## Phase 8：打包和发布准备 / Packaging And Release Prep

应用使用 PyInstaller 打包，并把运行数据迁移到 AppData：

The app was packaged with PyInstaller and moved runtime data to AppData:

- SQLite 数据库位于 `%APPDATA%/DDL-Reminder/` / SQLite database under `%APPDATA%/DDL-Reminder/`
- 日志文件位于 `%APPDATA%/DDL-Reminder/` / log file under `%APPDATA%/DDL-Reminder/`
- `.gitignore` 忽略构建产物 / build artifacts ignored in `.gitignore`
- README 和 docs 为 GitHub 发布整理 / README and docs prepared for GitHub

## 练习内容 / What This Project Practiced

- 分层架构 / Layered architecture
- 依赖注入 / Dependency injection
- Repository pattern
- 不过度设计的领域边界 / Domain-driven boundaries without overengineering
- PySide6 UI development
- SQLAlchemy persistence
- Windows desktop integration
- PyInstaller packaging
- pytest-driven regression checks
