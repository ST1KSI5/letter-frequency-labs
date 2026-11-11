import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from main import count_letters, render_histogram, main

class FrequencyTests(unittest.TestCase):
    def test_case_and_punctuation(self):
        self.assertEqual(count_letters("Абба! 123"), {"а": 2, "б": 2})
    def test_ukrainian(self):
        self.assertEqual(count_letters("Ґґ Єє Іі Її Йй"), {"ґ":2,"є":2,"і":2,"ї":2,"й":2})
    def test_unicode_normalization(self):
        self.assertEqual(count_letters("і\u0308И\u0306"), {"ї":1,"й":1})
    def test_mixed_alphabets(self):
        self.assertEqual(count_letters("AаAa"), {"a":3,"а":1})
    def test_empty_counter(self):
        self.assertEqual(count_letters("123 !"), {})
    def test_chart(self):
        self.assertIn("а "+"#"*50+" 2", render_histogram({"а":2}))
    def test_long_chart(self):
        result=render_histogram({"а":100})
        self.assertIn("#"*50+" 100", result)
        self.assertNotIn("#"*51, result)
    def run_input(self,text):
        from unittest.mock import patch
        output=io.StringIO()
        with patch("builtins.input",return_value=text), contextlib.redirect_stderr(output):
            code=main([])
        return code,output.getvalue()
    def test_empty_input(self):
        self.assertEqual(self.run_input("  ")[0],2)
    def test_no_letters(self):
        self.assertEqual(self.run_input("123!")[0],2)
    def test_utf8_file(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"text.txt"; p.write_text("Їжак\nїсть",encoding="utf-8-sig")
            out=io.StringIO()
            with contextlib.redirect_stdout(out): self.assertEqual(main(["--file",str(p)]),0)
            self.assertIn("ї "+"#"*50+" 2",out.getvalue())
    def test_bad_file(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"bad.txt"; p.write_bytes(b"\xff\xfe")
            with contextlib.redirect_stderr(io.StringIO()): self.assertEqual(main(["--file",str(p)]),2)
    def test_missing_file(self):
        with contextlib.redirect_stderr(io.StringIO()): self.assertEqual(main(["--file","__missing_7__.txt"]),2)
class ScalingTests(unittest.TestCase):
    def test_relative_widths(self):
        result = render_histogram({"а": 4, "б": 2})
        self.assertIn("а " + "#" * 50 + " 4", result)
        self.assertIn("б " + "#" * 25 + " 2", result)

    def test_single_letter_and_tied_maxima(self):
        self.assertIn("а " + "#" * 50 + " 1", render_histogram({"а": 1}))
        result = render_histogram({"а": 3, "б": 3})
        self.assertIn("а " + "#" * 50 + " 3", result)
        self.assertIn("б " + "#" * 50 + " 3", result)

    def test_rounding_half_up_and_visible_rare_letter(self):
        result = render_histogram({"а": 100, "б": 1})
        self.assertIn("б # 1", result)
        result = render_histogram({"а": 100, "б": 3})
        self.assertIn("б ## 3", result)

    def test_does_not_mutate_counts(self):
        counts = {"б": 2, "а": 4}
        original = counts.copy()
        render_histogram(counts)
        self.assertEqual(counts, original)

class ThresholdTests(unittest.TestCase):
    def test_filters_inclusively_without_changing_totals(self):
        counts = {"а": 4, "б": 2, "в": 1}
        result = render_histogram(counts, 2)
        self.assertIn("а " + "#" * 50 + " 4", result.splitlines())
        self.assertIn("б " + "#" * 25 + " 2", result.splitlines())
        self.assertNotIn("в #", result)
        self.assertIn("Усього літер: 7; різних: 3", result)
        self.assertIn("Показано різних літер: 2; поріг: 2.", result)
        self.assertEqual(counts, {"а": 4, "б": 2, "в": 1})

    def test_exact_maximum_boundary(self):
        result = render_histogram({"а": 4, "б": 2}, 4)
        self.assertIn("а " + "#" * 50 + " 4", result.splitlines())
        self.assertNotIn("б #", result)

    def test_no_matches_and_empty_input(self):
        counts = {"а": 4}
        self.assertEqual(render_histogram(counts, 5),
                         "Літер із частотою не меншою за 5 не знайдено.\n"
                         "Усього літер: 4; різних: 1\n"
                         "Показано різних літер: 0; поріг: 5.")
        self.assertEqual(counts, {"а": 4})
        self.assertEqual(render_histogram({}, 2), "Літер не знайдено.")

    def test_invalid_threshold_api(self):
        for value in (0, -1, 1.5, True, "2"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                render_histogram({"а": 4}, value)

    def test_cli_threshold(self):
        from unittest.mock import patch
        output = io.StringIO()
        with patch("builtins.input", return_value="ааааббв"), contextlib.redirect_stdout(output):
            self.assertEqual(main(["--min-count", "2"]), 0)
        self.assertIn("а " + "#" * 50 + " 4", output.getvalue().splitlines())
        self.assertIn("б " + "#" * 25 + " 2", output.getvalue().splitlines())
        self.assertNotIn("в #", output.getvalue())

    def test_cli_invalid_thresholds(self):
        for value in ("0", "-1", "1.5", "abc"):
            with self.subTest(value=value), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as error:
                    main(["--min-count", value])
                self.assertEqual(error.exception.code, 2)

    def test_file_threshold(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.txt"
            path.write_text("Аааа\nБбв", encoding="utf-8-sig")
            output = io.StringIO()
            errors = io.StringIO()
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
                self.assertEqual(main(["--file", str(path), "--min-count", "2"]), 0)
            self.assertIn("а " + "#" * 50 + " 4", output.getvalue().splitlines())
            self.assertIn("б " + "#" * 25 + " 2", output.getvalue().splitlines())
            self.assertIn("Усього літер: 7; різних: 3", output.getvalue().splitlines())
            self.assertIn("Показано різних літер: 2; поріг: 2.", output.getvalue().splitlines())
            self.assertNotIn("в #", output.getvalue())
            self.assertEqual(errors.getvalue(), "")

class CombinedFeatureTests(unittest.TestCase):
    def test_both_tasks_in_one_cli_run(self):
        from unittest.mock import patch
        output = io.StringIO()
        with patch("builtins.input", return_value="ааааббв"), contextlib.redirect_stdout(output):
            self.assertEqual(main(["--min-count", "2"]), 0)
        result = output.getvalue()
        self.assertIn("а " + "#" * 50 + " 4", result)
        self.assertIn("б " + "#" * 25 + " 2", result)
        self.assertNotIn("в #", result)
        self.assertIn("Усього літер: 7; різних: 3", result)

    def test_threshold_above_maximum_is_successful_cli_result(self):
        from unittest.mock import patch
        output = io.StringIO()
        errors = io.StringIO()
        with patch("builtins.input", return_value="ааааббв"), \
                contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            self.assertEqual(main(["--min-count", "5"]), 0)
        self.assertIn("не знайдено", output.getvalue())
        self.assertIn("Усього літер: 7; різних: 3", output.getvalue().splitlines())
        self.assertIn("Показано різних літер: 0; поріг: 5.", output.getvalue().splitlines())
        self.assertNotIn("#", output.getvalue())
        self.assertEqual(errors.getvalue(), "")

    def test_filtered_tied_maxima_are_both_fifty(self):
        result = render_histogram({"а": 4, "б": 4, "в": 1}, 4)
        self.assertIn("а " + "#" * 50 + " 4", result)
        self.assertIn("б " + "#" * 50 + " 4", result)
        self.assertNotIn("в #", result)

if __name__ == "__main__": unittest.main()
