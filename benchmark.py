import platform
import sys
from dataclasses import dataclass
from enum import Enum
from timeit import timeit

import typer

from levdist import levenshtein

try:
    from leven import levenshtein

    LEVEN_PRESENT = True
except ImportError:
    LEVEN_PRESENT = False

ITERATIONS = 1_000_000
# `leven` has some hacks that remove same prefix and suffix.
# To measure it fair I adjusted the strings.
S1 = "1Levenshtein1"
S2 = "2Frankenstein2"
DISTANCE = levenshtein(S1, S2)


@dataclass(frozen=True)
class PackageToTest:
    name: str
    pypi: str
    setup: str
    call: str


PACKAGES = [
    PackageToTest(
        "levdist",
        "https://pypi.org/project/levdist/",
        "from levdist import levenshtein",
        f"levenshtein('{S1}', '{S2}')",
    ),
    PackageToTest(
        "Levenshtein",
        "https://pypi.org/project/levenshtein/",
        "from Levenshtein import distance",
        f"distance('{S1}', '{S2}')",
    ),
    PackageToTest(
        "pylev",
        "https://pypi.org/project/pylev/",
        "from pylev import levenshtein",
        f"levenshtein('{S1}', '{S2}')",
    ),
    PackageToTest(
        "editdistance",
        "https://pypi.org/project/editdistance/",
        "import editdistance",
        f"editdistance.eval('{S1}', '{S2}')",
    ),
]

if LEVEN_PRESENT:
    PACKAGES.append(
        PackageToTest(
            "leven",
            "https://pypi.org/project/leven/",
            "from leven import levenshtein",
            f"levenshtein('{S1}', '{S2}')",
        )
    )


class OutputFormat(str, Enum):
    TEXT = "txt"
    MARKDOWN = "md"


def benchmark(pkg: PackageToTest) -> float:
    exec(
        f"""
{pkg.setup}
assert {pkg.call} == {DISTANCE}
             """
    )

    result = timeit(
        setup=pkg.setup,
        stmt=pkg.call,
        number=ITERATIONS,
    )

    return result / ITERATIONS


def main(
    output: typer.FileTextWrite = typer.Argument(sys.stdout),
    format: OutputFormat = typer.Option(OutputFormat.TEXT),
) -> None:
    with typer.progressbar(PACKAGES) as pkgs:
        results = tuple((benchmark(pkg) for pkg in pkgs))

    if format == OutputFormat.TEXT:
        for pkg, duration in zip(PACKAGES, results):
            typer.echo(f"{pkg.name} ({pkg.pypi}): {duration} sec", output)
    elif format == OutputFormat.MARKDOWN:
        typer.echo(f"# Benchmark ({ITERATIONS} iterations)", output)
        typer.echo(file=output)

        typer.echo("| OS | CPU | Python |", output)
        typer.echo("| -- | --- | ------ |", output)
        typer.echo(
            f"| {platform.system()} {platform.release()} | {platform.processor()} | {sys.version} |",
            output,
        )
        typer.echo(
            """
| Package | Duration of one iteration (sec) |
| ------- | ------------------------- |""",
            output,
        )
        for pkg, duration in zip(PACKAGES, results):
            typer.echo(f"| [{pkg.name}]({pkg.pypi}) | {duration} |", output)


if __name__ == "__main__":
    typer.run(main)
