# DDL Reminder Architecture

## 1. 文档目的

本文档描述 DDL Reminder 的整体架构、模块职责、依赖方向、核心数据流和技术边界。

DDL Reminder 是一个运行于 Windows 11 的本地桌面任务管理应用。它包含：

* 一个用于创建、编辑和管理任务的主窗口
* 一个始终置顶、展示最近三个紧迫任务的悬浮窗
* Windows 系统通知
* 系统托盘
* 开机自动启动
* 本地 SQLite 数据持久化

本项目同时用于恢复 Python 编码能力，并练习真实工程开发中的分层、测试、异常处理、日志、数据库迁移和应用打包。

架构设计遵循以下原则：

1. 保持单体应用，不引入不必要的分布式组件。
2. 核心业务逻辑应能够脱离 GUI 和数据库独立测试。
3. UI 不直接访问数据库。
4. 业务规则不依赖 PySide6、SQLAlchemy 或 Windows API。
5. 技术实现可以替换，但业务层尽量保持稳定。
6. 先实现简单正确的版本，再根据真实需求重构。

---

## 2. 架构类型

项目采用轻量分层单体架构。

整个应用运行在一个 Python 进程中，使用一个本地 SQLite 数据库。Qt 事件循环负责窗口交互、定时刷新和提醒检查。

整体结构如下：

```text
┌─────────────────────────────────────┐
│ UI Layer                            │
│ 主窗口、悬浮窗、任务弹窗、系统托盘    │
└──────────────────┬──────────────────┘
                   │ 调用
┌──────────────────▼──────────────────┐
│ Application Layer                   │
│ TaskService、ReminderService         │
│ StartupService                      │
└───────────────┬─────────────────────┘
                │ 使用
┌───────────────▼─────────────────────┐
│ Domain Layer                        │
│ Task、DeadlineStatus、业务规则、异常  │
└─────────────────────────────────────┘

Application Layer
        │
        │ 调用抽象接口
        ▼
┌─────────────────────────────────────┐
│ Ports / Repository Interfaces       │
│ TaskRepository、NotificationPort     │
│ StartupPort                         │
└──────────────────▲──────────────────┘
                   │ 实现
┌──────────────────┴──────────────────┐
│ Infrastructure Layer                │
│ SQLite、SQLAlchemy、Windows 通知      │
│ 开机启动、日志、配置                  │
└─────────────────────────────────────┘
```

主要调用方向：

```text
UI → Application → Domain
                 → Ports

Infrastructure → Ports 的具体实现
```

Domain 层不依赖其他层。

---

## 3. 技术选择

第一版采用以下技术：

* Python 3.11 或更高版本
* PySide6：桌面 GUI
* SQLite：本地数据库
* SQLAlchemy 2.x：数据库访问
* Alembic：数据库迁移
* pytest：自动化测试
* logging：日志记录
* QSettings：窗口位置和 UI 偏好
* PyInstaller：Windows 可执行文件打包

第一版不使用：

* FastAPI
* Redis
* 消息队列
* 微服务
* 云数据库
* Docker
* 复杂依赖注入框架
* 事件总线框架
* Unit of Work
* CQRS

这些技术目前不能解决项目中的真实问题，因此不引入。

---

## 4. 目录结构

目标目录结构如下：

```text
ddl-reminder/
├── src/
│   └── ddl_reminder/
│       ├── main.py
│       ├── config.py
│       │
│       ├── domain/
│       │   ├── task.py
│       │   ├── deadline.py
│       │   └── exceptions.py
│       │
│       ├── application/
│       │   ├── task_service.py
│       │   ├── reminder_service.py
│       │   └── startup_service.py
│       │
│       ├── ports/
│       │   ├── task_repository.py
│       │   ├── notification_port.py
│       │   └── startup_port.py
│       │
│       ├── infrastructure/
│       │   ├── database.py
│       │   ├── models.py
│       │   ├── sqlalchemy_task_repository.py
│       │   ├── windows_notification.py
│       │   ├── windows_startup.py
│       │   └── logging_config.py
│       │
│       └── ui/
│           ├── main_window.py
│           ├── floating_window.py
│           ├── task_dialog.py
│           ├── task_list_widget.py
│           └── tray.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fakes/
│
├── migrations/
├── AGENTS.md
├── PRODUCT.md
├── ARCHITECTURE.md
├── ROADMAP.md
├── README.md
└── pyproject.toml
```

