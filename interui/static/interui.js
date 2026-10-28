// interui · runtime cliente
// Reconcilia el DOM con el HTML que envía Python y reenvía eventos por WebSocket.

const CONFIG = window.__INTERUI__ || {};
const state = {
  ws: null,
  queue: [],
  attempts: 0,
  page: CONFIG.page || "/",
  connected: false,
  pending: new Map(),
};

/* ------------------------------------------------------------------ */
/* socket                                                              */
/* ------------------------------------------------------------------ */
function socketUrl() {
  const proto = location.protocol === "https:" ? "wss:" : "ws:";
  // Cada ventana nativa abre su propio canal e incluye su id (?w=…).
  const win = new URLSearchParams(location.search).get("w");
  const suffix = win ? `?w=${encodeURIComponent(win)}` : "";
  return `${proto}//${location.host}/ws${suffix}`;
}

function connect() {
  const ws = new WebSocket(socketUrl());
  state.ws = ws;

  ws.addEventListener("open", () => {
    state.connected = true;
    state.attempts = 0;
    setStatus(false);
    send({ t: "hello", page: state.page });
    flush();
  });

  ws.addEventListener("message", (event) => {
    let message;
    try {
      message = JSON.parse(event.data);
    } catch {
      return;
    }
    handle(message);
  });

  ws.addEventListener("close", () => {
    state.connected = false;
    setStatus(true);
    retry();
  });

  ws.addEventListener("error", () => ws.close());
}

function retry() {
  state.attempts += 1;
  const delay = Math.min(4000, 250 * 2 ** Math.min(state.attempts, 4));
  setTimeout(connect, delay);
}

function send(payload) {
  if (state.ws && state.ws.readyState === WebSocket.OPEN) {
    state.ws.send(JSON.stringify(payload));
  } else {
    state.queue.push(payload);
  }
}

function flush() {
  const pending = state.queue.splice(0, state.queue.length);
  for (const payload of pending) send(payload);
}

function handle(message) {
  switch (message.t) {
    case "render":
      applyRender(message);
      break;
    case "toast":
      toast(message);
      break;
    case "eval":
      try {
        (0, eval)(message.js);
      } catch (error) {
        console.error("[interui] eval", error);
      }
      break;
    case "nav":
      navigate(message.path, { push: true });
      break;
    case "update":
      updateBanner(message);
      break;
    case "crash":
      renderCrash(message);
      break;
    default:
      break;
  }
}

function setStatus(visible) {
  const el = document.getElementById("iui-status");
  if (!el) return;
  el.classList.toggle("hidden", !visible);
  el.classList.toggle("flex", visible);
}

/* ------------------------------------------------------------------ */
/* reconciliación del DOM                                              */
/* ------------------------------------------------------------------ */
function applyRender(message) {
  const root = document.getElementById("iui-root");
  if (!root) return;
  const template = document.createElement("template");
  template.innerHTML = (message.html || "").trim();
  const next = template.content.firstElementChild;
  if (!next) return;

  patch(root, next);
  if (message.title) document.title = message.title;
  if (message.theme) applyTheme(message.theme);
  if (message.page) {
    state.page = message.page;
    root.dataset.iuiPage = message.page;
  }
  afterRender();
}

function patch(current, next) {
  if (current.nodeType !== next.nodeType) {
    current.replaceWith(next.cloneNode(true));
    return;
  }
  if (current.nodeType === Node.TEXT_NODE) {
    if (current.nodeValue !== next.nodeValue) current.nodeValue = next.nodeValue;
    return;
  }
  if (current.nodeType !== Node.ELEMENT_NODE) return;
  if (current.tagName !== next.tagName) {
    current.replaceWith(next.cloneNode(true));
    return;
  }
  syncAttributes(current, next);
  patchChildren(current, next);
  syncProperties(current, next);
}

function syncAttributes(current, next) {
  for (const attr of Array.from(current.attributes)) {
    if (!next.hasAttribute(attr.name)) current.removeAttribute(attr.name);
  }
  for (const attr of Array.from(next.attributes)) {
    if (current.getAttribute(attr.name) !== attr.value) {
      current.setAttribute(attr.name, attr.value);
    }
  }
}

function patchChildren(current, next) {
  const currentKids = Array.from(current.childNodes);
  const nextKids = Array.from(next.childNodes);
  const length = Math.max(currentKids.length, nextKids.length);
  for (let index = 0; index < length; index += 1) {
    const live = currentKids[index];
    const fresh = nextKids[index];
    if (!fresh) {
      if (live) live.remove();
      continue;
    }
    if (!live) {
      current.appendChild(fresh.cloneNode(true));
      continue;
    }
    patch(live, fresh);
  }
}

