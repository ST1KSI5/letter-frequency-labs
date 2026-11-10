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
        self.assertIn("а ## 2", render_histogram({"а":2}))
    def test_long_chart(self):
        result=render_histogram({"а":100})
        self.assertIn("#"*60+"… 100", result)
        self.assertNotIn("#"*61, result)
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
            self.assertIn("ї ## 2",out.getvalue())
    def test_bad_file(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"bad.txt"; p.write_bytes(b"\xff\xfe")
            with contextlib.redirect_stderr(io.StringIO()): self.assertEqual(main(["--file",str(p)]),2)
    def test_missing_file(self):
        with contextlib.redirect_stderr(io.StringIO()): self.assertEqual(main(["--file","__missing_7__.txt"]),2)
class ThresholdTests(unittest.TestCase):
    def test_filters_inclusively_without_changing_totals(self):
        counts = {"а": 4, "б": 2, "в": 1}
        result = render_histogram(counts, 2)
        self.assertIn("а ", result)
        self.assertIn("б ", result)
        self.assertNotIn("в #", result)
        self.assertIn("Усього літер: 7; різних: 3", result)
        self.assertIn("Показано різних літер: 2; поріг: 2.", result)
        self.assertEqual(counts, {"а": 4, "б": 2, "в": 1})

    def test_exact_maximum_boundary(self):
        result = render_histogram({"а": 4, "б": 2}, 4)
        self.assertIn("а ", result)
        self.assertNotIn("б #", result)

    def test_no_matches_and_empty_input(self):
        self.assertEqual(render_histogram({"а": 4}, 5),
                         "Літер із частотою не меншою за 5 не знайдено.")
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
        self.assertIn("а ", output.getvalue())
        self.assertIn("б ", output.getvalue())
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
            with contextlib.redirect_stdout(output):
                self.assertEqual(main(["--file", str(path), "--min-count", "2"]), 0)
            self.assertNotIn("в #", output.getvalue())

if __name__ == "__main__": unittest.main()