目录应随功能逐步创建，不要求项目开始时建立所有空文件。

---

## 5. Domain Layer

Domain 层描述核心业务概念和规则。

这一层不关心任务如何显示、如何存储，也不关心 Windows 通知如何实现。

Domain 层禁止依赖：

* PySide6
* SQLAlchemy
* SQLite
* Windows API
* 日志配置
* 文件系统路径

### 5.1 Task

`Task` 表示一个任务。

主要字段：

```text
id
title
description
deadline
is_completed
completed_at
created_at
updated_at
notified_24h
notified_1h
```

建议使用 `dataclass` 定义领域对象。

字段含义：

* `id`：任务唯一标识。任务尚未持久化时允许为空。
* `title`：任务标题，不能为空。
* `description`：可选描述。
* `deadline`：完整的截止日期时间。
* `is_completed`：任务是否完成。
* `completed_at`：任务完成时间。
* `created_at`：创建时间。
* `updated_at`：最后更新时间。
* `notified_24h`：是否已经发送过 24 小时提醒。
* `notified_1h`：是否已经发送过 1 小时提醒。

第一版使用偏简单的领域模型。

任务创建、编辑、完成和恢复的流程主要由 `TaskService` 编排。只有明显属于对象本身的简单状态变化，才考虑作为 `Task` 的方法。

### 5.2 Deadline 规则

`domain/deadline.py` 负责所有截止时间相关规则。

包括：

* 合并日期和可选时间
* 未填写时间时使用当天 23:59
* 判断任务是否逾期
* 计算距离 DDL 的秒数
* 判断任务紧迫程度
* 判断是否进入提醒区间
* 生成与展示无关的时间状态结果

建议定义：

```text
DeadlineCategory
├── OVERDUE
├── WITHIN_ONE_HOUR
├── WITHIN_ONE_DAY
├── WITHIN_THREE_DAYS
└── NORMAL
```

Domain 层只返回状态和时间数据，不返回 UI 颜色。

例如：

```text
OVERDUE
seconds_remaining = -7200
```

UI 根据 `OVERDUE` 决定使用红色样式。

时间计算函数必须允许显式传入 `now`，避免在函数内部直接固定使用当前系统时间。

这样可以测试：

* 正好剩余 24 小时
* 正好剩余 1 小时
* 刚刚逾期
* 跨天
* 没有填写时间
* 系统时间变化

### 5.3 业务异常

业务异常统一定义在：

```text
domain/exceptions.py
```

第一版可包含：

```text
TaskError
TaskNotFoundError
InvalidTaskTitleError
InvalidDeadlineError
```

是否对重复完成任务抛异常，由业务规则决定。

第一版建议让“完成任务”具有幂等性：

* 未完成任务执行完成操作时，更新状态。
* 已完成任务再次执行完成操作时，直接返回当前任务。
* 不抛出错误。

这样可以避免用户重复点击按钮造成无意义报错。

---

## 6. Application Layer

Application 层负责执行完整业务用例。

这一层负责回答：

> 用户发起一个操作后，系统应该按照什么顺序完成？

Application 层可以依赖：

* Domain 对象和规则
* Repository 或 Port 接口

Application 层禁止：

* 直接执行 SQL
* 操作具体 Qt 控件
* 直接访问 Windows 注册表
* 直接依赖具体通知库
* 决定字体、颜色和窗口布局

### 6.1 TaskService

