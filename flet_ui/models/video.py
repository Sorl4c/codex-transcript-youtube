from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class Video:
    """Simple data structure representing a video entry."""

    id: int
    title: str
    channel: str
    upload_date: str
    transcript: str = ""
    summary: str = ""
    url: str = ""
    key_ideas: Optional[str] = None
    ai_categorization: Optional[str] = None

    @classmethod
    def from_listing(cls, data: Dict[str, Any]) -> "Video":
        return cls(
            id=int(data.get("id")),
            title=data.get("title", "Sin título"),
            channel=data.get("channel", "Desconocido"),
            upload_date=_normalize_date(data.get("upload_date")),
        )

    @classmethod
    def from_full_record(cls, data: Dict[str, Any]) -> "Video":
        return cls(
            id=int(data.get("id")),
            title=data.get("title", "Sin título"),
            channel=data.get("channel", "Desconocido"),
            upload_date=_normalize_date(data.get("upload_date")),
            transcript=data.get("transcript", ""),
            summary=data.get("summary", ""),
            url=data.get("url", ""),
            key_ideas=data.get("key_ideas"),
            ai_categorization=data.get("ai_categorization"),
        )

    def matches_query(self, query: str) -> bool:
        query = query.lower()
        return query in self.title.lower() or query in self.channel.lower()


def _normalize_date(raw_date: Optional[str]) -> str:
    if not raw_date:
        return ""
    if isinstance(raw_date, str) and len(raw_date) == 8 and raw_date.isdigit():
        return f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}"
    return raw_date or ""
