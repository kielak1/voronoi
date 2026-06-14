from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from PIL import Image, ImageDraw

EPSILON = 1e-9
DEFAULT_POINTS = (
    (2.0, 3.0),
    (1.0, 1.0),
    (3.0, 0.0),
    (5.0, 1.0),
)


@dataclass(frozen=True, slots=True)
class Point:
    x: float
    y: float

    def distance_squared(self, other: Point) -> float:
        return (self.x - other.x) ** 2 + (self.y - other.y) ** 2

    def almost_equals(self, other: Point, epsilon: float = EPSILON) -> bool:
        return (
            abs(self.x - other.x) <= epsilon
            and abs(self.y - other.y) <= epsilon
        )


@dataclass(frozen=True, slots=True)
class Segment:
    start: Point
    end: Point


@dataclass(frozen=True, slots=True)
class Bounds:
    min_x: float
    min_y: float
    max_x: float
    max_y: float

    def __post_init__(self) -> None:
        if self.min_x >= self.max_x or self.min_y >= self.max_y:
            raise ValueError("Bounds must have positive width and height.")

    @property
    def width(self) -> float:
        return self.max_x - self.min_x

    @property
    def height(self) -> float:
        return self.max_y - self.min_y

    def polygon(self) -> list[Point]:
        return [
            Point(self.min_x, self.min_y),
            Point(self.max_x, self.min_y),
            Point(self.max_x, self.max_y),
            Point(self.min_x, self.max_y),
        ]

    @classmethod
    def around(cls, points: Sequence[Point], padding: float = 0.2) -> Bounds:
        if not points:
            raise ValueError("At least one point is required.")
        if padding < 0:
            raise ValueError("Padding cannot be negative.")

        min_x = min(point.x for point in points)
        max_x = max(point.x for point in points)
        min_y = min(point.y for point in points)
        max_y = max(point.y for point in points)
        span = max(max_x - min_x, max_y - min_y, 1.0)
        margin = span * padding

        if math.isclose(min_x, max_x, abs_tol=EPSILON):
            min_x -= span / 2
            max_x += span / 2
        if math.isclose(min_y, max_y, abs_tol=EPSILON):
            min_y -= span / 2
            max_y += span / 2

        return cls(min_x - margin, min_y - margin, max_x + margin, max_y + margin)


@dataclass(frozen=True, slots=True)
class Cell:
    site: Point
    vertices: tuple[Point, ...]

    @property
    def edges(self) -> tuple[Segment, ...]:
        if len(self.vertices) < 2:
            return ()
        return tuple(
            Segment(vertex, self.vertices[(index + 1) % len(self.vertices)])
            for index, vertex in enumerate(self.vertices)
        )


@dataclass(frozen=True, slots=True)
class VoronoiDiagram:
    bounds: Bounds
    cells: tuple[Cell, ...]


def unique_points(points: Iterable[Point]) -> list[Point]:
    result: list[Point] = []
    for point in points:
        if not any(point.almost_equals(existing) for existing in result):
            result.append(point)
    return result


def _half_plane_value(point: Point, site: Point, other: Point) -> float:
    # Values <= 0 are at least as close to site as to other.
    return (
        2 * point.x * (other.x - site.x)
        + 2 * point.y * (other.y - site.y)
        + site.x**2
        + site.y**2
        - other.x**2
        - other.y**2
    )


def _intersection(
    start: Point,
    end: Point,
    start_value: float,
    end_value: float,
) -> Point:
    denominator = start_value - end_value
    if abs(denominator) <= EPSILON:
        return start
    ratio = start_value / denominator
    return Point(
        start.x + ratio * (end.x - start.x),
        start.y + ratio * (end.y - start.y),
    )