`TaskService` 负责任务管理用例。

主要方法：

```text
create_task
update_task
complete_task
restore_task
delete_task
get_task
list_active_tasks
list_completed_tasks
get_urgent_tasks
```

#### 创建任务

流程：

```text
接收用户输入
→ 校验标题
→ 合并日期和可选时间
→ 未填写时间时设置为 23:59
→ 创建 Task
→ 调用 Repository 保存
→ 返回保存后的 Task
```

#### 更新任务

流程：

```text
根据 task_id 查询任务
→ 任务不存在则抛出 TaskNotFoundError
→ 校验新的标题和 DDL
→ 修改任务
→ 更新 updated_at
→ 调用 Repository 保存
→ 返回更新后的 Task
```

如果用户修改 DDL，应该重置：

```text
notified_24h = False
notified_1h = False
```

否则任务的新截止时间可能无法触发提醒。

#### 完成任务

流程：

```text
查询任务
→ 不存在则抛出 TaskNotFoundError
→ 如果已经完成，直接返回
→ 设置 is_completed = True
→ 设置 completed_at
→ 设置 updated_at
→ 保存任务
```

已完成任务：

* 不出现在进行中列表
* 不出现在悬浮窗
* 不再触发提醒

#### 恢复任务

流程：

```text
查询任务
→ 设置 is_completed = False
→ 清空 completed_at
→ 更新 updated_at
→ 根据当前时间决定是否重置提醒状态
→ 保存任务
```

第一版建议恢复任务时重置两个提醒状态，使其仍有机会提醒。

#### 获取最紧迫任务

规则：

* 只查询未完成任务
* 按 `deadline` 升序排列
* DDL 相同时按 `created_at` 升序排列
* 最多返回指定数量
* 悬浮窗默认请求三个任务

因为逾期任务的 deadline 早于未来任务，所以按 deadline 升序已经自然满足“逾期任务优先”。

### 6.2 ReminderService

`ReminderService` 负责提醒检查和发送流程。

它依赖：

* `TaskRepository`
* `NotificationPort`

主要方法：

```text
check_reminders(now)
```

执行流程：

```text
查询所有未完成任务
→ 计算每个任务与当前时间的差值
→ 判断是否应该发送 24 小时提醒
→ 判断是否应该发送 1 小时提醒
→ 检查提醒是否已经发送
→ 调用 NotificationPort
→ 通知成功后更新提醒状态
```

提醒规则：

* 到期前 24 小时提醒一次
* 到期前 1 小时提醒一次
* 同一类提醒不能重复发送
* 已完成任务不提醒
* 程序关闭期间错过提醒时，启动后补发
* 通知失败时记录日志，并保留未发送状态

补发规则建议：

* 当前时间已经进入 24 小时区间，且 `notified_24h` 为 False，则发送 24 小时提醒。
* 当前时间已经进入 1 小时区间，且 `notified_1h` 为 False，则发送 1 小时提醒。
* 如果任务已经逾期，不再补发 24 小时或 1 小时提醒。

通知成功后再更新数据库状态。

第一版允许极低概率下重复通知，例如通知已经发送，但程序在更新数据库前崩溃。暂不为此引入复杂的 exactly-once 机制。

### 6.3 StartupService

`StartupService` 管理 Windows 开机启动。

它依赖：

```text
StartupPort
```

主要方法：

```text
enable_startup
disable_startup
is_startup_enabled
```

StartupService 不直接操作注册表。

具体的 Windows 实现放在 Infrastructure 层。

---

## 7. Ports

Ports 描述 Application 层需要哪些外部能力。

它们只定义接口，不包含具体技术实现。

第一版建议使用 Python `Protocol`。

### 7.1 TaskRepository

主要接口：

```text
add(task) -> Task
update(task) -> Task
get_by_id(task_id) -> Task
list_all() -> list[Task]
delete(task_id) -> None
```

Repository 负责：

