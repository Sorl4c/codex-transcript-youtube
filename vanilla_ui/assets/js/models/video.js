export class Video {
  constructor({
    id,
    title,
    channel,
    summary = "",
    transcript = "",
    published_at,
    duration = 0,
    tags = [],
    thumbnail_url = "",
  }) {
    this.id = id;
    this.title = title;
    this.channel = channel;
    this.summary = summary;
    this.transcript = transcript;
    this.published_at = published_at;
    this.duration = duration;
    this.tags = tags;
    this.thumbnail_url = thumbnail_url;
  }

  static fromJson(payload) {
    return new Video({
      id: payload.id,
      title: payload.title,
      channel: payload.channel,
      summary: payload.summary,
      transcript: payload.transcript,
      published_at: payload.published_at,
      duration: payload.duration ?? 0,
      tags: payload.tags ?? [],
      thumbnail_url: payload.thumbnail_url ?? "",
    });
  }
}
