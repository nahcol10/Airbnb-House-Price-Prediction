"""
ML Project Scaffolder
=====================
Generates a production-ready folder structure for ML projects.

Usage:
    python template.py my-project
    python template.py my-project --with-web
"""

import argparse
import os
from pathlib import Path

STRUCTURE = {
    "config": {"config.yaml": None},
    "data": {".gitkeep": None},
    "models": {".gitkeep": None},
    "artifacts": {".gitkeep": None},
    "logs": {".gitkeep": None},
    "notebooks": {"eda.ipynb": None, "training.ipynb": None},
    "src/airbnb": {
        "__init__.py": '"""ML Package."""\n',
        "config.py": None,
        "data.py": None,
        "train.py": None,
        "predict.py": None,
        "utils.py": None,
    },
    "api": {
        "__init__.py": "",
        "main.py": None,
    },
    "tests": {
        "__init__.py": "",
        "test_data.py": None,
        "test_train.py": None,
    },
    "main.py": None,
    "pyproject.toml": None,
    "requirements.txt": None,
    "Dockerfile": None,
    "heroku.yml": None,
    "runtime.txt": None,
    ".gitignore": None,
}

WEB_EXTRAS = {
    "web": {
        "package.json": None,
        "next.config.js": None,
        "tsconfig.json": None,
        "tailwind.config.js": None,
        "postcss.config.js": None,
        ".env.local": None,
    },
    "web/public": {".gitkeep": None},
    "web/src/app": {"layout.tsx": None, "page.tsx": None, "globals.css": None},
    "web/src/components": {"PredictionForm.tsx": None, "ResultCard.tsx": None},
    "web/src/lib": {"api.ts": None},
    "web/src/types": {"index.ts": None},
    "docker-compose.yml": None,
}


def create(root: Path, structure: dict):
    for dirname, contents in structure.items():
        dirpath = root / dirname
        dirpath.mkdir(parents=True, exist_ok=True)
        for filename, content in contents.items():
            filepath = dirpath / filename
            if filepath.exists():
                print(f"  [skip] {filepath.relative_to(root)}")
                continue
            if content is not None:
                filepath.write_text(content, encoding="utf-8")
            print(f"  [create] {filepath.relative_to(root)}")


def main():
    parser = argparse.ArgumentParser(description="Scaffold an ML project")
    parser.add_argument("name", help="Project directory name")
    parser.add_argument(
        "--with-web", action="store_true", help="Include React frontend template"
    )
    args = parser.parse_args()

    root = Path.cwd() / args.name
    if root.exists():
        print(f"Directory '{root}' already exists.")
        return

    print(f"\nScaffolding: {root.name}/\n")
    create(root, STRUCTURE)

    if args.with_web:
        print("\n  web extras:")
        create(root, WEB_EXTRAS)

    print(f"\nDone. cd {root.name} and start building.")


if __name__ == "__main__":
    main()