* 保存任务
* 查询任务
* 删除任务
* 将数据库模型转换成领域对象
* 在找不到任务时抛出 `TaskNotFoundError`

Repository 不负责：

* 判断标题是否合法
* 计算任务是否逾期
* 区分进行中任务和已完成任务
* 决定最紧迫任务的业务排序
* 发送通知
* 修改 UI

`list_active_tasks()`、`list_completed_tasks()` 和 `get_urgent_tasks(limit)` 属于 `TaskService` 的用例方法。
第一版先由 `TaskService` 调用 `list_all()` 后完成筛选和排序，避免 Repository 过早承载业务规则。
如果后续 SQLite 查询性能成为真实问题，再在保持业务语义清晰的前提下调整 Repository 查询能力。

### 7.2 NotificationPort

接口：

```text
send(title, message) -> None
```

Application 层不关心具体使用哪个 Windows 通知库。

测试时可以使用 Fake 实现，记录发送过的通知。

### 7.3 StartupPort

接口：

```text
enable() -> None
disable() -> None
is_enabled() -> bool
```

Infrastructure 层提供 Windows 具体实现。

---

## 8. Infrastructure Layer

Infrastructure 层负责具体技术实现。

包括：

* SQLAlchemy
* SQLite
* Windows 系统通知
* Windows 开机启动
* 日志
* 应用配置
* 用户数据目录

### 8.1 Database

`infrastructure/database.py` 负责：

* 创建 SQLAlchemy Engine
* 创建 Session 工厂
* 构造数据库连接地址
* 初始化数据库连接
* 提供数据库 Session

数据库文件应位于 Windows 当前用户的数据目录，而不是程序安装目录。

建议路径：

```text
%APPDATA%/DDLReminder/ddl_reminder.db
```

原因：

* 安装目录可能没有写入权限
* 程序升级不应覆盖用户数据
* 打包后的 exe 运行目录可能变化
* 用户数据应与可执行文件分离

### 8.2 ORM Models

`infrastructure/models.py` 定义 SQLAlchemy ORM 模型。

领域对象和数据库模型分开：

```text
Task        领域对象
TaskModel   数据库模型
```

两者职责不同：

* `Task` 表达业务含义。
* `TaskModel` 表达数据库表结构。

Repository 负责转换：

```text
TaskModel → Task
Task → TaskModel
```

第一版不引入额外 Mapper 框架。

### 8.3 SQLAlchemyTaskRepository

`SQLAlchemyTaskRepository` 实现 `TaskRepository`。

职责：

* 执行查询
* 执行插入、更新和删除
* commit
* 数据库失败时 rollback
* ORM Model 与 Domain Task 转换

第一版事务策略：

* 每个 Repository 写操作内部完成一次事务。
* 操作成功后 commit。
* 操作失败后 rollback 并重新抛出异常。

暂不引入 Unit of Work。

### 8.4 WindowsNotificationAdapter

负责调用 Windows 通知能力。

它实现：

```text
NotificationPort
```

通知发送失败时：

* 抛出基础设施异常
* ReminderService 捕获并记录日志
* 不更新任务的已提醒状态
* 不导致整个 GUI 程序退出

具体通知库需通过技术验证后确定。

### 8.5 WindowsStartupAdapter

负责 Windows 开机启动。

第一版优先考虑当前用户级注册表启动项，不要求管理员权限。

需要验证：

* 开发环境下启动 Python 模块
* PyInstaller 打包后启动 exe
* 可执行文件路径包含空格时的行为
* 用户移动 exe 后启动项如何处理

### 8.6 Settings

窗口位置、悬浮窗显示状态等 UI 偏好使用 `QSettings`。

适合放入 QSettings 的内容：

* 悬浮窗位置
* 悬浮窗是否显示
* 主窗口大小
* 是否开启开机启动

任务本身属于业务数据，必须存入 SQLite。