function syncProperties(current, next) {
  const tag = current.tagName;
  // Mientras el usuario escribe no se pisa el valor: su pulsación más reciente
  // siempre tiene prioridad sobre el HTML que llega del servidor.
  const editing = document.activeElement === current;
  if (tag === "INPUT") {
    const type = (current.getAttribute("type") || "text").toLowerCase();
    if (type === "checkbox" || type === "radio") {
      if (current.checked !== next.checked) current.checked = next.checked;
    } else if (type === "file") {
      /* el navegador controla el valor */
    } else if (!editing) {
      const desired = next.getAttribute("value") ?? "";
      if (current.value !== desired) current.value = desired;
    }
  } else if (tag === "TEXTAREA") {
    if (!editing) {
      const value = next.textContent ?? "";
      if (current.value !== value) current.value = value;
    }
  } else if (tag === "SELECT") {
    const desired = next.getAttribute("value");
    if (desired != null && current.value !== desired) current.value = desired;
    for (const option of current.options) {
      const template = Array.from(next.options).find((o) => o.value === option.value);
      const selected = template ? template.selected : false;
      if (option.selected !== selected) option.selected = selected;
    }
  } else if (tag === "PROGRESS" || tag === "METER") {
    current.value = next.value;
  }
}

/* ------------------------------------------------------------------ */
/* eventos                                                             */
/* ------------------------------------------------------------------ */
const DOM_EVENTS = {
  click: "click",
  dblclick: "dblclick",
  contextmenu: "contextmenu",
  change: "change",
  input: "input",
  submit: "submit",
  keydown: "keydown",
  keyup: "keyup",
  focusin: "focus",
  focusout: "blur",
  dragstart: "dragstart",
  dragover: "dragover",
  drop: "drop",
  select: "select",
};

function closestEmit(target) {
  let node = target instanceof Element ? target : null;
  while (node && node !== document.documentElement) {
    if (node.dataset && node.dataset.iuiEmit) return node;
    node = node.parentElement;
  }
  return null;
}

function declaredEvents(element) {
  const raw = element.dataset ? element.dataset.iuiOn : null;
  return raw ? raw.split(",") : [];
}

function closestByEvent(target, name) {
  let node = target instanceof Element ? target : null;
  while (node && node !== document.documentElement) {
    if (declaredEvents(node).includes(name)) return node;
    node = node.parentElement;
  }
  return null;
}

function readValue(element) {
  const tag = element.tagName;
  const type = (element.type || "").toLowerCase();
  if (type === "checkbox") return element.checked ? element.value || "on" : null;
  if (type === "radio") return element.value;
  if (tag === "SELECT" && element.multiple) {
    return Array.from(element.selectedOptions).map((option) => option.value);
  }
  if (type === "number" || type === "range") {
    const number = Number(element.value);
    return Number.isNaN(number) ? element.value : number;
  }
  if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return element.value;
  return element.dataset ? element.dataset.value ?? null : null;
}

function eventPayload(element, name, extra = {}) {
  const tag = element.tagName;
  const type = (element.type || "").toLowerCase();
  const payload = {
    t: "event",
    id: element.id,
    e: name,
    v: extra.v !== undefined ? extra.v : readValue(element),
    target: element.tagName.toLowerCase(),
    data: {
      name: element.name || "",
      index: element.dataset ? element.dataset.iuiIndex : undefined,
      ...(extra.data || {}),
    },
  };
  if (type === "checkbox") payload.checked = element.checked;
  if (extra.key) payload.key = extra.key;
  if (extra.mods) payload.mods = extra.mods;
  if (extra.files) payload.files = extra.files;
  if (tag === "FORM") payload.data.form = formValues(element);
  return payload;
}

function formValues(form) {
  const out = {};
  for (const [key, value] of new FormData(form).entries()) {
    if (out[key] !== undefined) {
      out[key] = [].concat(out[key], value instanceof File ? value.name : value);
    } else {
      out[key] = value instanceof File ? value.name : value;
    }
  }
  return out;
}

function dispatchEvent(element, name, extra = {}) {
  if (extra.confirm) {
    if (!window.confirm(extra.confirm)) return false;
  }
  send(eventPayload(element, name, extra));
  return true;
}

function debounced(element, name, delay = 200) {
  const key = `${element.id}:${name}`;
  clearTimeout(state.pending.get(key));
  state.pending.set(
    key,
    setTimeout(() => {
      state.pending.delete(key);
      dispatchEvent(element, name);
    }, delay),
  );
}

