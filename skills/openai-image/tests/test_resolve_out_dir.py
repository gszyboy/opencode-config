"""Unit tests for lib/image_io.resolve_out_dir.

Run with:  python3 -m unittest tests.test_resolve_out_dir -v
"""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from lib import image_io  # noqa: E402


class ResolveOutDirTests(unittest.TestCase):
    def setUp(self):
        self._cwd = os.getcwd()

    def tearDown(self):
        os.chdir(self._cwd)

    def test_default_is_cwd_gpt_image_out(self):
        os.chdir("/tmp")
        out = image_io.resolve_out_dir()
        self.assertEqual(out, Path("/tmp") / "gpt_image_out")

    def test_explicit_arg_wins_over_default(self):
        os.chdir("/tmp")
        out = image_io.resolve_out_dir(explicit="/srv/explicit")
        self.assertEqual(out, Path("/srv/explicit"))

    def test_explicit_arg_handles_tilde(self):
        os.chdir("/tmp")
        out = image_io.resolve_out_dir(explicit="~/pics")
        self.assertNotIn("~", str(out))


class LegacyDefaultShimTests(unittest.TestCase):
    def test_legacy_default_still_defined(self):
        self.assertTrue(hasattr(image_io, "DEFAULT_OUT_DIR"))
        self.assertIsInstance(image_io.DEFAULT_OUT_DIR, Path)
        self.assertEqual(image_io.DEFAULT_OUT_DIR.name, "gpt_image_out")


class DefaultOutDirnameTests(unittest.TestCase):
    def test_constant_is_string(self):
        self.assertIsInstance(image_io.DEFAULT_OUT_DIRNAME, str)
        self.assertEqual(image_io.DEFAULT_OUT_DIRNAME, "gpt_image_out")


if __name__ == "__main__":
    unittest.main(verbosity=2)
