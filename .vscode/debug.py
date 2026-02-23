import json
import platform
import sys
import subprocess
from pathlib import Path

PLATFORM = platform.system()


def load_config():
    """Loads configuration from build_config.json with defaults."""
    config_path = Path(__file__).parent / "build_config.json"
    data = {"GAME_NAME": "ArkhamSCE", "HOTKEY": "f13", "FORCE_GO": False}  # Defaults

    if config_path.is_file():
        try:
            with open(config_path, "r") as f:
                user_config = json.load(f)
                data.update(user_config)
        except Exception as e:
            print(f"Warning: Could not read build_config.json ({e}). Using defaults.")
    return data


# CONFIGURATION
CONFIG = load_config()
GAME_NAME = CONFIG["GAME_NAME"]
HOTKEY = CONFIG["HOTKEY"]
FORCE_GO = CONFIG["FORCE_GO"]
WINDOW_TITLE = "Tabletop Simulator"


def get_output_folder():
    home = Path.home()
    if PLATFORM == "Windows":
        return home / "Documents" / "My Games" / "Tabletop Simulator" / "Saves"
    else:
        return home / "Library" / "Tabletop Simulator" / "Saves"


# Recursive search for the GUID in ObjectStates
def find_script(objects, target_guid):
    for obj in objects:
        if obj.get("GUID") == target_guid:
            return obj.get("LuaScript", "")
        if "ContainedObjects" in obj:
            result = find_script(obj["ContainedObjects"], target_guid)
            if result:
                return result
    return None


def open_bundled_script(target_guid, line_number):
    output_folder = get_output_folder()
    save_path = output_folder / f"{GAME_NAME}.json"

    with open(save_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if target_guid.lower() == "global":
        script_content = data.get("LuaScript", "")
    else:
        script_content = find_script(data.get("ObjectStates", []), target_guid)

    if script_content:
        # Create a temp file for debugging
        temp_dir = Path(__file__).parent / "temp"
        temp_dir.mkdir(exist_ok=True)
        temp_path = temp_dir / f"DEBUG_{target_guid}.ttslua"
        with open(temp_path, "w", encoding="utf-8", newline='') as f:
            f.write(script_content)

        # Open in VS Code at the specific line: code -g file:line
        subprocess.run(["code", "-g", f"{temp_path}:{line_number}"], shell=True)
        print("Opened bundled script at correct line for debugging.")
    else:
        print(f"Object {target_guid} not found.")


if __name__ == "__main__":
    # Usage: python debug.py <guid> <line>
    open_bundled_script(sys.argv[1], sys.argv[2])