function onDelegated(domType, event) {
  const name = DOM_EVENTS[domType];
  if (!name) return;

  let node = event.target instanceof Element ? event.target : null;

  if (name === "click") {
    const emitter = closestEmit(event.target);
    if (emitter) {
      const raw = emitter.dataset.iuiValue !== undefined ? emitter.dataset.iuiValue : "";
      const value = emitter.dataset.iuiCast === "int" ? Number(raw) : raw;
      dispatchEvent(emitter, emitter.dataset.iuiEmit, { v: value });
      return;
    }
  }

  // comportamientos locales (modales, copiar, pestañas, navegación…)
  const chain = [];
  while (node && node !== document.documentElement) {
    chain.push(node);
    node = node.parentElement;
  }
  for (const element of chain) {
    runBehaviors(element, domType, event);
  }

  const target = closestByEvent(
    event.target instanceof Element ? event.target : null,
    name,
  );
  if (!target) return;

  if (name === "submit") event.preventDefault();

  if (name === "keydown" || name === "keyup") {
    const mods = {
      alt: event.altKey,
      ctrl: event.ctrlKey,
      meta: event.metaKey,
      shift: event.shiftKey,
    };
    if (name === "keydown") {
      const enterTarget = closestByEvent(event.target, "enter");
      if (event.key === "Enter" && enterTarget) {
        dispatchEvent(enterTarget, "enter", { v: readValue(enterTarget) });
      }
      const escapeTarget = closestByEvent(event.target, "escape");
      if (event.key === "Escape" && escapeTarget) {
        dispatchEvent(escapeTarget, "escape");
      }
    }
    dispatchEvent(target, name, { key: event.key, mods });
    return;
  }

  if (name === "input") {
    const live = ["range", "color", "search"].includes((target.type || "").toLowerCase());
    if (live) {
      dispatchEvent(target, name);
    } else {
      debounced(target, name, Number(target.dataset.iuiDebounce || 220));
    }
    return;
  }

  if (name === "change" && (target.type || "").toLowerCase() === "file") {
    return;
  }

  if (name === "dragover" || name === "dragstart") {
    if (target.dataset.iuiDropzone !== undefined) event.preventDefault();
    return;
  }

  if (name === "drop") {
    if (target.dataset.iuiDropzone !== undefined) {
      event.preventDefault();
      uploadFiles(target.dataset.iuiDropzone, event.dataTransfer.files);
      return;
    }
  }

  if (name === "select" || name === "blur" || name === "focus") {
    dispatchEvent(target, name);
    return;
  }

  dispatchEvent(target, name, { confirm: target.dataset.iuiConfirm });
}

for (const domType of Object.keys(DOM_EVENTS)) {
  const options = domType === "focusin" || domType === "focusout" ? true : false;
  document.addEventListener(domType, (event) => onDelegated(domType, event), options);
}

document.addEventListener("mouseover", (event) => {
  const target = closestByEvent(event.target, "mouseenter");
  if (target && !target.contains(event.relatedTarget)) dispatchEvent(target, "mouseenter");
});
document.addEventListener("mouseout", (event) => {
  const target = closestByEvent(event.target, "mouseleave");
  if (target && !target.contains(event.relatedTarget)) dispatchEvent(target, "mouseleave");
});

