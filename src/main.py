import argparse
import logging

from queries import run_query
from visualize import plot_points_race_by_race, plot_constructor_wins, plot_grid_vs_finish

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def cmd_wins(args: argparse.Namespace) -> None:
    """Show and plot constructor wins from a given year onward."""
    logger.info(f"Running constructor wins report (from {args.min_year})")
    plot_constructor_wins(args.min_year)


def cmd_points(args: argparse.Namespace) -> None:
    """Plot cumulative points progression for given drivers in a season."""
    logger.info(f"Running points progression for {args.drivers} in {args.year}")
    plot_points_race_by_race(args.year, args.drivers)


def cmd_grid(args: argparse.Namespace) -> None:
    """Plot grid vs finish position scatter for a season."""
    logger.info(f"Running grid-vs-finish analysis for {args.year}")
    plot_grid_vs_finish(args.year)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="F1 SQL Analytics — query and visualize Formula 1 historical data."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    wins_parser = subparsers.add_parser("wins", help="Constructor win totals")
    wins_parser.add_argument("--min-year", type=int, default=2014, help="Earliest season to include")
    wins_parser.set_defaults(func=cmd_wins)

    points_parser = subparsers.add_parser("points", help="Season points progression")
    points_parser.add_argument("--year", type=int, required=True, help="Season year")
    points_parser.add_argument("--drivers", nargs="+", required=True, help="Driver surnames, space-separated")
    points_parser.set_defaults(func=cmd_points)

    grid_parser = subparsers.add_parser("grid", help="Grid vs finish position scatter")
    grid_parser.add_argument("--year", type=int, required=True, help="Season year")
    grid_parser.set_defaults(func=cmd_grid)

    return parser


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)