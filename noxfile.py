from pathlib import Path
import shutil
import nox

SUPPORTED_PY_VER = list(f"3.{x}" for x in range(7, 12))
nox.options.reuse_existing_virtualenvs = True


@nox.session(python=False)
def bundle_icons(session: nox.Session, quiet: bool = True):
    """Bundle icons for distribution"""
    icon_pkgs = {
        "tabler": ["@tabler/icons/icons", "@tabler/icons/LICENSE"],
        "material": ["@mdi/svg/svg", "@mdi/svg/LICENSE"],
        "octicons": ["@primer/octicons/build/svg", "@primer/octicons/LICENSE"],
        "simple": ["simple-icons/icons", "simple-icons/LICENSE.md"],
        "fontawesome": [
            "@fortawesome/fontawesome-free/svgs",
            "@fortawesome/fontawesome-free/LICENSE.txt",
        ],
    }
    pkg_root = Path(__file__).parent

    # ensure icons from npm pkg exist
    session.run("npm", "install", external=True)

    for name, sources in icon_pkgs.items():
        icons_dist = pkg_root / "src" / "sphinx_social_cards" / ".icons" / name
        extra_svgo_args = ["-r"]
        if quiet:
            extra_svgo_args.append("-q")
        print("Optimizing", name, "icons")
        for src in sources:
            icons_src = pkg_root / "node_modules" / src
            if icons_src.is_dir():
                if icons_dist.exists():
                    shutil.rmtree(str(icons_dist))
                # copy icons from npm pkg
                session.run(
                    "npx",
                    "svgo",
                    "--config",
                    str(pkg_root / "tools" / "svgo_config.js"),
                    *extra_svgo_args,
                    "-f",
                    str(icons_src),
                    "-o",
                    str(icons_dist),
                    external=True,
                )
            elif icons_src.is_file():
                # copy the file (eg. LICENSE)
                icons_dist.parent.mkdir(parents=True, exist_ok=True)
                Path(icons_dist, icons_src.name).write_bytes(icons_src.read_bytes())


@nox.session(python=False)
@nox.parametrize(
    "builder", ["html", "dirhtml", "latex"], ids=["html", "dirhtml", "latex"]
)
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
    dist_dir = Path(__file__).parent / "dist"
    for f in dist_dir.glob("*.whl"):
        whl = str(f)
        break
    else:
        raise FileNotFoundError("dist/*.whl not found. Have you built the pkg?")
    session.install(whl)
    session.install(f"sphinx{sphinx}")
    session.install("-r", "tests/requirements.txt")
    session.run("coverage", "run", "-m", "pytest", "-vv", "-s")


@nox.session
def coverage(session: nox.Session):
    """Create coverage report."""
    session.install("coverage[toml]>=7.0")
    session.run("coverage", "combine")
    total = int(session.run("coverage", "report", "--format=total", silent=True))
    md = session.run("coverage", "report", "--format=markdown", silent=True)
    Path(".coverage_.md").write_text(
        f"<details><summary>Coverage is {total}%</summary>\n\n{md}\n\n</details>",
        encoding="utf-8",
    )
    session.run("coverage", "xml")
    session.run("coverage", "html")
    session.log("Coverage is %d%%", total)
