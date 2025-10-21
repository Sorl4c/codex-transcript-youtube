export class YouTubeService {
  constructor() {
    this.endpoint = "/api/youtube";
  }

  async fetchMetadata(urls = []) {
    console.warn(
      "YouTubeService.fetchMetadata aún no está conectado a ningún backend.",
    );
    return urls.map((url) => ({
      url,
      status: "pending",
    }));
  }
}
