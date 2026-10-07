# Qt Quick/QML UI Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace every Qt Widgets application window and dialog with a dark technology-style Qt Quick/QML interface while preserving the Python business layer, SQLite data, existing behavior, and Windows integrations, then ship and install `v0.2.0`.

**Architecture:** `main.py` continues to assemble the existing services and Windows integrations, then exposes a focused Python presentation layer to `QQmlApplicationEngine`. `TaskListModel`, `AppController`, and `FloatingWindowController` translate domain state and commands into QML-safe properties, roles, signals, and slots; QML owns all application windows, dialogs, and reusable visual components.

**Tech Stack:** Python 3.11+, PySide6 Qt Core/Gui/Widgets/Qml/Quick, Qt Quick Controls, SQLAlchemy, SQLite, PyInstaller, Inno Setup, pytest.

**Spec:** `docs/superpowers/specs/2026-10-07-qml-ui-migration-design.md`

## Global Constraints

- Release version is `0.2.0` and Git tag is `v0.2.0`.
- Keep the production database at `%APPDATA%/DDL-Reminder/tasks.db` with no schema migration.
- Preserve the existing domain, application, repository, reminder, tray, autostart, and single-instance behavior.
- Do not add statistics, snooze, accounts, synchronization, recurrence, or new reminder rules.
- Every application window and dialog must be QML; only the native system tray menu may remain Qt Widgets-based.
- Main-window tasks remain ordered by `(deadline, created_at)`.
- The floating window continues to show at most three earliest unfinished tasks and supports direct completion.
- README screenshots must be captured from the real QML application using synthetic data, never the production database.
- Preserve the PyInstaller root-level runtime DLL exclusions and Inno Setup `AppId`.
- Use the approved deep navy, cyan, violet, and deadline-category palette.

## Review Focus

- Invalid, empty, whitespace-only, and over-15-character titles must surface a QML error without closing the editor or mutating data.
- Date and time strings crossing the QML/Python boundary must reject malformed values and preserve entered form state.
- Complete/delete/restore operations must refresh both models immediately and retain deadline ordering.
- Floating geometry must handle saved off-screen positions, screen bounds, pinning, snapping, collapse, and tray restore.
- Source and packaged builds must resolve every QML file, icon, Qt Quick module, and plugin without network access or QML import errors.

---

### Task 1: Build the QML Task Presentation Model

**Files:**
- Create: `src/ddl_reminder/ui/task_list_model.py`
- Create: `tests/unit/test_task_list_model.py`

**Interfaces:**
- Consumes: `Task`, `DeadlineCategory`, `classify_deadline`, and `format_remaining_time`.
- Produces: `TaskListModel(QAbstractListModel)`, `replace_tasks(tasks: list[Task], now: datetime) -> None`, and roles `taskId`, `title`, `description`, `deadlineText`, `remainingText`, `category`, and `completed`. The model preserves the order supplied by the controller.

- [ ] **Step 1: Write failing model tests**

  Prove literal role values, empty-description normalization, completed/overdue values, and preservation of the supplied list order.

- [ ] **Step 2: Verify RED**

  Run: `python -m pytest tests/unit/test_task_list_model.py -q`

  Expected: FAIL because the module does not exist.

- [ ] **Step 3: Implement the minimal model**

  Implement explicit roles and `replace_tasks` using `beginResetModel()`/`endResetModel()` and the existing deadline functions.

- [ ] **Step 4: Verify GREEN and the suite**

  Run: `python -m pytest tests/unit/test_task_list_model.py -q`

  Run: `python -m pytest -q`

  Expected: all tests pass.

- [ ] **Step 5: Commit**

  `git commit -m "feat: add QML task list model"`

### Task 2: Add the Python Application Controller

**Files:**
- Create: `src/ddl_reminder/ui/app_controller.py`
- Create: `tests/unit/test_app_controller.py`
- Modify: `tests/unit/test_main_window.py`
- Modify: `tests/unit/test_floating_window.py`

**Interfaces:**
- Consumes: `TaskService`, `WindowsAutostart`, `build_autostart_command()`, `is_packaged_app()`, and `TaskListModel`.
- Produces: `AppController(QObject)` with `mainModel`, `floatingModel`, `currentFilter`, `sectionTitle`, `sectionCount`, and `autostartEnabled` properties; `tasksChanged`, `errorRequested(title, message)`, and `autostartChanged(enabled)` signals; and slots `setFilter(name)`, `setSearchQuery(query)`, `refreshTasks()`, `taskDetails(task_id)`, `createTask(...)`, `updateTask(...)`, `completeTask(task_id)`, `restoreTask(task_id)`, `deleteTask(task_id)`, and `setAutostart(enabled)`.

