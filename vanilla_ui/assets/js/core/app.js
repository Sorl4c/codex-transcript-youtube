import { State } from "./state.js";
import { Router } from "./router.js";
import { DatabaseService } from "../services/databaseService.js";
import { LibraryPage } from "../pages/LibraryPage.js";
import { Header } from "../components/Header.js";
import { Sidebar } from "../components/Sidebar.js";

export class App {
  constructor(root) {
    this.root = root;
    this.state = new State();
    this.databaseService = new DatabaseService("data/sample_videos.json");
    this.router = new Router();
    this.pageInstances = new Map();
    this.shell = null;
    this.routeOutlet = null;
  }

  async init() {
    this.renderShell();
    await this.bootstrapData();
    this.configureRoutes();
    this.router.navigate("library");
  }

  renderShell() {
    this.root.innerHTML = "";

    const shell = document.createElement("div");
    shell.className = "app-shell";

    const headerEl = document.createElement("header");
    headerEl.className = "app-header";

    const header = new Header({
      onToggleTheme: this.toggleTheme.bind(this),
    });
    headerEl.appendChild(header.render());

    const body = document.createElement("div");
    body.className = "app-body";

    const sidebarEl = document.createElement("aside");
    sidebarEl.className = "app-sidebar";
    const sidebar = new Sidebar({
      state: this.state,
      onNavigate: (route) => this.router.navigate(route),
    });
    sidebarEl.appendChild(sidebar.render());

    const main = document.createElement("main");
    main.className = "app-main";
    this.routeOutlet = main;

    body.append(sidebarEl, main);
    shell.append(headerEl, body);
    this.shell = shell;
    this.root.appendChild(shell);
  }

  async bootstrapData() {
    try {
      const videos = await this.databaseService.getAllVideos();
      this.state.setVideos(videos);
    } catch (error) {
      console.error("Error al inicializar datos:", error);
      this.state.setError("No se pudieron cargar los videos iniciales.");
    }
  }

  configureRoutes() {
    const libraryPage = new LibraryPage({
      state: this.state,
      services: {
        database: this.databaseService,
      },
    });

    this.pageInstances.set("library", libraryPage);

    this.router.register("library", () => {
      this.mountPage("library");
    });
  }

  mountPage(routeName) {
    if (!this.routeOutlet) {
      return;
    }

    this.routeOutlet.replaceChildren();
    this.pageInstances.forEach((page, name) => {
      if (name !== routeName) {
        page.unmount?.();
      }
    });

    const page = this.pageInstances.get(routeName);
    if (page) {
      page.mount(this.routeOutlet);
    } else {
      this.routeOutlet.textContent = "Vista no disponible.";
    }
  }

  toggleTheme() {
    const current = this.root.dataset.theme ?? "light";
    const next = current === "light" ? "dark" : "light";
    this.root.dataset.theme = next;
  }
}
