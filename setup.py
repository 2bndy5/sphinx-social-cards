from pathlib import Path
import subprocess
from setuptools import setup, Command
from setuptools.command.build import SubCommand
from setuptools.command.build_py import build_py
from setuptools.command.sdist import sdist

pkg_root = Path(__file__).parent / "src"


class SrcDistCommand(sdist):
    """Custom sdist command."""

    def run(self):
        self.run_command("bundle-icons")
        super().run()


class BuildPyCommand(build_py):
    """Custom bdist_wheel command."""

    def run(self):
        self.run_command("bundle-icons")
        super().run()


class BundleCommand(Command, SubCommand):
    """A custom command to run svgo (via nox) on all bundled SVG icons."""

    description = "Copy and optimize SVG files from npm modules."
    user_options = [
        # The format is (long option, short option, description).
        ("dirty", None, "skip bundling icons if they already exist in pkg src"),
    ]

    def initialize_options(self):
        """Set default values for options."""
        # Each user option must be listed here with their default value.
        self.dirty = False

    def finalize_options(self):
        """Post-process options."""
        if (
            self.dirty
            and not Path(pkg_root, "sphinx_social_cards", ".icons", "tabler").exists()
        ):
            raise OSError("Building package 'dirty', but no generated SVG files exist.")

    def run(self):
        """Run command."""
        if not self.dirty:
            self.announce("Running nox session: bundle_icons", level=2)
            subprocess.run(["nox", "-s", "bundle_icons"], check=True, shell=True)


# all install info is located in pyproject.toml
setup(
    cmdclass={
        "bundle-icons": BundleCommand,
        "build_py": BuildPyCommand,
        "sdist": SrcDistCommand,
    },
)
