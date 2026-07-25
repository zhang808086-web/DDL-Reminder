# 产品说明 / Product Notes

DDL Reminder 是一个 Windows 桌面 DDL 提醒工具。它的核心目标是让重要截止时间停留在桌面上，而不是藏在一个需要主动打开的任务列表里。

DDL Reminder is a Windows desktop reminder app for deadlines that should stay visible instead of being hidden inside a task list that the user must actively open.

## 目标用户 / Target User

第一目标用户是需要管理课程作业、报名截止、实验报告、提交日期等 DDL 的学生或个人用户。

The first target user is a student or individual user who needs to track coursework, registration deadlines, reports, submissions, and similar DDL-driven tasks.

应用坚持本地优先，不需要账号、云同步、多人协作或后端服务。

The app is intentionally local-first. It does not require accounts, cloud sync, collaboration, or a backend service.

## 核心体验 / Core Experience

- 创建带标题、可选描述和截止时间的任务
- 在主窗口查看进行中、已完成和紧急任务
- 在桌面悬浮窗中看到最紧急的三个任务
- 在 DDL 前和逾期后收到 Windows 通知
- 通过系统托盘常驻运行
- 根据用户选择支持 Windows 开机自启

- Create a task with a title, optional description, and deadline
- View active, completed, and urgent tasks in the main window
- See the three most urgent tasks in a desktop floating window
- Receive Windows notifications before deadlines and after overdue
- Keep the app resident in the system tray
- Support Windows autostart when enabled by the user

## 当前范围 / Current Scope

v0.1.0 聚焦于一个可用的单用户 Windows 桌面应用：

v0.1.0 focuses on a usable single-user Windows desktop app:

- 本地 SQLite 存储 / Local SQLite storage
- PySide6 桌面界面 / PySide6 desktop UI
- 系统托盘集成 / System tray integration
- 桌面悬浮提醒窗 / Floating reminder window
- DDL 分类和提醒规则 / Deadline classification and reminder rules
- PyInstaller 打包 / PyInstaller packaging

## v0.1.0 不包含 / Out Of Scope For v0.1.0

- 用户账号 / User accounts
- 云同步 / Cloud sync
- 手机端 / Mobile app
- Web 端 / Web app
- 多人协作 / Multi-user collaboration
- 自定义提醒规则 / Custom reminder rules
- 复杂重复任务 / Complex recurrence
- 插件系统 / Plugin system

## 产品原则 / Product Principle

DDL Reminder 应该轻量、安静、持续可见。它不追求成为完整的任务管理套件，最重要的价值是让紧急任务以很低的交互成本保持可见。

DDL Reminder should feel light, quiet, and persistently visible. It should not become a full productivity suite. Its strongest value is keeping urgent tasks visible with very little interaction cost.
