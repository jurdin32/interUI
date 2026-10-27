// Playground de estilos: solo importa el CSS para que Vite lo procese.
import "./styles.css";

document.documentElement.classList.toggle(
  "dark",
  window.matchMedia("(prefers-color-scheme: dark)").matches,
);
