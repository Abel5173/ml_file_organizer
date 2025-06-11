from utils.cache import load_cache, cache_category, get_cached_category
from utils.classify import classify_file
import os
import unittest


class TestOrganizer(unittest.TestCase):
    def setUp(self):
        self.config = {
            "base_categories": ["Documents", "Pictures", "Telegram Desktop"],
            "api": {
                "text_model": "facebook/bart-large-mnli",
                "vision_model": "google/vit-base-patch16-224",
                "text_limit": 512,
                "huggingface_token": "mock_token",
                "rate_limit": {"max_requests_per_hour": 300, "retry_delay": 60}
            }
        }
        self.token = "mock_token"
        self.downloads_dir = "/tmp/test_downloads"
        os.makedirs(self.downloads_dir, exist_ok=True)

    def test_classify_pdf(self):
        result = classify_file("test.pdf", self.token,
                               self.config, self.downloads_dir)
        self.assertTrue(result.startswith("Documents/"))
        self.assertTrue(os.path.exists(
            os.path.join(self.downloads_dir, result)))

    def test_classify_image(self):
        result = classify_file("test.jpg", self.token,
                               self.config, self.downloads_dir)
        self.assertTrue(result.startswith("Pictures/"))
        self.assertTrue(os.path.exists(
            os.path.join(self.downloads_dir, result)))

    def test_classify_telegram_pdf(self):
        result = classify_file("Telegram Desktop/test.pdf",
                               self.token, self.config, self.downloads_dir)
        self.assertTrue(result.startswith("Telegram Desktop/"))
        self.assertTrue(os.path.exists(
            os.path.join(self.downloads_dir, result)))

    def test_cache(self):
        file_path = "test.pdf"
        category = "Documents/Invoices"
        cache = load_cache()
        cache_category(file_path, category, cache)
        self.assertEqual(get_cached_category(
            file_path, load_cache()), category)


if __name__ == "__main__":
    unittest.main()