/* ------------------------------------------------------------------ */
/* comportamientos                                                     */
/* ------------------------------------------------------------------ */
function runBehaviors(element, domType, event) {
  if (element.nodeType !== 1) return;
  const dataset = element.dataset || {};

  if (domType === "click") {
    if (dataset.iuiModal) openDialog(dataset.iuiModal);
    if (dataset.iuiToggle) toggleTarget(dataset.iuiToggle, element);
    if (dataset.iuiDrawer) toggleDrawer(element, dataset.iuiDrawer);
    if (dataset.iuiClose !== undefined) closeDialog(dataset.iuiClose);
    if (dataset.iuiTab) activateTab(dataset.iuiTab, element);
    if (dataset.iuiCollapse) toggleCollapse(dataset.iuiCollapse);
    if (dataset.iuiCopy !== undefined) copyText(dataset.iuiCopy);
    if (dataset.iuiDismiss !== undefined) dismiss(element);
    if (dataset.iuiScrollTo) scrollToId(dataset.iuiScrollTo);
    if (dataset.iuiTheme) applyTheme(dataset.iuiTheme);
    if (dataset.iuiLink) {
      event.preventDefault();
      navigate(dataset.iuiLink, { push: true });
    }
    if (dataset.iuiSort !== undefined) dispatchEvent(element, "sort", { v: dataset.iuiSort });
    if (dataset.iuiPage !== undefined) dispatchEvent(element, "page", { v: Number(dataset.iuiPage) });
    if (dataset.iuiRemove !== undefined) dispatchEvent(element, "remove", { v: dataset.iuiRemove });
    if (dataset.iuiAdd !== undefined) dispatchEvent(element, "add", { v: dataset.iuiAdd });
    if (dataset.iuiToggleValue !== undefined) {
      dispatchEvent(element, "toggle", { v: dataset.iuiToggleValue });
    }
    if (dataset.iuiNative) {
      nativeControl(dataset.iuiNative);
    }
    if (dataset.iuiExternal) {
      externalControl(dataset.iuiExternal);
    }
    if (dataset.iuiDownload) {
      const [name, ...rest] = dataset.iuiDownload.split("|");
      download(name || "datos.txt", rest.join("|"));
    }
    if (dataset.iuiReveal) {
      const input = document.getElementById(dataset.iuiReveal);
      if (input) input.type = input.type === "password" ? "text" : "password";
    }
    if (dataset.iuiCommand !== undefined) {
      /* el clic cierra la paleta */
      document.querySelectorAll("[data-iui-palette]").forEach((palette) => {
        if (palette.contains(element)) palette.classList.add("hidden");
      });
    }
  }

  if (domType === "input" || domType === "change") {
    if (dataset.iuiSync) syncInputs(element, dataset.iuiSync);
    if (dataset.iuiCommand !== undefined) filterCommand(element, dataset.iuiCommand);
    if (domType === "input" && dataset.iuiOtpNext && element.value) {
      const next = document.getElementById(dataset.iuiOtpNext);
      if (next) next.focus({ preventScroll: true });
    }
  }

  if (domType === "change") {
    if (element.tagName === "INPUT" && element.type === "file") {
      uploadFiles(element.id, element.files);
    }
  }

  if (domType === "keydown") {
    if (dataset.iuiCommand !== undefined && event.key === "Escape") {
      const palette = element.closest("[data-iui-palette]");
      if (palette) palette.classList.add("hidden");
    }
  }

  if (domType === "dragover" && dataset.iuiDropzone !== undefined) {
    element.classList.add("ring-2", "ring-indigo-500");
    event.preventDefault();
  }
  if ((domType === "dragleave" || domType === "drop") && dataset.iuiDropzone !== undefined) {
    element.classList.remove("ring-2", "ring-indigo-500");
  }
}

function dialogs() {
  return document.querySelectorAll("[data-iui-dialog]");
}

function openDialog(id) {
  const element = id ? document.getElementById(id) : null;
  if (!element) return;
  element.classList.remove("hidden");
  element.classList.add("flex");
  element.setAttribute("data-iui-open", "true");
  const focusable = element.querySelector("[autofocus], input, textarea, select, button");
  if (focusable) focusable.focus({ preventScroll: true });
}

function closeDialog(id) {
  const targets = id
    ? [document.getElementById(id)].filter(Boolean)
    : Array.from(document.querySelectorAll("[data-iui-open='true']"));
  for (const element of targets) {
    element.classList.add("hidden");
    element.classList.remove("flex");
    element.removeAttribute("data-iui-open");
  }
}

function toggleTarget(id) {
  const element = document.getElementById(id);
  if (!element) return;
  element.classList.toggle("hidden");
}

/* Sidebar de AppShell en ventanas estrechas: el estado se guarda aquí porque
   cada render reconstruye el HTML y perdería los atributos puestos a mano. */
const drawerState = new Map();

function toggleDrawer(element, mode) {
  const shell = element.closest ? element.closest(".iui-shell") : null;
  if (!shell) return;
  const open = mode === "close" ? false : !drawerState.get(shell.id);
  drawerState.set(shell.id, open);
  applyDrawerState();
}

function applyDrawerState() {
  document.querySelectorAll(".iui-shell").forEach((shell) => {
    shell.dataset.sidebar = drawerState.get(shell.id) ? "open" : "closed";
  });
}

/* Al elegir algo del menú lateral, el panel se cierra solo. */
document.addEventListener("click", (event) => {
  const target = event.target;
  if (!target || !target.closest) return;
  const shell = target.closest(".iui-shell");
  if (!shell || !drawerState.get(shell.id)) return;
  if (target.closest(".iui-shell-side, .iui-shell-row > aside")) {
    drawerState.set(shell.id, false);
    applyDrawerState();
  }
});

function toggleCollapse(id) {
  const element = document.getElementById(id);
  if (!element) return;
  const open = element.dataset.open === "true";
  element.dataset.open = String(!open);
  element.classList.toggle("hidden", open);
}

function activateTab(id, trigger) {
  const panel = document.getElementById(id);
  if (!panel) return;
  const group = panel.closest("[data-iui-tabgroup]") || panel.parentElement;
  if (!group) return;
  group.querySelectorAll("[data-iui-panel]").forEach((node) => node.classList.add("hidden"));
  panel.classList.remove("hidden");
  const bar = trigger.closest("[data-iui-tabbar]");
  if (bar) {
    bar.querySelectorAll("[data-iui-tab]").forEach((node) => {
      node.classList.remove("border-indigo-600", "text-indigo-600", "dark:text-indigo-400");
      node.classList.add("border-transparent", "text-slate-500");
    });
  }
  trigger.classList.remove("border-transparent", "text-slate-500");
  trigger.classList.add("border-indigo-600", "text-indigo-600", "dark:text-indigo-400");
}

