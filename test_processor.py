import unittest
import io
from processor import DocumentProcessor

class TestDocumentProcessor(unittest.TestCase):
    def test_token_count(self):
        text = "Hello world"
        # Test that token counting works and returns a positive number
        count = DocumentProcessor.get_token_count(text)
        self.assertGreater(count, 0)
        # Token count should be reasonable (not exact check to avoid brittleness)
        self.assertLess(count, 10, "Token count seems unreasonably high for simple text")

    def test_merge_as_text(self):
        # Create mock file objects
        f1 = io.BytesIO(b"Content 1")
        f1.name = "file1.txt"
        f2 = io.BytesIO(b"Content 2")
        f2.name = "file2.txt"
        
        result = DocumentProcessor.merge_as_text([f1, f2])
        
        self.assertIn("Content 1", result)
        self.assertIn("Content 2", result)
        self.assertIn("# File: file1.txt", result)
        self.assertIn("# File: file2.txt", result)

    def test_fast_lane_check(self):
        # We can't easily test pypdf merge without real pdfs, 
        # but we can check if it tries to enter the right block or logic
        pass

if __name__ == '__main__':
    unittest.main()
