# noqa: D100
import platform
import sys
from dataclasses import dataclass
from pathlib import Path
from timeit import timeit

import humanize
import typer
from rich.console import Console
from rich.progress import track
from rich.table import Table

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
class PackageToTest:  # noqa: D101
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
        ),
    )


def benchmark(pkg: PackageToTest) -> float:  # noqa: D103
    exec(  # noqa: S102
        f"""
{pkg.setup}
assert {pkg.call} == {DISTANCE}
             """,
    )

    result = timeit(
        setup=pkg.setup,
        stmt=pkg.call,
        number=ITERATIONS,
    )

    return result / ITERATIONS


app = typer.Typer()


@app.command()
def console() -> None:
    """Benchmarks and prints result to the standard output."""
    results = tuple(
        (pkg, benchmark(pkg))
        for pkg in track(PACKAGES, description="Running benchmarks")
    )

    iterations_humanized = humanize.intword(ITERATIONS)
    table = Table(title=f"Benchmark ({iterations_humanized} iterations)")
    table.add_column("Package")
    table.add_column("Duration")

    for pkg, duration in results:
        duration_humanized = humanize.metric(duration, "s")
        table.add_row(f"{pkg.name} ({pkg.pypi})", duration_humanized)

    console = Console()
    console.print(table)


@app.command()
def markdown() -> None:
    """Benchmarks and writes MarkDown table to the output."""
    results = tuple(
        (pkg, benchmark(pkg))
        for pkg in track(PACKAGES, description="Running benchmarks")
    )

    benchmark_path = Path("BENCHMARK.md")
    with benchmark_path.open("w") as output:
        iterations_humanized = humanize.intword(ITERATIONS)
        typer.echo(f"# Benchmark ({iterations_humanized} iterations)", output)
        typer.echo(file=output)

        typer.echo("| OS | CPU | Python |", output)
        typer.echo("| -- | --- | ------ |", output)
        typer.echo(
            f"| {platform.system()} {platform.release()} "
            f"| {platform.processor()} "
            f"| {sys.version} |",
            output,
        )
        typer.echo(
            """
| Package | Duration of one iteration (s) |
| ------- | ------------------------- |""",
            output,
        )
        for pkg, duration in results:
            typer.echo(f"| [{pkg.name}]({pkg.pypi}) | {duration} |", output)


if __name__ == "__main__":
    app()
