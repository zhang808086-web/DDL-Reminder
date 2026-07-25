phase1 接口设计草稿：

1.domain/task.py

Task:
- 字段:
'''text
id
title
description
deadline
created_at
updated_at
is_completed
completed_at
notified_24h
notified_1h
'''

- title description deadline is_completed应该是人创建任务时操作的，而其他的应该由系统进行填写
- 状态变化，比如mark_completed()放在Task中，但是由TaskService去调用


2. domain/deadline.py

deadline.py 对外暴露的函数:

```python
classify_deadline(deadline: datetime, now: datetime) -> tuple[DeadlineCategory, int]

normalize_deadline(deadline_date: date, deadline_time: time | None = None) -> datetime

format_remaining_time(deadline: datetime, now: datetime) -> str
```

DeadlineCategory:

```text
OVERDUE
WITHIN_ONE_HOUR
WITHIN_ONE_DAY
WITHIN_THREE_DAYS
NORMAL
```

classify_deadline:
- input: deadline, now
- deadline: datetime, now: datetime
- output: 一个枚举值 + 时间差 seconds_diff
- seconds_diff = deadline - now 的总秒数
- seconds_diff 为正数表示还没到期，0 或负数表示已经逾期

分类规则:

| 条件 | 分类 |
| --- | --- |
| seconds_diff <= 0 | OVERDUE |
| 0 < seconds_diff <= 3600 | WITHIN_ONE_HOUR |
| 3600 < seconds_diff <= 86400 | WITHIN_ONE_DAY |
| 86400 < seconds_diff <= 259200 | WITHIN_THREE_DAYS |
| seconds_diff > 259200 | NORMAL |

边界:
- seconds_diff == 0 -> OVERDUE
- seconds_diff == 3600 -> WITHIN_ONE_HOUR
- seconds_diff == 86400 -> WITHIN_ONE_DAY
- seconds_diff == 259200 -> WITHIN_THREE_DAYS
- 不增加 WITHIN_ONE_MINUTE，分钟级别只是显示细节，不作为紧迫程度分类


- 没填时间: normalize_deadline(deadline_date, deadline_time = None) -> datetime
放在deadline.py,在TaskService中调用
- deadline_time 为 None 时，默认使用 23:59
- if deadline_date = None 不予创建，抛出InvalidDeadlineError
- 这个函数只负责 date + time -> datetime，不负责创建 Task
- 逾期 < 1h 显示已逾期 0 h

- format_remaining_time(deadline, now) -> str:
- 负责把时间差转换成给用户看的字符串
- DeadlineCategory 决定紧迫程度，format_remaining_time 决定怎么显示
- 向下取整

格式化规则:

| 条件 | 输出格式 | 示例 |
| --- | --- | --- |
| seconds_diff <= -86400 | 已逾期 X 天 | -25h -> 已逾期 1 天 |
| -86400 < seconds_diff <= 0 | 已逾期 X 小时 | -1h30min -> 已逾期 1 小时 |
| seconds_diff >= 86400 | 剩余 X 天 | 25h -> 剩余 1 天 |
| 3600 <= seconds_diff < 86400 | 剩余 X 小时 | 23h59min -> 剩余 23 小时 |
| 0 < seconds_diff < 3600 | 剩余 X 分钟 | 59s -> 剩余 0 分钟 |

注意:
- format_remaining_time 可以显示分钟，但 DeadlineCategory 不需要 WITHIN_ONE_MINUTE
- UI 不自己计算 deadline - now，只使用 deadline.py 的结果




3. domain/exceptions.py
- 异常应当抛出具体的异常种类并显示在UI

- TaskError(基类)
TaskNotFoundError(TaskError) -> Task查不到
InvalidTaskTitleError(TaskError) -> Title为空，Title超过长度限制，长度限制为15字，Title全为空白字符
InvalidDeadlineError(TaskError) -> deadline_date = None


phase2 接口设计:

TaskService:

```text
TaskService(repository: TaskRepository)
```

- TaskService 通过构造函数接收 TaskRepository。
- TaskService 不在方法内部创建 Repository。
- 测试时可以传入 InMemoryTaskRepository 或 FakeRepository。
- 未来 Phase 3 可以传入 SQLAlchemyTaskRepository。

```text
create_task(
    title: str,
    deadline_date: date,
    deadline_time: time | None = None,
    description: str = "",
    now: datetime | None = None,
) -> Task
update_task(
    task_id: int,
    title: str | None = None,
    description: str | None = None,
    deadline_date: date | None = None,
    deadline_time: time | None = None,
    now: datetime | None = None,
) -> Task
complete_task(task_id: int, now: datetime) -> Task
restore_task(task_id: int, now: datetime) -> Task
delete_task(task_id: int) -> None
get_task(task_id: int) -> Task
list_active_tasks() -> list[Task]
list_completed_tasks() -> list[Task]
get_urgent_tasks(limit: int = 3) -> list[Task]
```

时间参数规则：

- create_task 和 update_task 接收 now: datetime | None = None。
- 当 now 为 None 时，TaskService 内部使用 datetime.now()。
- 当测试需要固定时间时，测试代码显式传入 now。
- create_task 使用 now 设置 created_at 和 updated_at。
- update_task 使用 now 设置 updated_at。

create_task：

- description 默认为空字符串。
- deadline_date 必填，deadline_time 可选。
- deadline 由 normalize_deadline(deadline_date, deadline_time) 生成。
- 创建 Task 后调用 Repository 保存。

update_task：

- 不允许修改 id。
- title、description 和 deadline 都可以选择性修改。
- title 不为 None 时，仍然需要满足 Task 的标题校验规则。
- description 不为 None 时，更新任务描述。
- deadline_date 和 deadline_time 都是可选参数。
- 如果只传 deadline_time，不传 deadline_date，则沿用原来的 deadline 日期。
- 如果只传 deadline_date，不传 deadline_time，则沿用原来的 deadline 时间。
- 如果 deadline 发生变化，则重置 notified_24h 和 notified_1h。
- updated_at 设置为 now。
- 修改后调用 Repository 保存。

list_active_tasks：

- 只返回 is_completed 为 False 的任务。
- 不包含已完成任务。

list_completed_tasks：

- 只返回 is_completed 为 True 的任务。

get_urgent_tasks：

- 只返回未完成任务。
- 按 deadline 升序排列。
- 如果 deadline 相同，按 created_at 升序排列。
- 最多返回 limit 个任务。
- 逾期任务因为 deadline 更早，会自然排在未逾期任务前面。



TaskRepository
主要接口：

```text
add(task) -> Task
update(task) -> Task
get_by_id(task_id) -> Task
list_all() -> list[Task]
delete(task_id) -> None
```

1. id由repositiory生成
2. get_by_id()找不到时，repository直接抛TaskNotFoundError
3. update保存这个任务当前状态
4. add(task) 总是分配新的 id。如果传入的 task 已经有 id，也会被 repository 覆盖为新的 id。



phase 6逻辑设计:
class Reminder:
    task_id: int
    title: str
    message: str
    level: enum{"24h", "1h" "overdue"}

已完成任务：不提醒

距离 deadline <= 1 小时：
- 如果 notified_1h 是 False，则生成 1h 提醒
- 然后设置 notified_1h = True
- 同时设置notified_24h = True,确保不同时发24h提醒和1h提醒

距离 deadline <= 24 小时：
- 如果 notified_24h 是 False，则生成 24h 提醒
- 然后设置 notified_24h = True

已逾期：
- 如果 notified_1h 是 False，可以生成 overdue 提醒
- 然后设置 notified_1h = True
- 避免启动时逾期任务无限重复弹













