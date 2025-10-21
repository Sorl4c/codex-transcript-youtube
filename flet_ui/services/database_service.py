from __future__ import annotations

from typing import Dict, Iterable, List, Optional

import db

from config.settings import get_settings
from models.video import Video


class DatabaseService:
    """Wrapper around the legacy sqlite helpers with higher level helpers."""

    def __init__(self, db_module=db):
        self._db = db_module
        self._db.init_db()
        self._settings = get_settings()

    # --- Queries --------------------------------------------------------------------

    def get_all_videos(self) -> List[Video]:
        rows = self._db.get_all_videos(
            order_by=self._settings.default_sort_field,
            order_dir=self._settings.default_sort_direction.upper(),
        )
        return [Video.from_listing(row) for row in rows]

    def search_videos(self, query: str, *, order_by: str, order_dir: str) -> List[Video]:
        """Return videos filtered by query matching title or channel."""

        normalized_query = (query or "").strip()
        if not normalized_query:
            return self.get_all_videos()

        results: Dict[int, Video] = {}

        for field in ("title", "channel"):
            try:
                rows = self._db.filter_videos(
                    by_field=field,
                    value=normalized_query,
                    order_by=order_by,
                    order_dir=order_dir.upper(),
                )
            except ValueError:
                continue
            for row in rows:
                video = Video.from_listing(row)
                results[video.id] = video

        return list(results.values())

    def get_video_details(self, video_id: int) -> Optional[Video]:
        row = self._db.get_video_by_id(video_id)
        if not row:
            return None
        return Video.from_full_record(row)

    # --- Mutations -------------------------------------------------------------------

    def delete_video(self, video_id: int) -> bool:
        return bool(self._db.delete_video(video_id))

    def update_summary(self, video_id: int, summary: str) -> bool:
        return bool(self._db.update_video_summary(video_id, summary))
