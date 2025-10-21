from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, TYPE_CHECKING

from config.settings import AppSettings, get_settings

if TYPE_CHECKING:
    from models.video import Video


@dataclass
class SessionState:
    """Simple session container shared across pages and components."""

    settings: AppSettings = field(default_factory=get_settings)
    videos: List["Video"] = field(default_factory=list)
    filtered_videos: List["Video"] = field(default_factory=list)
    selected_video_id: Optional[int] = None
    search_query: str = ""
    sort_field: str = ""
    sort_direction: str = ""
    current_page: int = 0
    page_size: int = 0
    is_loading: bool = False
    detail_cache: Dict[int, "Video"] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.sort_field = self.settings.default_sort_field
        self.sort_direction = self.settings.default_sort_direction
        self.page_size = self.settings.page_size

    # --- Video collection management -------------------------------------------------

    def set_videos(self, videos: Iterable["Video"]) -> None:
        self.videos = list(videos)
        self._refresh_filtered(reset_page=True)

    def update_video(self, video: "Video") -> None:
        """Update or insert a video inside collections and cache."""

        self.detail_cache[video.id] = video
        updated = False
        for idx, existing in enumerate(self.videos):
            if existing.id == video.id:
                self.videos[idx] = video
                updated = True
                break
        if not updated:
            self.videos.append(video)
        self._refresh_filtered(reset_page=False)

    def remove_video(self, video_id: int) -> None:
        self.videos = [video for video in self.videos if video.id != video_id]
        self.detail_cache.pop(video_id, None)
        if self.selected_video_id == video_id:
            self.selected_video_id = None
        self._refresh_filtered(reset_page=False)

    # --- Filtering and sorting -------------------------------------------------------

    def update_search(self, query: str) -> None:
        self.search_query = query.strip()
        self._refresh_filtered(reset_page=True)

    def update_sort(self, field: str, direction: str) -> None:
        field = field or self.sort_field
        direction = direction.lower()
        if direction not in {"asc", "desc"}:
            direction = self.sort_direction
        self.sort_field = field
        self.sort_direction = direction
        self._refresh_filtered(reset_page=False)

    def set_page(self, page_index: int) -> None:
        if page_index < 0:
            page_index = 0
        if page_index >= self.total_pages:
            page_index = max(self.total_pages - 1, 0)
        self.current_page = page_index

    def set_page_size(self, size: int) -> None:
        if size <= 0:
            return
        self.page_size = min(size, self.settings.max_page_size)
        self._refresh_filtered(reset_page=True)

    def _refresh_filtered(self, reset_page: bool) -> None:
        videos: Iterable["Video"] = self.videos
        if self.search_query:
            lowered = self.search_query.lower()
            videos = [video for video in videos if video.matches_query(lowered)]
        videos = self._sort_videos(videos)
        self.filtered_videos = list(videos)
        if reset_page:
            self.current_page = 0
        else:
            self.current_page = min(self.current_page, max(self.total_pages - 1, 0))

    def _sort_videos(self, videos: Iterable["Video"]) -> Iterable["Video"]:
        reverse = self.sort_direction == "desc"

        key_map = {
            "upload_date": lambda video: video.upload_date or "",
            "title": lambda video: video.title.lower(),
            "channel": lambda video: video.channel.lower(),
        }
        sort_key = key_map.get(self.sort_field, key_map["upload_date"])
        return sorted(videos, key=sort_key, reverse=reverse)

    # --- Selection -------------------------------------------------------------------

    def select_video(self, video_id: Optional[int]) -> None:
        self.selected_video_id = video_id

    def cache_details(self, video: "Video") -> None:
        self.detail_cache[video.id] = video

    # --- Accessors -------------------------------------------------------------------

    def get_current_page_items(self) -> List["Video"]:
        start = self.current_page * self.page_size
        end = start + self.page_size
        return self.filtered_videos[start:end]

    @property
    def total_videos(self) -> int:
        return len(self.videos)

    @property
    def total_filtered(self) -> int:
        return len(self.filtered_videos)

    @property
    def total_pages(self) -> int:
        if not self.filtered_videos:
            return 1
        return math.ceil(len(self.filtered_videos) / self.page_size)

    @property
    def selected_video(self) -> Optional["Video"]:
        if self.selected_video_id is None:
            return None
        if self.selected_video_id in self.detail_cache:
            return self.detail_cache[self.selected_video_id]
        for video in self.videos:
            if video.id == self.selected_video_id:
                return video
        return None