- [ ] **Step 1: Write failing query tests**

  Prove active/completed/urgent filtering, substring search, deterministic ordering, the three-task floating limit, and section metadata.

- [ ] **Step 2: Verify query tests fail**

  Run: `python -m pytest tests/unit/test_app_controller.py -q`

  Expected: FAIL because `AppController` does not exist.

- [ ] **Step 3: Implement query state and synchronized refresh**

  Add model properties, filter/search slots, `_tasks_for_current_filter(now: datetime) -> list[Task]`, and refresh both models from one service snapshot.

- [ ] **Step 4: Verify query tests pass**

  Run: `python -m pytest tests/unit/test_app_controller.py -q`

- [ ] **Step 5: Write failing command tests**

  Test create, update, complete, restore, delete, malformed ISO date/time values, domain title failures, success signals, failure signals, `False` results that keep dialogs open, and autostart rollback after `OSError`.

- [ ] **Step 6: Verify command tests fail for missing behavior**

  Run: `python -m pytest tests/unit/test_app_controller.py -q`

- [ ] **Step 7: Implement commands**

  Parse `YYYY-MM-DD` and `HH:MM` at the presentation boundary. Catch `TaskError`, `ValueError`, and autostart `OSError`; emit user-facing errors and refresh only after success.

- [ ] **Step 8: Replace obsolete QWidget behavior tests**

  Move time-ordering and direct-completion assertions into controller/model tests.

- [ ] **Step 9: Verify focused and full suites**

  Run: `python -m pytest tests/unit/test_app_controller.py tests/unit/test_task_list_model.py -q`

  Run: `python -m pytest -q`

- [ ] **Step 10: Commit**

  `git commit -m "feat: expose task workflows to QML"`

### Task 3: Preserve Floating-Window Native Behavior

**Files:**
- Create: `src/ddl_reminder/ui/floating_window_controller.py`
- Create: `tests/unit/test_floating_window_controller.py`

**Interfaces:**
- Consumes: a `QQuickWindow`, `QSettings`, screen geometry, cursor position, and app-controller refresh signals.
- Produces: `FloatingWindowController(QObject)` with `pinned` and `collapsed` properties; slots `attachWindow(window)`, `togglePinned()`, `showFromTray()`, `savePosition()`, `restorePosition()`, `beginDrag()`, and `finishDrag()`; plus pure helpers for clamp, edge selection, expanded position, and collapsed position.

- [ ] **Step 1: Write failing geometry tests**

  Cover left/right/top/bottom snapping, collapsed offsets, restored off-screen coordinates, exact thresholds, and pinned behavior with literal rectangles.

- [ ] **Step 2: Verify RED**

  Run: `python -m pytest tests/unit/test_floating_window_controller.py -q`

- [ ] **Step 3: Implement pure geometry helpers**

- [ ] **Step 4: Verify geometry tests pass**

- [ ] **Step 5: Write failing lifecycle tests**

  Test saved position, pin/unpin, collapse cooldown, tray expansion, and hide-on-close using a specific fake window matching the production geometry contract.

- [ ] **Step 6: Implement the controller**

  Attach to the QML window, observe move/enter/leave/close events, animate position, and retain compatible `QSettings("ddl-reminder", "ddl-reminder")` state.

- [ ] **Step 7: Verify focused and full suites**

  Run: `python -m pytest tests/unit/test_floating_window_controller.py -q`

  Run: `python -m pytest -q`

- [ ] **Step 8: Commit**

  `git commit -m "feat: preserve floating window behavior for QML"`

### Task 4: Build the Shared Theme and Main QML Window

**Files:**
- Create: `src/ddl_reminder/ui/qml_resources.py`
- Create: `src/ddl_reminder/ui/qml/qmldir`
- Create: `src/ddl_reminder/ui/qml/Theme.qml`
- Create: `src/ddl_reminder/ui/qml/Main.qml`
- Create: `src/ddl_reminder/ui/qml/components/AppButton.qml`
- Create: `src/ddl_reminder/ui/qml/components/WindowButton.qml`
- Create: `src/ddl_reminder/ui/qml/components/NavigationButton.qml`
- Create: `src/ddl_reminder/ui/qml/components/TaskCard.qml`
- Create: `src/ddl_reminder/ui/qml/components/StatusChip.qml`
- Create: `tests/unit/test_qml_resources.py`
- Create: `tests/integration/test_qml_loading.py`