不要求所有 UI 配置都经过 Application Service。

---

## 9. UI Layer

UI 层使用 PySide6。

职责：

* 创建和展示窗口
* 接收输入
* 响应用户点击
* 调用 Service
* 显示结果
* 将业务异常转换为用户可理解的提示

UI 层禁止：

* 直接执行 SQL
* 自己判断提醒区间
* 在多个窗口重复实现 DDL 计算
* 自己创建 Repository 或数据库 Engine
* 将数据库 Session 保存在窗口中

### 9.1 MainWindow

主窗口负责：

* 显示进行中任务
* 显示已完成任务
* 打开创建任务弹窗
* 打开编辑任务弹窗
* 完成任务
* 恢复任务
* 删除任务
* 隐藏到系统托盘

MainWindow 持有：

```text
TaskService
```

MainWindow 不持有：

```text
Database Session
SQLAlchemy Engine
SQLAlchemy Model
```

### 9.2 TaskDialog

TaskDialog 负责采集：

* 标题
* 描述
* 日期
* 可选时间

TaskDialog 返回用户输入，不直接保存数据库。

建议使用输入对象：

```text
TaskFormData
├── title
├── description
├── deadline_date
└── deadline_time
```

### 9.3 FloatingWindow

悬浮窗负责：

* 始终置顶
* 最多显示三个任务
* 显示任务标题
* 显示剩余或逾期状态
* 根据 DeadlineCategory 设置样式
* 点击任务后打开主窗口
* 保存窗口位置
* 定时刷新显示

悬浮窗调用：

```text
TaskService.get_urgent_tasks(limit=3)
```

悬浮窗不直接访问数据库。

### 9.4 SystemTray

系统托盘负责：

* 打开主窗口
* 显示悬浮窗
* 隐藏悬浮窗
* 退出应用

关闭主窗口默认行为是隐藏，而不是退出程序。

只有托盘菜单中的“退出”操作真正结束应用。

### 9.5 UI 刷新

第一版不引入事件总线框架。

使用 Qt Signal 完成窗口刷新。

示例数据流：

```text
任务创建成功
→ 发出 tasks_changed 信号
→ MainWindow 刷新列表
→ FloatingWindow 刷新最近任务
```

主窗口和悬浮窗不直接修改对方内部状态。

它们通过重新调用 Service 获取最新数据。

---

## 10. Composition Root

`main.py` 是应用的 Composition Root。

它负责创建并连接所有组件。

主要流程：

```text
初始化 QApplication
→ 配置日志
→ 加载配置
→ 创建数据库 Engine 和 SessionFactory
→ 创建 SQLAlchemyTaskRepository
→ 创建 WindowsNotificationAdapter
→ 创建 WindowsStartupAdapter
→ 创建 TaskService
→ 创建 ReminderService
→ 创建 StartupService
→ 创建 MainWindow
→ 创建 FloatingWindow
→ 创建 SystemTray
→ 连接 Qt Signals
→ 启动提醒定时器
→ 进入 Qt 事件循环
```

窗口和 Service 不应在内部自行创建依赖。

依赖通过构造函数传入。

例如：

```text
MainWindow(task_service)
FloatingWindow(task_service)
ReminderService(task_repository, notification_port)
```

---

## 11. 核心业务流程

### 11.1 创建任务

```text
用户打开 TaskDialog
→ 输入标题、描述、日期和可选时间
→ UI 将 TaskFormData 传给 TaskService
→ TaskService 校验标题
→ TaskService 规范化 deadline
→ TaskService 创建 Task
→ Repository 写入 SQLite
→ 返回保存后的 Task
→ UI 关闭弹窗
→ 发出 tasks_changed 信号
→ 主窗口与悬浮窗刷新
```

### 11.2 完成任务

