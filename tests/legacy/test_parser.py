import unittest
import io
from parser import vtt_to_plain_text_stream, format_transcription, vtt_to_plain_text

class TestParser(unittest.TestCase):

    def test_vtt_to_plain_text_stream_basic(self):
        vtt_data = [
            "WEBVTT",
            "Kind: captions",
            "Language: en",
            "",
            "00:00:01.000 --> 00:00:03.000",
            "Hello world",
            "",
            "00:00:04.000 --> 00:00:06.000",
            "This is a test"
        ]
        iterator = iter(vtt_data)
        result = list(vtt_to_plain_text_stream(iterator))
        self.assertEqual(result, ["Hello world", "This is a test"])

    def test_vtt_to_plain_text_stream_with_duplicates(self):
        vtt_data = [
            "WEBVTT",
            "00:00:01.000 --> 00:00:03.000",
            "Repeat this line",
            "Repeat this line",
            "",
            "00:00:04.000 --> 00:00:06.000",
            "This is unique"
        ]
        iterator = iter(vtt_data)
        result = list(vtt_to_plain_text_stream(iterator))
        self.assertEqual(result, ["Repeat this line", "This is unique"])

    def test_vtt_to_plain_text_stream_empty(self):
        vtt_data = []
        iterator = iter(vtt_data)
        result = list(vtt_to_plain_text_stream(iterator))
        self.assertEqual(result, [])

    def test_vtt_to_plain_text_stream_only_metadata(self):
        vtt_data = [
            "WEBVTT",
            "Kind: captions",
            "Language: en",
            "STYLE",
            "::cue { color: white; }"
        ]
        iterator = iter(vtt_data)
        result = list(vtt_to_plain_text_stream(iterator))
        self.assertEqual(result, [])

    def test_vtt_to_plain_text_wrapper(self):
        vtt_string = "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\nHello again"
        result = vtt_to_plain_text(vtt_string)
        self.assertEqual(result, "Hello again")

    def test_format_transcription_with_title_and_url(self):
        text_content = "This is the main content."
        result = format_transcription(text_content, title="My Video", url="http://example.com")
        expected = "Título: My Video\nURL: http://example.com\n\nThis is the main content."
        self.assertEqual(result, expected)

    def test_format_transcription_no_metadata(self):
        text_content = "Just content."
        result = format_transcription(text_content)
        self.assertEqual(result, "Just content.")

    def test_format_transcription_multiline_to_single_paragraph(self):
        text_content = "First line.\nSecond line.\n  Third line with spaces.  "
        result = format_transcription(text_content)
        expected = "First line. Second line. Third line with spaces."
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