async function copyText(text) {
  const api = bridge();
  if (api && typeof api.clipboard_write === "function") {
    const ok = await api.clipboard_write(text || "");
    if (ok) {
      toast("Copiado al portapapeles", "success");
      return;
    }
  }
  try {
    await navigator.clipboard.writeText(text || "");
    toast("Copiado al portapapeles", "success");
  } catch {
    toast("No se pudo copiar", "error");
  }
}

function dismiss(element) {
  const snackbar = element.closest("[data-iui-snackbar]");
  const target = snackbar || element.closest("[data-iui-dismissible]") || element;
  target.remove();
}

document.addEventListener("click", (event) => {
  const button = event.target.closest && event.target.closest("[data-iui-dismiss]");
  if (!button) return;
  event.preventDefault();
  dismiss(button);
});

function scrollToId(id) {
  const element = document.getElementById(id);
  if (element) element.scrollIntoView({ behavior: "smooth", block: "start" });
}

function applyTheme(mode) {
  const resolved =
    mode === "system"
      ? window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light"
      : mode;
  const root = document.documentElement;
  root.classList.remove("light", "dark");
  root.classList.add(resolved);
  root.dataset.theme = resolved;
}

function syncInputs(source, targetId) {
  const target = document.getElementById(targetId);
  if (target && target.value !== source.value) target.value = source.value;
}

function filterCommand(input, listId) {
  const list = document.getElementById(listId);
  if (!list) return;
  const term = input.value.trim().toLowerCase();
  let visible = 0;
  for (const item of list.querySelectorAll("[data-iui-item]")) {
    const match = !term || (item.textContent || "").toLowerCase().includes(term);
    item.classList.toggle("hidden", !match);
    if (match) visible += 1;
  }
  const empty = list.querySelector("[data-iui-empty]");
  if (empty) empty.classList.toggle("hidden", visible > 0);
}

/* ------------------------------------------------------------------ */
/* menús (barra de menús, desplegables y menú contextual)               */
/* ------------------------------------------------------------------ */
function closestData(target, key) {
  let node = target instanceof Element ? target : null;
  while (node && node !== document.documentElement) {
    if (node.dataset && node.dataset[key] !== undefined) return node;
    node = node.parentElement;
  }
  return null;
}

function menuPanels() {
  return document.querySelectorAll("[data-iui-menu-panel], [data-iui-context-panel]");
}

function closeMenus(except) {
  for (const panel of menuPanels()) {
    if (panel === except) continue;
    panel.classList.add("hidden");
    panel.classList.remove("flex");
    const owner = panel.id;
    document
      .querySelectorAll(`[data-iui-menu="${owner}"], [data-iui-toggle="${owner}"]`)
      .forEach((trigger) => trigger.setAttribute("aria-expanded", "false"));
  }
}

function openMenu(panelId, trigger) {
  const panel = document.getElementById(panelId);
  if (!panel) return;
  closeMenus(panel);
  panel.classList.remove("hidden");
  panel.classList.add("flex");
  if (trigger) trigger.setAttribute("aria-expanded", "true");
}

function toggleMenu(panelId, trigger) {
  const panel = document.getElementById(panelId);
  if (!panel) return;
  if (panel.classList.contains("hidden")) openMenu(panelId, trigger);
  else closeMenus();
}

function openContextMenu(panelId, x, y) {
  const panel = document.getElementById(panelId);
  if (!panel) return;
  closeMenus(panel);
  panel.classList.remove("hidden");
  panel.classList.add("flex");
  panel.style.left = "0px";
  panel.style.top = "0px";
  const rect = panel.getBoundingClientRect();
  const left = Math.min(x, window.innerWidth - rect.width - 8);
  const top = Math.min(y, window.innerHeight - rect.height - 8);
  panel.style.left = `${Math.max(8, left)}px`;
  panel.style.top = `${Math.max(8, top)}px`;
}

document.addEventListener("contextmenu", (event) => {
  const host = closestData(event.target, "iuiContext");
  if (!host) return;
  event.preventDefault();
  openContextMenu(host.dataset.iuiContext, event.clientX, event.clientY);
});

