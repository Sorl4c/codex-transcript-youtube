import { App } from "./core/app.js";

const mountApplication = () => {
  const root = document.getElementById("app-root");
  if (!root) {
    console.error("No se encontró el nodo raíz para montar la aplicación.");
    return;
  }

  const app = new App(root);
  app.init();
};

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", mountApplication, {
    once: true,
  });
} else {
  mountApplication();
}
