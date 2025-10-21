from __future__ import annotations

import re
from typing import Dict, Optional, Tuple

from downloader import download_vtt
from parser import format_transcription, vtt_to_plain_text


class YouTubeService:
    """Thin wrapper around downloader/parser modules for the Flet UI."""

    VIDEO_ID_PATTERNS = (
        r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/v/|youtube\.com/e/|youtube\.com/watch\?.*&v=)([^#\&\?\n]*)",
        r"youtube\.com/shorts/([^#\&\?\n]*)",
        r"youtube\.com/live/([^#\&\?\n]*)",
    )

    def get_video_id_from_url(self, url: str) -> str:
        if not url:
            return ""
        for pattern in self.VIDEO_ID_PATTERNS:
            match = re.search(pattern, url, re.IGNORECASE)
            if match and match.group(1):
                return match.group(1)
        return url.strip()

    def fetch_transcript(
        self, url: str, *, lang: str = "es", keep_timestamps: bool = False
    ) -> Optional[Dict[str, str]]:
        """Download subtitles and return both raw and formatted transcript data."""

        vtt_content, detected_lang, metadata = download_vtt(url, lang=lang)
        if not vtt_content or not metadata:
            return None

        remove_timestamps = not keep_timestamps
        plain_text = vtt_to_plain_text(vtt_content, remove_timestamps=remove_timestamps)
        formatted_transcript = format_transcription(
            plain_text,
            title=metadata.get("title"),
            url=url,
        )
        return {
            "transcript": formatted_transcript,
            "plain_text": plain_text,
            "language": detected_lang or lang,
            "metadata": metadata,
        }

    def build_video_payload(
        self,
        url: str,
        *,
        keep_timestamps: bool = False,
    ) -> Optional[Dict[str, Optional[str]]]:
        """Return a dictionary ready to be inserted in database."""

        result = self.fetch_transcript(url, keep_timestamps=keep_timestamps)
        if not result:
            return None

        metadata = result["metadata"]
        upload_date = self._normalize_date(metadata.get("publish_date") or metadata.get("upload_date"))
        return {
            "url": url,
            "channel": metadata.get("channel", "N/A"),
            "title": metadata.get("title", "Título no disponible"),
            "upload_date": upload_date or "",
            "transcript": result["transcript"],
            "summary": "",
            "key_ideas": "",
            "ai_categorization": "",
        }

    @staticmethod
    def _normalize_date(raw_date: Optional[str]) -> Optional[str]:
        if not raw_date:
            return None
        if len(raw_date) == 8 and raw_date.isdigit():
            # Original format YYYYMMDD
            return f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}"
        return raw_date
