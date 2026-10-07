# Qt Quick/QML UI Migration Design

## Goal

Migrate every application window and dialog from Qt Widgets to Qt Quick/QML while preserving the existing Python business layer, PySide6 runtime, SQLite database, reminders, tray integration, autostart behavior, and user-visible feature set.

The release will be published as `v0.2.0`, installed over the local `v0.1.4` installation, and documented with screenshots captured from the real QML application.

## Scope

The migration includes:

- Main window
- Floating reminder window
- Create-task dialog
- Task-detail and edit dialog
- Settings dialog
- Save, restore, and delete confirmation dialogs
- Shared visual components, theme, icons, and window controls
- Python-to-QML presentation models and controllers
- PyInstaller and installer updates required to ship QML
- README, architecture, product, screenshot, and release documentation

The migration does not add new business features. In particular, it does not add statistics, snooze behavior, accounts, synchronization, recurring tasks, or new reminder rules.

## Architecture

`main.py` remains the composition root. It creates `QApplication`, the existing database engine, repositories, application services, tray integration, reminder timer, single-instance lock, and the QML engine.

The QML layer does not access SQLAlchemy, repositories, or domain objects directly. A Python presentation layer exposes QML-safe values and commands:

```text
main.py
├── QApplication and QQmlApplicationEngine
├── SQLite / repositories / application services
├── tray, reminders, autostart, and single-instance lock
└── AppController
    ├── TaskListModel for the main window
    ├── TaskListModel for the floating window
    ├── search and filter state
    ├── task commands
    ├── settings commands
    └── window and error signals

QML
├── MainWindow.qml
├── FloatingWindow.qml
├── TaskEditorDialog.qml
├── TaskDetailDialog.qml
├── SettingsDialog.qml
├── ConfirmDialog.qml
└── components/
```

The controller uses `QObject` properties, signals, and slots. Task collections use `QAbstractListModel` with explicit roles for IDs, titles, descriptions, deadline text, remaining-time text, completion state, and deadline category. QML receives only primitives and Qt-compatible date/time values.

The system tray may continue using `QSystemTrayIcon` and `QMenu` because it is system integration rather than an application window. `QApplication` remains the application type so tray support continues to work alongside `QQmlApplicationEngine`.

## Data Flow

On startup, `main.py` creates the existing `TaskService` and injects it into `AppController`. The controller loads active, completed, or urgent tasks according to the current filter, applies the current search query, and orders results by `(deadline, created_at)`.

QML invokes controller slots for create, update, complete, restore, delete, filter, search, settings, and window actions. The controller calls the existing application services. After a successful mutation it refreshes both the main-window and floating-window models and emits a shared tasks-changed signal so the reminder runner executes with current data.

Domain and application exceptions are caught by the controller and converted into user-facing error signals. QML displays those messages without exposing Python tracebacks. A failed operation leaves the editor open and does not refresh models as though the operation succeeded.

## Main Window

The main window follows the approved dark technology visual direction:

- Deep navy background with restrained cyan and violet accents
- Frameless rounded shell with custom minimize, maximize, and hide controls
- Left navigation for active, completed, urgent, and settings views
- Top search input and create-task action
- Central task list using reusable QML task cards
- Deadline-category accent colors and accessible text contrast
- Empty-state presentation when a filter has no tasks

Task cards preserve the current information and actions: title, optional description, deadline, remaining or overdue time, complete or restore, edit, and delete. No overview statistics panel is added.

## Floating Window

The floating window remains frameless, always on top, and limited to the three earliest unfinished tasks. Each card supports opening task details and completing the task directly.

The migration preserves:

- Dragging
- Stored window position
- Edge detection and snapping
- Automatic edge collapse and expansion
- Pinning to disable automatic collapse
- Hide-on-close behavior
- Tray-based restoration
- Periodic remaining-time refresh

Window geometry and edge behavior remain in Python where access to screens, native window position, animation state, and `QSettings` can be tested independently. QML owns the visual content and pointer events and delegates geometry commands to the controller.

## Dialogs

All application dialogs use QML:

- The create dialog defaults the deadline time to `23:59`.
- The detail dialog displays current task values and permits editing and saving.
- The settings dialog displays and changes the existing Windows autostart option.
- Confirmation dialogs retain separate save, restore, and delete wording and visual severity.

Dialogs are modal relative to the relevant application window. Validation errors preserve the entered values and keep the dialog open.

## Assets and Screenshots

The existing application icon and useful SVG assets remain. New UI assets must be local, bundled, and usable without network access.

The three README screenshots are replaced with captures from the actual QML application:

- `docs/screenshots/main-window.png`
- `docs/screenshots/floating-window.png`
- `docs/screenshots/task-detail-dialog.png`

Screenshot capture uses a test repository with synthetic tasks and never reads the user's production database. The previously generated concept mockup is a visual reference only and is not presented as a product screenshot.

## Compatibility and Data Safety

The production database remains `%APPDATA%/DDL-Reminder/tasks.db`. No schema change or data migration is introduced.

Before local installation, the existing database is backed up and hashed. After installation, the database hash must match and `PRAGMA integrity_check` must return `ok`. Existing task IDs, completion states, deadlines, descriptions, and reminder flags remain unchanged.

The existing `v0.1.4` GitHub release remains available for rollback.

## Packaging and Release

PyInstaller must include all QML source files and the Qt Quick/QML runtime modules required by the application. The existing root-level DLL filtering remains in place. The Inno Setup installer retains the current application ID and install location so `v0.2.0` upgrades the existing installation and preserves the desktop shortcut and AppData database.

The release process is:

1. Run the complete automated test suite.
2. Verify QML import and component loading without QML warnings or errors.
3. Build the PyInstaller distribution.
4. Verify the packaged executable can load and start the QML interface.
5. Build and install the Inno Setup package locally.
6. Verify installed files, shortcut target, database hash, and database integrity.
7. Commit and push the implementation to `main`.
8. Create and push tag `v0.2.0`.
9. Publish the GitHub release and upload the versioned installer.
10. Verify the remote branch, tag, release, and installer asset.

## Testing

Tests cover the presentation boundary rather than QML implementation details:

- Task model roles and values
- Active, completed, and urgent filters
- Search behavior
- Deadline and creation-time ordering
- Create, update, complete, restore, and delete commands
- Error signaling and preservation of dialog state
- Synchronization between main and floating task models
- Floating-window position, pin, snap, collapse, and restore behavior
- Autostart state changes
- QML root component and dialog component loading
- QML resource availability in source and packaged builds

Existing domain, application, repository, reminder, single-instance, and autostart tests remain. UI-specific QWidget tests are replaced when their behavior moves to the QML presentation boundary.

## Success Criteria

- Every application window and dialog is rendered with Qt Quick/QML.
- The Python business layer, PySide6 runtime, SQLite schema, and existing feature set are preserved.
- Main-window task ordering and floating-window direct completion still work.
- Floating-window native behavior remains available.
- All automated tests and packaging checks pass.
- The local installation upgrades without modifying the production database.
- README screenshots show the real QML application.
- GitHub `main`, tag `v0.2.0`, and the `v0.2.0` installer release are published and verified.
