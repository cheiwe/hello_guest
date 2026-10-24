"""
Runs Python in the open Unreal Editor through Python Remote Execution.

Needs Project Settings > Plugins > Python > Enable Remote Execution (on in this project).
Uses remote_execution.py that ships with the engine.

    py Scripts/Tools/ue_run.py Scripts/Editor/create_act1_house.py
    py Scripts/Tools/ue_run.py -c "print(unreal.SystemLibrary.get_engine_version())"
"""

import argparse
import os
import sys
import time

ENGINE_DIR = os.environ.get("UE_ENGINE_DIR", r"C:\Program Files\Epic Games\UE_5.8\Engine")
sys.path.append(os.path.join(ENGINE_DIR, "Plugins", "Experimental", "PythonScriptPlugin", "Content", "Python"))

import remote_execution  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs="?", help="Python file to execute in the editor")
    parser.add_argument("-c", "--command", help="Python statement to execute instead of a file")
    parser.add_argument("--timeout", type=float, default=10.0, help="Seconds to wait for the editor")
    args = parser.parse_args()
    if not args.file and not args.command:
        parser.error("give a file or -c")

    remote = remote_execution.RemoteExecution()
    remote.start()
    try:
        deadline = time.time() + args.timeout
        while not remote.remote_nodes and time.time() < deadline:
            time.sleep(0.1)
        if not remote.remote_nodes:
            sys.exit("No Unreal Editor found. Is it open with Remote Execution enabled?")
        remote.open_command_connection(remote.remote_nodes[0]["node_id"])
        if args.file:
            path = os.path.abspath(args.file).replace("\\", "/")
            result = remote.run_command(path, unattended=True, exec_mode=remote_execution.MODE_EXEC_FILE)
        else:
            result = remote.run_command(args.command, unattended=True, exec_mode=remote_execution.MODE_EXEC_STATEMENT)
    finally:
        remote.stop()

    for entry in result.get("output", []):
        print(entry["output"].rstrip())
    if result.get("result") and result["result"] != "None":
        print(result["result"])
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