document.addEventListener("click", (event) => {
  const trigger = closestData(event.target, "iuiMenu");
  const toggle = closestData(event.target, "iuiToggle");
  if (trigger) {
    event.stopPropagation();
    toggleMenu(trigger.dataset.iuiMenu, trigger);
    return;
  }
  const menuItem = closestData(event.target, "iuiMenuItem");
  if (menuItem) closeMenus();
  else if (!event.target.closest || !event.target.closest("[data-iui-menu-panel], [data-iui-context-panel]")) {
    closeMenus();
  }
}, true);

document.addEventListener("mouseover", (event) => {
  // Con un menú abierto, pasar por otro elemento de la barra cambia de menú.
  const bar = event.target.closest && event.target.closest('[role="menubar"]');
  if (!bar) return;
  const anyOpen = [...menuPanels()].some((panel) => !panel.classList.contains("hidden"));
  if (!anyOpen) return;
  const trigger = closestData(event.target, "iuiMenu");
  if (trigger) openMenu(trigger.dataset.iuiMenu, trigger);
});

/* ------------------------------------------------------------------ */
/* navegación interna                                                  */
/* ------------------------------------------------------------------ */
function navigate(path, options = {}) {
  if (!path) return;
  state.page = path;
  if (options.push && location.pathname !== path) history.pushState({ path }, "", path);
  send({ t: "nav", path });
}

window.addEventListener("popstate", (event) => {
  const path = (event.state && event.state.path) || location.pathname;
  navigate(path, { push: false });
});

document.addEventListener("click", (event) => {
  const anchor = event.target.closest && event.target.closest("a[href]");
  if (!anchor) return;
  const href = anchor.getAttribute("href") || "";
  if (href.startsWith("http://") || href.startsWith("https://") || href.startsWith("mailto:")) {
    if (isDesktop() && !anchor.hasAttribute("download")) {
      event.preventDefault();
      externalControl(href);
    }
    return;
  }
  if (!href.startsWith("/") || href.startsWith("//")) return;
  if (anchor.target && anchor.target !== "_self") return;
  if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
  if (anchor.hasAttribute("download")) return;
  event.preventDefault();
  navigate(href, { push: true });
});