```text
用户点击完成
→ UI 调用 TaskService.complete_task(task_id)
→ Service 查询任务
→ 任务不存在则抛业务异常
→ 设置完成状态和完成时间
→ Repository 保存
→ UI 发出 tasks_changed 信号
→ 任务从进行中列表和悬浮窗消失
→ 任务出现在已完成页面
```

### 11.3 恢复任务

```text
用户在已完成页面点击恢复
→ TaskService.restore_task(task_id)
→ 清除完成状态
→ 清除 completed_at
→ 重置提醒状态
→ Repository 保存
→ UI 刷新
```

### 11.4 删除任务

```text
用户点击删除
→ UI 显示确认提示
→ TaskService.delete_task(task_id)
→ Repository 删除记录
→ UI 刷新
```

删除操作是真实删除，不保留回收站。

### 11.5 提醒检查

```text
QTimer 每分钟触发
→ ReminderService.check_reminders(now)
→ 查询未完成任务
→ 计算每个任务的剩余时间
→ 判断是否需要发送提醒
→ 调用 WindowsNotificationAdapter
→ 成功后更新提醒状态
```

### 11.6 应用启动

```text
应用启动
→ 初始化数据库
→ 创建窗口和托盘
→ 主窗口默认隐藏
→ 显示悬浮窗
→ 加载窗口位置
→ 检查错过的提醒
→ 启动每分钟提醒检查
```

---

## 12. 数据模型

第一版包含一张 `tasks` 表。

建议字段：

```text
id               INTEGER PRIMARY KEY
title            TEXT NOT NULL
description      TEXT NULL
deadline         DATETIME NOT NULL
is_completed     BOOLEAN NOT NULL
completed_at     DATETIME NULL
notified_24h     BOOLEAN NOT NULL
notified_1h      BOOLEAN NOT NULL
created_at       DATETIME NOT NULL
updated_at       DATETIME NOT NULL
```

建议索引：

```text
deadline
is_completed, deadline
```

主要查询：

```text
查询所有任务
根据 ID 查询任务
```

数据库结构变化由 Alembic 管理。

生产数据不得通过删除数据库重新初始化的方式升级。

---

## 13. 时间处理

第一版按 Windows 当前本地时间运行。

数据库中的 datetime 统一采用同一种策略，禁止一部分使用本地时间、一部分使用 UTC。

第一版推荐：

* Domain 和 Application 中使用无时区的本地 datetime。
* 所有时间均来自统一的时间获取入口。
* 测试中显式传入固定 now。
* 后续若加入云同步，再迁移为 UTC 存储。

所有 DDL 显示和提醒逻辑必须共用同一套 Deadline 领域函数。

不允许主窗口、悬浮窗和提醒服务分别实现自己的时间计算。

---

## 14. 异常处理

异常分为三类。

### 14.1 业务异常

例如：

* 标题为空
* 任务不存在
* DDL 输入无效

业务异常由 Domain 或 Application 层抛出。

UI 捕获后显示清晰提示。

### 14.2 基础设施异常

例如：

* 数据库无法打开
* 数据库提交失败
* Windows 通知发送失败
* 开机启动注册失败

基础设施层应保留原始异常信息，并记录日志。

用户界面只显示可理解的信息，不直接展示完整堆栈。

### 14.3 未知异常

应用入口应设置最后一道异常保护。

发生未知错误时：

* 记录完整堆栈
* 尽量显示错误提示
* 避免静默退出
* 不使用 `except Exception: pass`

---

## 15. 日志

日志至少记录：

* 应用启动和退出
* 数据库初始化
* 任务创建、完成、恢复和删除
* 提醒发送成功或失败
* 开机启动设置变化
* 未处理异常

日志不得记录：

* 敏感 Token
* 用户隐私数据的完整内容
* 无必要的重复调试信息

日志文件应存放在用户数据目录下。

---

## 16. 测试策略

### 16.1 Domain 单元测试

测试：

* 未填写时间时默认 23:59
* 判断逾期
* 剩余 24 小时边界
* 剩余 1 小时边界
* 剩余时间分类
* DDL 排序规则