def clip_polygon(
    polygon: Sequence[Point],
    site: Point,
    other: Point,
) -> list[Point]:
    if not polygon or site.almost_equals(other):
        return list(polygon)

    clipped: list[Point] = []
    previous = polygon[-1]
    previous_value = _half_plane_value(previous, site, other)
    previous_inside = previous_value <= EPSILON

    for current in polygon:
        current_value = _half_plane_value(current, site, other)
        current_inside = current_value <= EPSILON

        if current_inside != previous_inside:
            clipped.append(
                _intersection(previous, current, previous_value, current_value)
            )
        if current_inside:
            clipped.append(current)

        previous = current
        previous_value = current_value
        previous_inside = current_inside

    return clipped


def generate_voronoi(
    points: Iterable[Point],
    bounds: Bounds | None = None,
    padding: float = 0.2,
) -> VoronoiDiagram:
    sites = unique_points(points)
    if not sites:
        raise ValueError("At least one unique point is required.")

    diagram_bounds = bounds or Bounds.around(sites, padding)
    cells: list[Cell] = []

    for site in sites:
        polygon = diagram_bounds.polygon()
        for other in sites:
            if not site.almost_equals(other):
                polygon = clip_polygon(polygon, site, other)
                if not polygon:
                    break
        cells.append(Cell(site, tuple(polygon)))

    return VoronoiDiagram(diagram_bounds, tuple(cells))


class Canvas:
    def __init__(self, bounds: Bounds, width: int = 800, height: int = 800):
        if width <= 0 or height <= 0:
            raise ValueError("Canvas dimensions must be positive.")
        self.bounds = bounds
        self.width = width
        self.height = height
        self.image = Image.new("RGB", (width, height), "white")
        self.draw = ImageDraw.Draw(self.image)

    def map_point(self, point: Point) -> tuple[float, float]:
        x = (point.x - self.bounds.min_x) / self.bounds.width * self.width
        y = self.height - (
            (point.y - self.bounds.min_y) / self.bounds.height * self.height
        )
        return x, y

    def render(self, diagram: VoronoiDiagram) -> Image.Image:
        for cell in diagram.cells:
            if len(cell.vertices) >= 3:
                polygon = [self.map_point(vertex) for vertex in cell.vertices]
                self.draw.polygon(
                    polygon,
                    fill=_site_color(cell.site),
                    outline=(45, 45, 45),
                    width=2,
                )

        radius = max(3, min(self.width, self.height) // 120)
        for cell in diagram.cells:
            x, y = self.map_point(cell.site)
            self.draw.ellipse(
                (x - radius, y - radius, x + radius, y + radius),
                fill=(10, 10, 10),
                outline=(255, 255, 255),
                width=1,
            )
        return self.image


def _site_color(site: Point) -> tuple[int, int, int]:
    seed = int(abs(site.x * 73856093 + site.y * 19349663))
    return (
        80 + seed % 150,
        80 + (seed // 7) % 150,
        80 + (seed // 17) % 150,
    )


def parse_points(values: Sequence[str]) -> list[Point]:
    points: list[Point] = []
    for value in values:
        try:
            x_text, y_text = value.split(",", maxsplit=1)
            points.append(Point(float(x_text), float(y_text)))
        except ValueError as error:
            raise argparse.ArgumentTypeError(
                f"Invalid point '{value}'. Expected format: x,y"
            ) from error
    return points


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a bounded Voronoi diagram.")
    parser.add_argument(
        "--points",
        nargs="+",
        metavar="X,Y",
        help="Sites in x,y format. Uses a built-in example when omitted.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("voronoi.png"),
        help="Output PNG path (default: voronoi.png).",
    )
    parser.add_argument("--width", type=int, default=800)
    parser.add_argument("--height", type=int, default=800)
    parser.add_argument("--padding", type=float, default=0.2)
    parser.add_argument("--show", action="store_true", help="Open the generated image.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    points = (
        parse_points(args.points)
        if args.points
        else [Point(x, y) for x, y in DEFAULT_POINTS]
    )
    diagram = generate_voronoi(points, padding=args.padding)
    image = Canvas(diagram.bounds, args.width, args.height).render(diagram)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.output)
    print(f"Saved Voronoi diagram to {args.output.resolve()}")
    if args.show:
        image.show()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
