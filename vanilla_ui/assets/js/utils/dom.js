export const createElement = (tag, options = {}) => {
  const element = document.createElement(tag);
  if (options.classes) {
    element.className = Array.isArray(options.classes)
      ? options.classes.join(" ")
      : options.classes;
  }
  if (options.dataset) {
    Object.entries(options.dataset).forEach(([key, value]) => {
      element.dataset[key] = value;
    });
  }
  if (options.attrs) {
    Object.entries(options.attrs).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        element.setAttribute(key, value);
      }
    });
  }
  if (options.text) {
    element.textContent = options.text;
  }
  if (options.html) {
    element.innerHTML = options.html;
  }
  return element;
};

export const clearChildren = (node) => {
  if (!node) {
    return;
  }
  while (node.firstChild) {
    node.removeChild(node.firstChild);
  }
};

export const formatIcon = (pathDefinition) => {
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("viewBox", "0 0 24 24");
  svg.setAttribute("aria-hidden", "true");
  svg.setAttribute("focusable", "false");
  svg.innerHTML = `<path d="${pathDefinition}" />`;
  return svg;
};