### 16.2 Application 单元测试

使用 Fake Repository 和 Fake Notification。

测试：

* 创建任务
* 编辑任务
* 完成任务
* 重复完成
* 恢复任务
* 删除任务
* 查询最近三个任务
* 24 小时提醒不重复
* 1 小时提醒不重复
* 已完成任务不提醒
* 通知失败时不更新提醒状态

### 16.3 Repository 集成测试

使用临时 SQLite 数据库。

测试：

* 任务保存后可以查询
* 更新可以持久化
* 删除可以持久化
* 查询全部任务时包含进行中和已完成任务
* 查询不存在的任务时抛出 `TaskNotFoundError`
* 数据库失败后事务回滚

### 16.4 GUI 手工测试

第一版主要手工验证：

* 悬浮窗始终置顶
* 悬浮窗可拖动
* 窗口位置可以恢复
* 托盘打开和隐藏窗口
* 主窗口关闭后应用继续运行
* Windows 通知正常
* 开机启动正常
* PyInstaller 打包后正常启动

GUI 自动化测试不是第一版重点。

---

## 17. 性能和可靠性

这是本地个人应用，数据量预计较小。

第一版不进行复杂缓存。

性能要求：

* 常见操作应立即响应
* 悬浮窗刷新不能明显卡顿
* 每分钟提醒检查不阻塞 UI
* 第一版数据量较小，最近三个任务可以由 `TaskService` 在内存中筛选和排序

如果通知检查或数据库操作后续出现明显阻塞，再考虑使用线程或 Qt Worker。

第一版不提前引入异步架构。

---

## 18. 安全和数据保护

第一版不包含账号和网络通信。

主要风险是本地数据丢失和文件权限问题。

需要保证：

* 数据库放在用户数据目录
* 程序升级不覆盖数据库
* 数据库迁移有明确版本
* 删除操作需要用户确认
* 日志不保存不必要的任务描述
* 应用不要求管理员权限

后续可以考虑加入数据库备份和导出功能，但不属于第一版。

---

## 19. 架构约束

开发过程中必须遵守：

1. UI 不直接执行 SQL。
2. UI 不直接使用 SQLAlchemy Model。
3. Domain 不导入 PySide6。
4. Domain 不导入 SQLAlchemy。
5. ReminderService 不直接依赖具体通知库。
6. TaskService 不直接操作窗口。
7. 所有 DDL 时间计算集中在 Domain。
8. 组件依赖由 `main.py` 统一组装。
9. 不为未确认的未来需求增加抽象。
10. 核心逻辑必须能够自动化测试。

---

## 20. 待验证技术问题

以下问题需要通过小型技术实验确认：

* Windows 通知最终使用哪个 Python 库。
* PyInstaller 打包后系统通知是否正常。
* 开机启动使用注册表还是启动文件夹。
* 打包后如何稳定获取 exe 路径。
* PyInstaller 打包后 Alembic 和数据库迁移如何执行。
* Windows 休眠恢复后 QTimer 是否会立即补执行。
* 数据库 datetime 的序列化行为。
* 单实例运行采用哪种实现。
* 应用崩溃时日志文件是否能正常写入。

在技术验证完成前，不在架构文档中假设这些方案已经确定。

---

## 21. 第一阶段实现范围

第一阶段只实现 Domain 层，不实现 GUI 和数据库。

范围包括：

* `Task`
* DDL 日期时间规范化
* `DeadlineCategory`
* 剩余和逾期时间计算
* 提醒区间判断
* 业务异常
* Domain 单元测试

第一阶段完成标准：

* 不导入 PySide6
* 不导入 SQLAlchemy
* 所有时间逻辑可以传入固定 now
* 所有关键边界有 pytest 测试
* 开发者能够解释每个函数的输入、输出和异常路径

后续阶段按照 `ROADMAP.md` 逐步推进。