**Interfaces:**
- Consumes: context properties named `appController` and `floatingWindowController` plus local assets.
- Produces: `qml_path(name: str) -> Path`, a loadable `Main.qml`, reusable controls, and root methods `showMainWindow()`, `showFloatingWindow()`, and `prepareToQuit()`.

- [ ] **Step 1: Write failing resource and QML-load tests**

  Resolve source files and load `Main.qml` offscreen with real in-memory services. Assert one root object, required object names, and no QML load errors.

- [ ] **Step 2: Verify RED**

  Run: `python -m pytest tests/unit/test_qml_resources.py tests/integration/test_qml_loading.py -q`

- [ ] **Step 3: Implement resource resolution and theme primitives**

  Support source and frozen layouts. Define palette, typography, spacing, radii, hover/focus states, and restrained glow.

- [ ] **Step 4: Implement the main window**

  Build the frameless shell, sidebar, search, create action, window controls, empty state, and `ListView` bound to `mainModel`. Keep business decisions in Python.

- [ ] **Step 5: Verify QML and the full suite**

  Run: `python -m pytest tests/unit/test_qml_resources.py tests/integration/test_qml_loading.py -q`

  Run: `python -m pytest -q`

- [ ] **Step 6: Commit**

  `git commit -m "feat: add QML theme and main window"`

### Task 5: Build QML Dialogs and Floating Window

**Files:**
- Create: `src/ddl_reminder/ui/qml/FloatingWindow.qml`
- Create: `src/ddl_reminder/ui/qml/dialogs/TaskEditorDialog.qml`
- Create: `src/ddl_reminder/ui/qml/dialogs/TaskDetailDialog.qml`
- Create: `src/ddl_reminder/ui/qml/dialogs/SettingsDialog.qml`
- Create: `src/ddl_reminder/ui/qml/dialogs/ConfirmDialog.qml`
- Create: `src/ddl_reminder/ui/qml/components/FormField.qml`
- Create: `src/ddl_reminder/ui/qml/components/DateTimeField.qml`
- Create: `src/ddl_reminder/ui/qml/components/FloatingTaskCard.qml`
- Modify: `src/ddl_reminder/ui/qml/Main.qml`
- Modify: `tests/integration/test_qml_loading.py`

**Interfaces:**
- Consumes: controller slots and models from Tasks 2-3.
- Produces: QML methods for create/detail/settings/confirmation dialogs, forms that close only when commands return `True`, and an always-on-top floating window bound to `floatingModel`.

- [ ] **Step 1: Extend the smoke test and verify RED**

  Require every dialog and floating component to instantiate offscreen. Open create/detail dialogs with synthetic data and assert modal visibility and object names.

- [ ] **Step 2: Implement form and confirmation components**

  Use ISO date/time values at the Python boundary. Preserve values after failed saves. Keep save/restore/delete wording and severity distinct.

- [ ] **Step 3: Implement settings and floating QML**

  Bind autostart, task cards, direct completion, pin/hide actions, empty state, and detail actions. Delegate geometry to `FloatingWindowController`.

- [ ] **Step 4: Verify focused and full suites**

  Run: `python -m pytest tests/integration/test_qml_loading.py tests/unit/test_app_controller.py tests/unit/test_floating_window_controller.py -q`

  Run: `python -m pytest -q`

- [ ] **Step 5: Commit**

  `git commit -m "feat: migrate dialogs and floating window to QML"`

### Task 6: Switch the Application Runtime to QML

**Files:**
- Modify: `src/ddl_reminder/main.py`
- Modify: `src/ddl_reminder/ui/resources.py`
- Delete: obsolete QWidget window, dialog, card, theme, and window-control modules under `src/ddl_reminder/ui/`
- Delete or replace: obsolete QWidget-only tests under `tests/unit/`
- Create: `tests/integration/test_application_runtime.py`

**Interfaces:**
- Consumes: QML resources, controllers, and existing infrastructure.
- Produces: `create_application_runtime(argv: list[str])` returning an owned runtime that retains the engine, controllers, tray, reminder timer, and lock; `main() -> int` remains the executable entry point.

- [ ] **Step 1: Write a failing composition test**

  With in-memory services and fake external boundaries, prove root loading, normal/autostart visibility, tray actions, reminder refresh, and quit behavior.

- [ ] **Step 2: Verify RED**

  Run: `python -m pytest tests/integration/test_application_runtime.py -q`

- [ ] **Step 3: Refactor `main.py`**

  Expose context properties, load `Main.qml`, wire tray/reminders, preserve startup behavior, and return nonzero if no QML root loads.

- [ ] **Step 4: Remove obsolete QWidget application UI**

  Delete only modules whose responsibilities now live in controllers or QML; retain assets and resource helpers.

