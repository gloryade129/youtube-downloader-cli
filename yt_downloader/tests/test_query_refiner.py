import unittest
from yt_downloader.query_refiner import refine_query, RefinedQuery


class TestQueryRefiner(unittest.TestCase):

    def test_refine_acoustic_live(self):
        prompt = "please search for acoustic live version of Hotel California in mp3"
        result = refine_query(prompt, current_format="mp3")
        
        self.assertIn("acoustic", result.tags_detected)
        self.assertIn("live", result.tags_detected)
        self.assertEqual(result.suggested_format, "mp3")
        self.assertIn("Hotel California", result.cleaned_query)

    def test_refine_mp4_video(self):
        prompt = "download HD video clip of python tutorial in mp4"
        result = refine_query(prompt, current_format="mp3")
        
        self.assertEqual(result.suggested_format, "mp4")
        self.assertIn("Python Tutorial", result.cleaned_query)

    def test_fallback_query(self):
        prompt = "Hotel California"
        result = refine_query(prompt, current_format="flac")
        self.assertEqual(result.cleaned_query, "Hotel California")
        self.assertEqual(result.suggested_format, "flac")


if __name__ == "__main__":
    unittest.main()
