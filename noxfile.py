import nox

SUPPORTED_PY_VER = list(f"3.{x}" for x in range(8, 13))
nox.options.reuse_existing_virtualenvs = True


@nox.session(python=False)
@nox.parametrize("builder", ["html", "dirhtml"], ids=["html", "dirhtml"])
def docs(session: nox.Session, builder: str):
    """Build docs."""
    session.run("pip", "install", "-r", "docs/requirements.txt")
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


@nox.session(python=SUPPORTED_PY_VER)
@nox.parametrize(
    "sphinx",
    [">=4.5,<5", ">=5,<6", ">=6,<7", ">=7,<8"],
    ids=["sphinx4", "sphinx5", "sphinx6", "sphinx7"],
)
def tests(session: nox.Session, sphinx: str):
    """Run unit tests and collect code coverage analysis."""
    session.install("-e", ".")
    session.install(f"sphinx{sphinx}")
    if sphinx.endswith("<5"):
        # sphinxcontrib deps that dropped support for sphinx v4.x
        session.install("-r", "tests/requirements-sphinx4.txt")
    session.install("-r", "tests/requirements.txt")
    session.run("coverage", "run", "-m", "pytest", "-v")


@nox.session
def coverage(session: nox.Session):
    """Create coverage report."""
    session.install("coverage[toml]>=7.0")
    session.run("coverage", "combine")
    total = int(session.run("coverage", "report", "--format=total", silent=True))
    session.run("coverage", "xml")
    session.run("coverage", "html")
    session.log("Coverage is %d%%", total)
