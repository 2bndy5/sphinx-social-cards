import logging
from os import environ
import sys
import nox

nox.options.reuse_existing_virtualenvs = True
nox.options.default_venv_backend = "uv"

ci_logger = logging.getLogger("CI logger")
ci_handler = logging.StreamHandler(stream=sys.stdout)
ci_handler.formatter = logging.Formatter("%(msg)s")
ci_logger.handlers.append(ci_handler)
ci_logger.propagate = False


def uv_sync(session: nox.Session, *args: str):
    """Synchronize dependencies using uv with additional arguments.

    Args:
        session: The nox session to run the command in.
        *args: Additional arguments to pass to `uv sync`.
    """
    session.run_install(
        "uv",
        "sync",
        "--active",
        *args,
    )


@nox.session
@nox.parametrize("builder", ["html", "dirhtml"], ids=["html", "dirhtml"])
def docs(session: nox.Session, builder: str):
    """Build docs."""
    if "CI" in environ:
        ci_logger.info(f"::group::Using {builder} builder")
    uv_sync(session, "--group", "docs", "--extra", "github")
    session.run(
        "sphinx-build",
        "-b",
        builder,
        "-W",
        "--keep-going",
        "-T",
        "docs",
        f"docs/_build/{builder}",
    )
    if "CI" in environ:
        ci_logger.info("::endgroup::")


def skip_version(python: int, sphinx: int) -> bool:
    return python < 10 and sphinx >= 8


def test_version() -> list[tuple[str, int]]:
    """generator function to conform tested versions of sphinx and python"""
    conditions = []
    for python in range(9, 14):
        for sphinx in range(4, 9):
            if skip_version(python, sphinx):
                continue
            conditions.append((f"3.{python}", sphinx))
    return conditions


def test_ids() -> list[str]:
    """generator function to conform tested versions of sphinx and python"""
    ids = []
    for python in range(9, 14):
        for sphinx in range(4, 9):
            if skip_version(python, sphinx):
                continue
            ids.append(f"3.{python},sphinx{sphinx}")
    return ids


@nox.session
@nox.parametrize(
    arg_names="python,sphinx",
    arg_values_list=test_version(),
    ids=test_ids(),
)
def tests(session: nox.Session, sphinx: int):
    """Run unit tests and collect code coverage analysis."""
    if "CI" in environ:
        ci_logger.info(f"::group::Using sphinx v{sphinx}")
    uv_sync(session, "--group", "test", "--extra", "github")
    if sphinx == 4:
        session.run("uv", "pip", "install", "-r", "tests/requirements-sphinx4.txt")
    else:
        spec = f"sphinx>={sphinx},<{sphinx + 1}"
        session.run("uv", "pip", "install", spec)
    session.run("coverage", "run", "-m", "pytest", "-v")
    if "CI" in environ:
        ci_logger.info("::endgroup::")


@nox.session
def coverage(session: nox.Session):
    """Create coverage report."""
    uv_sync(session, "--group", "coverage")
    session.run("coverage", "combine")
    total = int(session.run("coverage", "report", "--format=total", silent=True))
    session.run("coverage", "xml")
    session.run("coverage", "html")
    session.log("Coverage is %d%%", total)
