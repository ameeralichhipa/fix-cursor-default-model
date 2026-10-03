#!/usr/bin/env python3
"""Keep Cursor Agent/Composer on Auto and prefer Last Used."""

from __future__ import annotations

import json
import os
import platform
import shutil
import sqlite3
import sys
import time
from pathlib import Path

APP_KEY = (
    "src.vs.platform.reactivestorage.browser.reactiveStorageServiceImpl"
    ".persistentStorage.applicationUser"
)

AUTO_SELECTED = [{"modelId": "default", "parameters": []}]
MODES = [
    "cmd-k",
    "composer",
    "background-composer",
    "composer-ensemble",
    "plan-execution",
    "spec",
    "deep-search",
    "quick-agent",
]

REPO_URL = "https://github.com/ameeralichhipa/fix-cursor-default-model"


def state_db_path() -> Path:
    home = Path.home()
    system = platform.system()

    if system == "Windows":
        appdata = Path(os.environ.get("APPDATA", home / "AppData" / "Roaming"))
        return appdata / "Cursor" / "User" / "globalStorage" / "state.vscdb"

    if system == "Darwin":
        return (
            home
            / "Library"
            / "Application Support"
            / "Cursor"
            / "User"
            / "globalStorage"
            / "state.vscdb"
        )

    return home / ".config" / "Cursor" / "User" / "globalStorage" / "state.vscdb"


def settings_json_path() -> Path:
    home = Path.home()
    system = platform.system()

    if system == "Windows":
        appdata = Path(os.environ.get("APPDATA", home / "AppData" / "Roaming"))
        return appdata / "Cursor" / "User" / "settings.json"

    if system == "Darwin":
        return home / "Library" / "Application Support" / "Cursor" / "User" / "settings.json"

    return home / ".config" / "Cursor" / "User" / "settings.json"


def get_value(conn: sqlite3.Connection, key: str):
    row = conn.execute("SELECT value FROM ItemTable WHERE key=?", (key,)).fetchone()
    return row[0] if row else None


def put_value(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO ItemTable (key, value) VALUES (?, ?)",
        (key, value),
    )


def pin_auto_in_db(db: Path) -> Path:
    backup = db.with_name(f"{db.name}.bak-auto-{int(time.time())}")
    shutil.copy2(db, backup)

    conn = sqlite3.connect(str(db))
    conn.execute("PRAGMA busy_timeout=5000")
    try:
        put_value(
            conn,
            "cursor/applicationOpenModelAppliedConfig",
            json.dumps({"selectedModels": AUTO_SELECTED}),
        )
        put_value(conn, "cursor/applicationOpenRecentComposerModelSwitch", "null")
        put_value(conn, "cursor/modelNudgesEnabled", "false")
        put_value(conn, "cursor/initialModelState", "applied")

        raw = get_value(conn, APP_KEY)
        if not raw:
            raise RuntimeError("Cursor applicationUser settings blob was not found.")

        data = json.loads(raw)
        ai = data.setdefault("aiSettings", {})
        model_config = ai.setdefault("modelConfig", {})

        for mode in MODES:
            prev = model_config.get(mode, {})
            max_mode = True
            if isinstance(prev, dict) and "maxMode" in prev and mode not in (
                "composer",
                "background-composer",
            ):
                max_mode = bool(prev["maxMode"])

            model_config[mode] = {
                "modelName": "default",
                "maxMode": max_mode,
                "selectedModels": list(AUTO_SELECTED),
            }

        data["useLastUsedModelAsDefault"] = True
        ai["useLastUsedModelAsDefault"] = True
        ai["defaultModelPreference"] = "lastUsed"
        if isinstance(data.get("composerState"), dict):
            data["composerState"]["useLastUsedModelAsDefault"] = True
            data["composerState"]["defaultModelPreference"] = "lastUsed"

        put_value(conn, APP_KEY, json.dumps(data, separators=(",", ":")))
        conn.commit()
    finally:
        conn.close()

    return backup


def pin_settings_json(path: Path) -> None:
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {}

    data["cursor.agent.defaultModelPreference"] = "lastUsed"
    data["cursor.composer.defaultModelPreference"] = "lastUsed"
    data["cursor.chat.defaultModelPreference"] = "lastUsed"
    data["cursor.defaultModelPreference"] = "lastUsed"
    path.write_text(json.dumps(data, indent=4) + "\n", encoding="utf-8")


def main() -> int:
    print("Fix Cursor Default Model")
    print("Keep Cursor on Auto")
    print(REPO_URL)
    print(f"OS: {platform.system()} {platform.release()}")

    db = state_db_path()
    print(f"State DB: {db}")

    if not db.exists():
        print("ERROR: Cursor state database not found.")
        print("Open Cursor once on this machine, then run this tool again.")
        return 1

    try:
        backup = pin_auto_in_db(db)
        print(f"Backup: {backup}")
        pin_settings_json(settings_json_path())
        print("Pinned model: Auto (default)")
        print("Preference: Last Used")
        print()
        print("Next steps:")
        print("1) Open Cursor Settings -> Agents -> Conversation")
        print("2) Set Default Model = Last Used")
        print("3) Reload Window (Ctrl/Cmd+Shift+P -> Developer: Reload Window)")
        print("4) Confirm a new Agent chat shows Auto")
        print()
        print("If a future Cursor update changes the model again, re-run this tool.")
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    code = main()
    if sys.stdin is not None and sys.stdin.isatty():
        try:
            input("\nPress Enter to close...")
        except EOFError:
            pass
    sys.exit(code)
