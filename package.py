import argparse
import importlib.metadata
import subprocess
import sys
from pathlib import Path

import paddlex


def main():
    parser = argparse.ArgumentParser(
        description="Build SandFlowServer with PyInstaller."
    )

    parser.add_argument(
        "--file",
        default="app.py",
        help="Main Python entry file. Default: app.py"
    )

    parser.add_argument(
        "--name",
        default="SandFlowServer",
        help="Executable/folder name. Default: SandFlowServer"
    )

    parser.add_argument(
        "--nvidia",
        action="store_true",
        help="Include NVIDIA package binaries for GPU deployment."
    )

    parser.add_argument(
        "--onefile",
        action="store_true",
        help="Build a single EXE instead of a folder build."
    )

    args = parser.parse_args()

    main_file = Path(args.file)

    if not main_file.exists():
        print(f"ERROR: Could not find {main_file}")
        sys.exit(1)

    project_dir = main_file.resolve().parent
    templates_dir = project_dir / "templates"
    static_dir = project_dir / "static"

    if not templates_dir.exists():
        print(f"ERROR: Missing folder: {templates_dir}")
        sys.exit(1)

    if not static_dir.exists():
        print(f"ERROR: Missing folder: {static_dir}")
        sys.exit(1)

    installed_deps = {
        dist.metadata["Name"]
        for dist in importlib.metadata.distributions()
        if dist.metadata.get("Name")
    }

    paddlex_deps = set(
        paddlex.utils.deps.BASE_DEP_SPECS.keys()
    )

    deps_to_copy_metadata = sorted(
        dep
        for dep in installed_deps
        if dep in paddlex_deps
    )

    separator = ";" if sys.platform.startswith("win") else ":"

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "--noconfirm",
        "--name",
        args.name,
        "--collect-all",
        "paddleocr",
        "--collect-all",
        "paddlex",
        "--collect-binaries",
        "paddle",
        "--add-data",
        f"{templates_dir}{separator}templates",
        "--add-data",
        f"{static_dir}{separator}static",
    ]

    if args.onefile:
        cmd.append("--onefile")
    else:
        cmd.append("--onedir")

    if args.nvidia:
        cmd += [
            "--collect-binaries",
            "nvidia"
        ]

    for dep in deps_to_copy_metadata:
        cmd += [
            "--copy-metadata",
            dep
        ]

    cmd.append(str(main_file))

    print("\nBuilding SandFlowServer with command:\n")
    print(" ".join(f'"{part}"' if " " in str(part) else str(part) for part in cmd))
    print()

    try:
        subprocess.run(
            cmd,
            check=True,
            cwd=project_dir
        )
    except subprocess.CalledProcessError as exc:
        print(f"\nPackaging failed with exit code {exc.returncode}")
        sys.exit(exc.returncode)

    output_type = "single executable" if args.onefile else "folder build"

    print("\nBuild complete.")
    print(f"Type: {output_type}")
    print(f"Output: {project_dir / 'dist' / args.name}")


if __name__ == "__main__":
    main()