/* ------------------------------------------------------------------ */
/* subidas de ficheros                                                 */
/* ------------------------------------------------------------------ */
async function uploadFiles(targetId, fileList) {
  const files = Array.from(fileList || []);
  if (!files.length) return;
  const host = targetId ? document.getElementById(targetId) : null;
  const source = host || document.querySelector("[data-iui-upload]");
  const uploaded = [];
  for (const file of files) {
    try {
      const response = await fetch("/api/upload", {
        method: "POST",
        headers: {
          "X-File-Name": encodeURIComponent(file.name),
          "X-File-Type": file.type || "application/octet-stream",
        },
        body: file,
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      uploaded.push(await response.json());
    } catch (error) {
      console.error("[interui] subida fallida", error);
      toast(`No se pudo subir ${file.name}`, "error");
    }
  }
  if (source) {
    send({
      t: "event",
      id: source.id,
      e: "change",
      v: files.map((file) => file.name),
      files: uploaded,
      data: { name: source.name || "" },
    });
  }
  document.querySelectorAll("[data-iui-upload]").forEach((input) => {
    if (input !== source) input.value = "";
  });
}

/* ------------------------------------------------------------------ */
/* toasts                                                              */
/* ------------------------------------------------------------------ */
const TOAST_STYLES = {
  info: "bg-slate-900 text-white ring-slate-700",
  success: "bg-emerald-600 text-white ring-emerald-500",
  warning: "bg-amber-500 text-slate-950 ring-amber-400",
  error: "bg-rose-600 text-white ring-rose-500",
};

function toast(payload, level = "info") {
  const data = typeof payload === "string" ? { message: payload, level } : payload || {};
  const host = document.getElementById("iui-toasts");
  if (!host) return;
  const tone = data.level || "info";
  const wrapper = document.createElement("div");
  wrapper.className =
    "pointer-events-auto flex items-start gap-3 rounded-xl px-4 py-3 text-sm shadow-lg ring-1 " +
    (TOAST_STYLES[tone] || TOAST_STYLES.info) +
    " translate-y-2 opacity-0 transition duration-200";
  wrapper.setAttribute("role", "status");
  wrapper.dataset.iuiSnackbar = "true";

  if (data.image) {
    const image = document.createElement("img");
    image.src = data.image;
    image.alt = "";
    image.className = "h-9 w-9 shrink-0 rounded-lg object-cover";
    wrapper.appendChild(image);
  } else if (data.icon) {
    // El marcado SVG llega ya dimensionado desde Python.
    const icon = document.createElement("span");
    icon.className = "shrink-0";
    icon.innerHTML = data.icon;
    wrapper.appendChild(icon);
  }

  const body = document.createElement("div");
  body.className = "flex min-w-0 flex-1 flex-col gap-0.5";
  if (data.title) {
    const title = document.createElement("p");
    title.className = "truncate font-semibold leading-snug";
    title.textContent = data.title;
    body.appendChild(title);
  }
  const text = document.createElement("span");
  text.className = "leading-snug" + (data.title ? " opacity-90" : "");
  text.textContent = data.message || "";
  body.appendChild(text);
  wrapper.appendChild(body);

  if (data.action && data.action.label) {
    const action = document.createElement("button");
    action.type = "button";
    action.textContent = data.action.label;
    action.className =
      "shrink-0 rounded-md px-1 py-0.5 text-xs font-semibold underline-offset-2 hover:underline";
    action.addEventListener("click", () => {
      if (data.action.js) {
        try {
          new Function(data.action.js)();
        } catch (error) {
          console.error(error);
        }
      }
      wrapper.remove();
    });
    wrapper.appendChild(action);
  }

  const close = document.createElement("button");
  close.type = "button";
  close.className = "shrink-0 rounded-md p-0.5 opacity-70 transition hover:opacity-100";
  close.textContent = "✕";
  close.setAttribute("aria-label", "Cerrar aviso");
  close.addEventListener("click", () => wrapper.remove());
  wrapper.appendChild(close);

  host.appendChild(wrapper);
  requestAnimationFrame(() => {
    wrapper.classList.remove("translate-y-2", "opacity-0");
    wrapper.classList.add("translate-y-0", "opacity-100");
  });
  const ms = Number(data.duration ?? 4200);
  if (ms > 0) {
    setTimeout(() => {
      wrapper.classList.add("opacity-0", "translate-y-2");
      setTimeout(() => wrapper.remove(), 250);
    }, ms);
  }
}

/* ------------------------------------------------------------------ */
/* aviso de versión nueva                                              */
/* ------------------------------------------------------------------ */
const UPDATE_KEY = "iui-update-dismissed";

function updateBanner(message) {
  const version = message.latest || "";
  if (!version) return;
  if (localStorage.getItem(UPDATE_KEY) === version) return;
  const existing = document.getElementById("iui-update");
  if (existing) existing.remove();

  const box = document.createElement("div");
  box.id = "iui-update";
  box.setAttribute("role", "status");
  box.className =
    "fixed bottom-4 left-1/2 z-[90] w-[min(680px,calc(100vw-2rem))] -translate-x-1/2 " +
    "rounded-xl border border-indigo-200 bg-white p-4 shadow-2xl " +
    "dark:border-indigo-500/40 dark:bg-slate-900";

  const title = document.createElement("p");
  title.className = "text-sm font-semibold text-slate-900 dark:text-white";
  title.textContent = `interUI ${version} ya está disponible`;
  title.dataset.iuiUpdateTitle = "true";

  const detail = document.createElement("p");
  detail.className = "mt-1 text-xs text-slate-500 dark:text-slate-400";
  detail.textContent = `Tienes la ${message.current || ""}. Actualiza con este comando:`;

  const code = document.createElement("code");
  code.className =
    "mt-2 block overflow-x-auto rounded-lg bg-slate-100 px-3 py-2 " +
    "font-mono text-[11px] text-slate-800 dark:bg-slate-800 dark:text-slate-100";
  code.textContent = message.command || "";

  const actions = document.createElement("div");
  actions.className = "mt-3 flex flex-wrap items-center gap-2";

  const copy = document.createElement("button");
  copy.type = "button";
  copy.className =
    "rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-medium text-white transition hover:bg-indigo-500";
  copy.textContent = "Copiar comando";
  copy.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(code.textContent || "");
      copy.textContent = "¡Copiado!";
      setTimeout(() => (copy.textContent = "Copiar comando"), 1600);
    } catch (error) {
      const range = document.createRange();
      range.selectNodeContents(code);
      const selection = window.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
    }
  });

  const link = document.createElement("a");
  link.href = message.url || "https://github.com/jurdin32/interUI";
  link.dataset.iuiExternal = link.href;
  link.className =
    "rounded-lg px-3 py-1.5 text-xs font-medium text-indigo-600 transition hover:bg-indigo-50 " +
    "dark:text-indigo-400 dark:hover:bg-slate-800";
  link.textContent = "Cómo actualizar";

  const later = document.createElement("button");
  later.type = "button";
  later.className =
    "ml-auto rounded-lg px-3 py-1.5 text-xs font-medium text-slate-500 transition " +
    "hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800";
  later.textContent = "Ahora no";
  later.addEventListener("click", () => {
    localStorage.setItem(UPDATE_KEY, version);
    box.remove();
  });

  actions.append(copy, link, later);
  box.append(title, detail, code, actions);
  document.body.appendChild(box);
}

