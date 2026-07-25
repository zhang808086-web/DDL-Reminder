# 手动验收清单 / Manual Test Checklist

发布前可以使用这份清单进行手动验证。

Use this checklist before creating a release build.

## 主窗口 / Main Window

- 创建带标题、描述、日期和时间的任务 / Create a task with title, description, date, and time
- 创建不带描述的任务 / Create a task without description
- 编辑标题、描述、日期和时间 / Edit title, description, date, and time
- 非法标题会提示错误，并保持弹窗打开 / Invalid title shows an error and keeps the dialog open
- 完成进行中的任务 / Complete an active task
- 恢复已完成任务 / Restore a completed task
- 删除进行中任务时出现确认 / Delete an active task after confirmation
- 删除已完成任务时出现确认 / Delete a completed task after confirmation
- 进行中、已完成、紧急筛选展示正确 / Active, completed, and urgent filters show the expected tasks
- 搜索可以按标题或描述过滤任务 / Search filters tasks by title or description

## 悬浮窗 / Floating Window

- 最多显示三个紧急未完成任务 / Shows at most three urgent active tasks
- 显示剩余时间或逾期时间 / Displays remaining time or overdue time
- 点击任务打开任务详情 / Clicking a task opens task detail
- 从悬浮窗编辑任务后主窗口立即刷新 / Editing from the floating window refreshes the main window immediately
- 从主窗口完成、恢复、删除任务后悬浮窗立即刷新 / Completing, restoring, or deleting from the main window refreshes the floating window immediately
- 定时刷新会更新剩余时间 / Timer refresh updates remaining time
- 移动后保存位置 / Position is saved after moving
- 固定按钮会禁用自动收起 / Pin button disables auto-hide
- 未固定时可以贴边吸附 / Unpinned window snaps to screen edges
- 左、右、上、下四个边缘都能自动收起 / Auto-hide works on left, right, top, and bottom edges
- 托盘菜单可以重新显示隐藏或收起的悬浮窗 / Tray menu can show the floating window after it is hidden or collapsed

## 提醒 / Reminder

- 24 小时内任务触发一次 24 小时提醒 / A task within 24 hours triggers one 24-hour reminder
- 1 小时内任务触发一次 1 小时提醒 / A task within 1 hour triggers one 1-hour reminder
- 已提醒过的任务不会重复触发同类提醒 / A task already reminded does not repeat the same reminder
- 逾期任务触发逾期提醒 / An overdue task triggers an overdue reminder
- 已发过 1 小时提醒的任务，逾期后仍可触发逾期提醒 / A task that received the 1-hour reminder can still receive the overdue reminder
- 已完成任务不会触发提醒 / Completed tasks do not trigger reminders
- 通知失败会写日志，不会导致应用崩溃 / Notification failure is logged and does not crash the app

## Windows 集成 / Windows Integration

- 关闭主窗口时隐藏而不是退出 / Closing the main window hides it instead of exiting the app
- 托盘菜单可以显示主窗口 / Tray menu can show the main window
- 双击托盘图标打开主窗口 / Tray double-click opens the main window
- 托盘菜单可以显示悬浮窗 / Tray menu can show the floating window
- 托盘退出会真正退出应用 / Tray exit actually quits the app
- 启动第二个实例不会打开另一个应用实例 / Starting a second instance does not open another app instance
- 设置页可以开启开机自启 / Autostart can be enabled from settings
- 托盘菜单可以开启开机自启 / Autostart can be enabled from the tray menu
- 设置页和托盘菜单的自启状态保持同步 / Autostart setting stays synchronized between settings and tray
- Windows 登录后应用自动启动，并显示悬浮窗 / After Windows login, the app starts with the floating window visible

## 打包 / Packaging

- 打包命令成功完成 / Build command completes successfully
- `dist/DDL-Reminder/DDL-Reminder.exe` 可以正常启动 / `dist/DDL-Reminder/DDL-Reminder.exe` starts normally
- 打包后应用使用 AppData 数据库路径 / Packaged app uses AppData database path
- 打包后应用使用 AppData 日志路径 / Packaged app uses AppData log path
- 不出现开发用终端窗口 / No development-only terminal window appears
- 新环境启动时数据库为空 / Fresh install starts with an empty database
- 重新打包不会覆盖已有 AppData 数据库 / Existing AppData database is not overwritten by rebuilding the exe
