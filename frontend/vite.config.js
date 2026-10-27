import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";
import { fileURLToPath } from "node:url";
import fs from "node:fs";
import path from "node:path";

const here = path.dirname(fileURLToPath(import.meta.url));
const staticDir = path.resolve(here, "../interui/static");

/** Elimina el stub JS que Vite genera junto al CSS compilado. */
function dropJsStub() {
  return {
    name: "interui-drop-js-stub",
    closeBundle() {
      const stub = path.join(staticDir, "interui-styles.js");
      if (fs.existsSync(stub)) fs.unlinkSync(stub);
    },
  };
}

export default defineConfig({
  plugins: [tailwindcss(), dropJsStub()],
  build: {
    // Compila directamente dentro del paquete Python para que el wheel
    // incluya el CSS ya generado y no necesite Node en tiempo de ejecución.
    outDir: staticDir,
    emptyOutDir: false,
    cssCodeSplit: false,
    sourcemap: false,
    reportCompressedSize: false,
    lib: {
      entry: path.resolve(here, "src/entry.js"),
      formats: ["es"],
      fileName: () => "interui-styles.js",
      cssFileName: "app",
    },
  },
  server: {
    port: 5180,
  },
});
