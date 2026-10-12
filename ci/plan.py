"""Prints the CI matrix: one entry per recipe a change reaches, per profile in ci/profiles.

Run from the registry's root with the arguments `silo affected` takes: --since <ref> or --all.
"""

import json
import subprocess
import sys
import tomllib
from pathlib import Path

RUNNERS = {"linux": "ubuntu-latest", "windows": "windows-latest", "macos": "macos-latest"}

profiles = sorted(Path("ci/profiles").glob("*.toml"))
command = ["silo", "affected", ".", *sys.argv[1:]]
for profile in profiles:
    command += ["--profile", str(profile)]
affected = json.loads(subprocess.run(command, stdout=subprocess.PIPE, text=True, check=True).stdout)

matrix = []
for profile in profiles:
    described = tomllib.loads(profile.read_text(encoding="utf-8"))
    for recipe in affected[profile.stem]:
        matrix.append(
            {
                "name": "@".join(Path(recipe).parts[1:]),
                "recipe": recipe,
                "profile": profile.stem,
                "runner": RUNNERS[described["settings"]["os"]],
            }
        )
print(json.dumps({"include": matrix}))