/* ------------------------------------------------------------------ */
/* errores de render                                                   */
/* ------------------------------------------------------------------ */
function renderCrash(message) {
  const root = document.getElementById("iui-root");
  if (!root) return;
  root.innerHTML = `
    <div class="mx-auto max-w-3xl p-8">
      <div class="rounded-2xl border border-rose-300 bg-rose-50 p-6 dark:border-rose-800 dark:bg-rose-950/40">
        <h2 class="text-lg font-semibold text-rose-700 dark:text-rose-300">Error al renderizar</h2>
        <p class="mt-2 font-mono text-sm text-rose-900 dark:text-rose-200">${escapeHtml(message.message)}</p>
        <pre class="mt-4 max-h-72 overflow-auto rounded-lg bg-slate-950 p-4 text-xs text-slate-200">${escapeHtml(
          message.detail || "",
        )}</pre>
      </div>
    </div>`;
}

function escapeHtml(text) {
  return String(text).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  })[char]);
}

/* ------------------------------------------------------------------ */
/* arranque                                                            */
/* ------------------------------------------------------------------ */
function afterRender() {
  closeMenus();
  applyDrawerState();
  applyTheme(document.documentElement.dataset.theme || CONFIG.theme || "light");
  document.querySelectorAll("[data-iui-autofocus]").forEach((element) => {
    if (document.activeElement === document.body) element.focus({ preventScroll: true });
  });
  document.querySelectorAll("[data-iui-indeterminate]").forEach((element) => {
    element.indeterminate = true;
  });
  document.querySelectorAll("[data-iui-snackbar][data-iui-duration]").forEach((element) => {
    if (element.dataset.iuiArmed) return;
    element.dataset.iuiArmed = "1";
    const ms = parseInt(element.dataset.iuiDuration || "0", 10);
    if (ms > 0) {
      setTimeout(() => {
        element.classList.add("opacity-0");
        setTimeout(() => element.remove(), 250);
      }, ms);
    }
  });
}

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    closeMenus();
    closeDialog();
  }
});

/* ------------------------------------------------------------------ */
/* escritorio (pywebview)                                              */
/* ------------------------------------------------------------------ */
function bridge() {
  return window.pywebview && window.pywebview.api ? window.pywebview.api : null;
}

function isDesktop() {
  return Boolean(bridge());
}

async function callNative(method, ...args) {
  const api = bridge();
  if (!api || typeof api[method] !== "function") return null;
  try {
    return await api[method](...args);
  } catch (error) {
    console.error("[interui] native " + method, error);
    return null;
  }
}

async function nativeControl(action) {
  switch (action) {
    case "minimize":
      await callNative("minimize");
      break;
    case "maximize":
      await callNative("toggle_maximize");
      break;
    case "fullscreen":
      await callNative("toggle_fullscreen");
      break;
    case "close":
      await callNative("close");
      break;
    case "top":
      await callNative("set_always_on_top", true);
      break;
    default:
      break;
  }
}

function externalControl(url) {
  if (!url) return;
  if (isDesktop()) callNative("open_external", url);
  else window.open(url, "_blank", "noopener");
}

function download(name, text) {
  if (isDesktop()) {
    callNative("save_file", name, String(text ?? ""));
    return;
  }
  const blob = new Blob([text ?? ""], { type: "text/plain;charset=utf-8" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = name || "datos.txt";
  link.click();
  URL.revokeObjectURL(link.href);
}

window.interui = {
  toast,
  send,
  navigate,
  openDialog,
  closeDialog,
  copy: copyText,
  upload: uploadFiles,
  download,
  closeMenus,
  openMenu,
  toggleMenu,
  updateBanner,
  get page() {
    return state.page;
  },
  get desktop() {
    return isDesktop();
  },
  native: {
    get available() {
      return isDesktop();
    },
    async openFile(multiple = false) {
      return callNative("open_file", multiple);
    },
    async pickFolder() {
      return callNative("pick_folder");
    },
    async save(name, text) {
      return callNative("save_file", name, String(text ?? ""));
    },
    async notify(title, message = "") {
      return callNative("notify", title, message);
    },
    async setTitle(title) {
      return callNative("set_title", title);
    },
    minimize: () => callNative("minimize"),
    toggleMaximize: () => callNative("toggle_maximize"),
    fullscreen: () => callNative("toggle_fullscreen"),
    close: () => callNative("close"),
    openExternal: (url) => externalControl(url),
    async clipboard(text) {
      if (isDesktop()) return callNative("clipboard_write", text);
      return copyText(text);
    },
    info: () => callNative("info"),
  },
};

if (window.pywebview) {
  window.pywebview.addEventListener("pywebviewready", () => {
    document.documentElement.dataset.desktop = "true";
  });
}

connect();
afterRender();
