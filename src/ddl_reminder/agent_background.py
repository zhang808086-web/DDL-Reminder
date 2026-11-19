"""Windowless entry point for automatic MCP registration.

Build with the Windows GUI subsystem. Do not create a QApplication, print to
stdio or launch shells/console child processes from this scheduled entry point.
"""


def main() -> int:
    try:
        import json
        from ddl_reminder.infrastructure.agent_setup import connect_agents, installed_mcp_command
        from ddl_reminder.infrastructure.app_paths import get_app_data_dir

        results = connect_agents(installed_mcp_command())
        report = json.dumps(results, ensure_ascii=False, indent=2)
        (get_app_data_dir() / "agent-setup.json").write_text(report, encoding="utf-8")
        return 0 if all(item["success"] for item in results) else 1
    except Exception:
        # A background registration failure must never display a GUI traceback.
        try:
            import logging
            from ddl_reminder.infrastructure.app_paths import get_app_data_dir
            logging.basicConfig(filename=get_app_data_dir() / "agent-setup.log", encoding="utf-8", level=logging.ERROR)
            logging.exception("Automatic agent registration failed")
        except Exception:
            pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
