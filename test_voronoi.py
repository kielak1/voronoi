import tempfile
import unittest
from pathlib import Path

from voronoi import Bounds, Canvas, Point, generate_voronoi, main, unique_points


class VoronoiTests(unittest.TestCase):
    def test_generates_triangle_cells(self) -> None:
        diagram = generate_voronoi([Point(0, 0), Point(4, 0), Point(2, 3)])

        self.assertEqual(len(diagram.cells), 3)
        self.assertTrue(all(len(cell.vertices) >= 3 for cell in diagram.cells))

    def test_handles_obtuse_triangle(self) -> None:
        diagram = generate_voronoi([Point(0, 0), Point(6, 0), Point(1, 1)])

        self.assertEqual(len(diagram.cells), 3)
        self.assertTrue(all(cell.edges for cell in diagram.cells))

    def test_handles_collinear_vertical_points(self) -> None:
        diagram = generate_voronoi([Point(2, 0), Point(2, 2), Point(2, 4)])

        self.assertEqual(len(diagram.cells), 3)
        self.assertGreater(diagram.bounds.width, 0)
        self.assertGreater(diagram.bounds.height, 0)

    def test_handles_collinear_horizontal_points(self) -> None:
        diagram = generate_voronoi([Point(0, 2), Point(2, 2), Point(4, 2)])

        self.assertEqual(len(diagram.cells), 3)
        self.assertTrue(all(len(cell.vertices) == 4 for cell in diagram.cells))

    def test_removes_duplicate_points(self) -> None:
        points = [Point(1, 1), Point(1, 1), Point(2, 2)]

        self.assertEqual(unique_points(points), [Point(1, 1), Point(2, 2)])
        self.assertEqual(len(generate_voronoi(points).cells), 2)

    def test_canvas_maps_different_axis_ranges(self) -> None:
        bounds = Bounds(10, 20, 30, 60)
        canvas = Canvas(bounds)

        self.assertEqual(canvas.map_point(Point(10, 20)), (0.0, 800.0))
        self.assertEqual(canvas.map_point(Point(30, 60)), (800.0, 0.0))

    def test_single_point_fills_bounds(self) -> None:
        diagram = generate_voronoi([Point(1, 1)])

        self.assertEqual(len(diagram.cells), 1)
        self.assertEqual(len(diagram.cells[0].vertices), 4)

    def test_empty_points_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            generate_voronoi([])

    def test_cli_saves_png(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "diagram.png"

            result = main(["--output", str(output), "--points", "0,0", "2,0", "1,2"])

            self.assertEqual(result, 0)
            self.assertTrue(output.exists())
            self.assertGreater(output.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
