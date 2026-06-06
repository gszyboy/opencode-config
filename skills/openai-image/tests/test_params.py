"""Unit tests for the pure helpers in lib/params.py.

Run with:  python3 -m unittest tests.test_params -v
"""

from __future__ import annotations

import unittest

import sys
from pathlib import Path

# Make the scripts/lib directory importable.
SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from lib import params  # noqa: E402


class ResolveSizeTests(unittest.TestCase):
    def test_aliases(self):
        self.assertEqual(params.resolve_size("1k"), "1024x1024")
        self.assertEqual(params.resolve_size("square"), "1024x1024")
        self.assertEqual(params.resolve_size("portrait"), "1024x1536")
        self.assertEqual(params.resolve_size("landscape"), "1536x1024")
        self.assertEqual(params.resolve_size("4k"), "3840x2160")
        self.assertEqual(params.resolve_size("auto"), "auto")

    def test_literal_passes(self):
        self.assertEqual(params.resolve_size("1536x1024"), "1536x1024")
        self.assertEqual(params.resolve_size("2048x1152"), "2048x1152")

    def test_literal_16_multiple_required(self):
        with self.assertRaises(ValueError):
            params.resolve_size("1003x1003")

    def test_literal_max_edge(self):
        with self.assertRaises(ValueError):
            params.resolve_size("4096x1024")

    def test_literal_aspect_ratio(self):
        with self.assertRaises(ValueError):
            params.resolve_size("4096x512")  # 8:1 > 3:1

    def test_literal_too_few_pixels(self):
        with self.assertRaises(ValueError):
            params.resolve_size("512x512")  # 262144 < 655360

    def test_experimental_flag(self):
        self.assertTrue(params.is_experimental("3840x2160"))
        self.assertTrue(params.is_experimental("3008x2000"))
        self.assertFalse(params.is_experimental("2560x1440"))
        self.assertFalse(params.is_experimental("2048x2048"))


class ResolveQualityTests(unittest.TestCase):
    def test_canonical(self):
        self.assertEqual(params.resolve_quality("low"), "low")
        self.assertEqual(params.resolve_quality("high"), "high")
        self.assertEqual(params.resolve_quality("auto"), "auto")

    def test_aliases(self):
        self.assertEqual(params.resolve_quality("draft"), "low")
        self.assertEqual(params.resolve_quality("preview"), "low")
        self.assertEqual(params.resolve_quality("normal"), "medium")
        self.assertEqual(params.resolve_quality("standard"), "medium")
        self.assertEqual(params.resolve_quality("final"), "high")
        self.assertEqual(params.resolve_quality("print"), "high")

    def test_default(self):
        self.assertEqual(params.resolve_quality(None), "high")
        self.assertEqual(params.resolve_quality(""), "high")

    def test_bad_value(self):
        with self.assertRaises(ValueError):
            params.resolve_quality("ultra")


class ResolveFormatTests(unittest.TestCase):
    def test_canonical(self):
        self.assertEqual(params.resolve_format("png"), "png")
        self.assertEqual(params.resolve_format("jpeg"), "jpeg")
        self.assertEqual(params.resolve_format("webp"), "webp")

    def test_jpg_alias(self):
        self.assertEqual(params.resolve_format("jpg"), "jpeg")
        self.assertEqual(params.resolve_format("JPG"), "jpeg")

    def test_default(self):
        self.assertEqual(params.resolve_format(None), "png")
        self.assertEqual(params.resolve_format(""), "png")

    def test_bad_value(self):
        with self.assertRaises(ValueError):
            params.resolve_format("gif")


class ResolveBackgroundTests(unittest.TestCase):
    def test_canonical(self):
        self.assertEqual(params.resolve_background("transparent"), "transparent")
        self.assertEqual(params.resolve_background("opaque"), "opaque")
        self.assertEqual(params.resolve_background("auto"), "auto")

    def test_default(self):
        self.assertEqual(params.resolve_background(None), "auto")
        self.assertEqual(params.resolve_background(""), "auto")

    def test_bad_value(self):
        with self.assertRaises(ValueError):
            params.resolve_background("white")


class ResolveModerationTests(unittest.TestCase):
    def test_canonical(self):
        self.assertEqual(params.resolve_moderation("low"), "low")
        self.assertEqual(params.resolve_moderation("auto"), "auto")

    def test_default(self):
        self.assertEqual(params.resolve_moderation(None), "auto")
        self.assertEqual(params.resolve_moderation(""), "auto")

    def test_bad_value(self):
        with self.assertRaises(ValueError):
            params.resolve_moderation("high")


class LooksLikeUnsupportedFieldErrorTests(unittest.TestCase):
    def test_background_400(self):
        m = params.looks_like_unsupported_field_error("400: unknown field 'background'")
        self.assertEqual(m, "background")

    def test_moderation_400(self):
        m = params.looks_like_unsupported_field_error(
            "Bad Request: this gateway does not support moderation"
        )
        self.assertEqual(m, "moderation")

    def test_unrelated(self):
        m = params.looks_like_unsupported_field_error("insufficient_quota")
        self.assertIsNone(m)


if __name__ == "__main__":
    unittest.main(verbosity=2)
