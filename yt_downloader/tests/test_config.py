import unittest
import os
import tempfile
from pathlib import Path
from yt_downloader.config import load_config, save_config, check_ffmpeg


class TestConfig(unittest.TestCase):

    def test_load_config_defaults(self):
        config = load_config()
        self.assertIn("download_dir", config)
        self.assertIn("default_format", config)

    def test_check_ffmpeg(self):
        ok, path = check_ffmpeg()
        self.assertIsInstance(ok, bool)
        self.assertIsInstance(path, str)


if __name__ == "__main__":
    unittest.main()
