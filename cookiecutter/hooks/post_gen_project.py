import shutil
from pathlib import Path

REMOVE_PATHS = [
    "{% if cookiecutter.add_layout != 'True' -%} layouts {%- endif %}",
    "{% if cookiecutter.add_image != 'True' -%} images {%- endif %}",
]

for excess in REMOVE_PATHS:
    exc_path = Path(Path.cwd(), "{{ cookiecutter.package_name }}", excess)
    if excess and exc_path.exists():
        shutil.rmtree(str(exc_path))