- [ ] **Step 5: Verify runtime and full suites**

  Run: `python -m pytest tests/integration/test_application_runtime.py tests/integration/test_qml_loading.py -q`

  Run: `python -m pytest -q`

- [ ] **Step 6: Commit**

  `git commit -m "refactor: run application with Qt Quick"`

### Task 7: Capture Real Screenshots and Update Documentation

**Files:**
- Create: `tools/capture_qml_screenshots.py`
- Replace: `docs/screenshots/main-window.png`
- Replace: `docs/screenshots/floating-window.png`
- Replace: `docs/screenshots/task-detail-dialog.png`
- Modify: `README.md`
- Modify: `docs/screenshots/README.md`
- Modify: `docs/architecture.md`
- Modify: `docs/product.md`
- Modify: `docs/manual-test-checklist.md`
- Modify: `docs/development-notes.md`
- Modify: `docs/release.md`
- Modify: `pyproject.toml`
- Modify: `installer/DDL-Reminder.iss`

**Interfaces:**
- Consumes: the real QML runtime with `InMemoryTaskRepository` and deterministic synthetic tasks.
- Produces: three real PNG captures plus `v0.2.0` documentation and metadata.

- [ ] **Step 1: Implement screenshot capture**

  Load real QML against synthetic tasks, render each target view, and save `QQuickWindow.grabWindow()` results to the existing screenshot filenames.

- [ ] **Step 2: Capture and inspect all screenshots**

  Run: `python tools/capture_qml_screenshots.py`

  Inspect at original resolution for clipping, unreadable text, private data, old QWidget visuals, and control mismatches. Fix QML and repeat until clean.

- [ ] **Step 3: Update documentation and versions**

  Document Qt Quick/QML, the Python bridge, unchanged data behavior, packaging, actual screenshots, and `v0.2.0` in consistent Chinese and English sections.

- [ ] **Step 4: Verify**

  Run: `git diff --check`

  Run: `python -m pytest -q`

- [ ] **Step 5: Commit**

  `git commit -m "docs: publish QML interface preview"`

### Task 8: Package, Install, Verify, and Publish v0.2.0

**Files:**
- Modify: `DDL-Reminder.spec`
- Modify: `installer/DDL-Reminder.iss` only if verification requires additional upgrade cleanup.

**Interfaces:**
- Consumes: QML package files, Qt Quick imports, existing installation, and GitHub repository.
- Produces: a verified local installation and `DDL-Reminder-Setup-v0.2.0.exe` attached to release `v0.2.0`.

- [ ] **Step 1: Bundle QML and Qt Quick**

  Add the QML tree as package data, collect required QtQml/QtQuick modules, preserve assets and root-DLL filtering.

- [ ] **Step 2: Run final source verification**

  Run: `python -m pytest -q`

  Run: `git diff --check`

- [ ] **Step 3: Build with PyInstaller**

  Run: `python -m PyInstaller --clean --noconfirm DDL-Reminder.spec`

  Expected: exit 0 and `dist/DDL-Reminder/DDL-Reminder.exe` exists.

- [ ] **Step 4: Verify packaged QML and DLL loading**

  Start against controlled data/config, load all windows/dialogs, and confirm no conflicting root runtime/ICU DLLs. Verify Qt Core/Gui/Widgets/Qml/Quick DLL loading.

- [ ] **Step 5: Build the installer**

  Run: `iscc installer\DDL-Reminder.iss`

  Expected: exit 0 and `installer_dist/DDL-Reminder-Setup.exe` exists.

- [ ] **Step 6: Protect the production database during local upgrade**

  Confirm the app is closed. Back up and hash `tasks.db`, silently install over the existing application, then require an unchanged hash and `PRAGMA integrity_check = ok`.

- [ ] **Step 7: Verify the installed application**

  Check executable hashes, desktop shortcut, QML/resources, runtime DLLs, and a real startup smoke test with no immediate process exit.

- [ ] **Step 8: Commit packaging changes and verify a clean tree**

  Commit with `build: package Qt Quick interface`, rerun the full suite and diff check, and require `git status --short` to be empty.

- [ ] **Step 9: Integrate and push `main`**

  Merge the verified feature branch, rerun tests on merged `main`, and push without force.

- [ ] **Step 10: Tag and publish**

  Create annotated tag `v0.2.0`, push it, create the GitHub release, and upload `DDL-Reminder-Setup-v0.2.0.exe`.

- [ ] **Step 11: Verify the remote release**

  Verify remote `main` and tag resolution, public release state, matching asset name and byte size, and a valid download URL.
