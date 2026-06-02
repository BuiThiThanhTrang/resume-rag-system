from pathlib import Path


def load_project_env(root_dir: Path) -> None:
    try:
        from dotenv import load_dotenv

        load_dotenv(root_dir / ".env", override=False)
    except Exception:
        return
