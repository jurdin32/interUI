# Documentación de interUI

interUI crea **aplicaciones de escritorio** en Python: la interfaz se escribe con
componentes, se renderiza como HTML dentro de una ventana nativa del sistema
operativo y los eventos vuelven a Python por un canal local. No hay navegador,
ni servidor que desplegar, ni conexión a internet.

Esta página es el mapa de la documentación. Si es tu primera vez, empieza por el
tutorial: en media hora tienes una app con formularios, tablas y una base de
datos real.

---

## Empieza aquí: el tutorial paso a paso

Si es tu primera vez, **no leas el resto todavía**. El tutorial va en orden, un
paso por archivo, y cada paso se ejecuta:

1. [Paso 1 · La ventana más pequeña posible](guia.md#paso-1-la-ventana-más-pequeña-posible) — una ventana vacía.
2. [Paso 2 · Añadir contenido](guia.md#paso-2-añadir-contenido-y-jerarquía) — texto y tarjetas.
3. [Paso 3 · Poner un menú](guia.md#paso-3-poner-un-menú) — Archivo, Ayuda y botones de ventana.
4. [Paso 4 · Botones y eventos](guia.md#paso-4-botones-y-eventos) — que un botón haga algo.
5. [Paso 5 · Estado reactivo](guia.md#paso-5-estado-reactivo) — que la ventana se actualice sola.
6. [Paso 6 · La rejilla](guia.md#paso-6-la-rejilla-de-12-columnas) — columnas.
7. [Paso 7 · Varias vistas](guia.md#paso-7-varias-vistas-y-navegación) — páginas.
8. [Paso 8 · Formularios](guia.md#paso-8-formularios-con-validación) — campos y validación.
9. [Paso 9 · Tabla y búsqueda](guia.md#paso-9-mostrar-datos-tabla-y-búsqueda) — listas.
10. [Paso 10 · Persistencia](guia.md#paso-10-persistencia-de-datos) — guardar entre sesiones.
11. [Paso 11 · Formulario desde un modelo](guia.md#paso-11-formulario-desde-un-modelo) — el formulario se genera solo.
12. [Paso 12 · De archivo a proyecto](guia.md#paso-12-de-archivo-suelto-a-proyecto) — la carpeta completa.

---

## Referencia rápida

| Documento | Qué aprendes |
|---|---|
| [Instalación](../README.md#instalación) | Instalar interUI y comprobar el entorno con `iui doctor`. |
| [Anatomía de un proyecto](proyecto.md) | Qué es `main.py`, qué es `iui.py`, dónde van los modelos y cómo encajan las apps. |

Camino mínimo, si tienes prisa:

```bash
pip install "interui[desktop]"
iui startproject mi_app        # sin nombre abre el asistente
cd mi_app
python main.py
```

---

## Temas (guías conceptuales)

Cada tema explica **cómo funciona** una parte del framework y por qué está hecha
así. Se leen en cualquier orden.

### La ventana y el escritorio

| Documento | Contenido |
|---|---|
| [Escritorio](escritorio.md) | Ciclo de vida, multiventana, ventanas sin marco, diálogos del sistema, datos persistentes, empaquetado. |
| [Menús y barras](menus.md) | `AppShell`, `MenuBar`, menús contextuales, barra de comandos, notificaciones. |
| [Diálogos](dialogos.md) | Modales no bloqueantes, confirmaciones, formularios, niveles de cierre. |

### La interfaz

| Documento | Contenido |
|---|---|
| [Rejilla de 12 columnas](rejilla.md) | Columnas, breakpoints, patrones de composición. |
| [Estilos](estilos.md) | Tokens (`colors.red_500`, `pad.py_6`), variantes (`hover_`, `md_`, `dark_`), clases propias. |
| [Iconos](iconos.md) | Los 204 iconos incluidos y cómo dibujarlos. |
| [Controles](controles.md) | Referencia de todos los componentes, con un ejemplo ejecutable por control. |

### Los datos

| Documento | Contenido |
|---|---|
| [Formularios](formularios.md) | `forms.py` en la app, `ui.ModelForm`, validación, `ui.state()` en las vistas. |
| [Datos](datos.md) | `interui.json`, modelos, consultas, migraciones, motores soportados, recetas. |
| [Configuración](configuracion.md) | Referencia completa de `interui.json`. |

---

## Referencia

| Documento | Contenido |
|---|---|
| [Comandos](comandos.md) | `iui`, `interui`, `iui.py` y `python -m interui`: todas las opciones. |
| [Configuración](configuracion.md) | Cada clave de `interui.json`, con su valor por defecto. |
| [Controles](controles.md) | Firma y ejemplos de cada componente. |
| [Formularios](formularios.md) | Un formulario por modelo, listo en tres líneas. |
| [Iconos](iconos.md) | Nombres disponibles. |

---

## Cómo se hace

| Documento | Contenido |
|---|---|
| [Empaquetar en un ejecutable](escritorio.md#6-empaquetado) | `iui build`: `.app` en macOS, `.exe` en Windows, binario en Linux. |
| [Actualizar interUI](actualizar.md) | Comprobar la versión, actualizar la instalación y el aviso dentro de la app. |
| [Publicar el paquete](publicar.md) | Construir el wheel, probarlo en TestPyPI y publicar en PyPI. |
| [Estilos con Tailwind](estilos.md#8-si-añades-tokens-nuevos) | Recompilar el CSS cuando añades clases nuevas (`iui assets`). |

---

## Convenciones de esta documentación

- Los bloques de código con `bash` son comandos de terminal; los de `python` se
  ejecutan dentro de tu app.
- `[interui] …` al principio de una línea es un mensaje del framework en la
  consola.
- Los nombres de componentes van en `PascalCase` (`Button`, `Table`) y los
  atajos de la API compacta en minúsculas (`button`, `table`): son el mismo
  control con menos ceremonia.
- «Ventana» siempre significa la ventana nativa del sistema operativo. El
  navegador solo aparece en el capítulo de depuración y nunca es el destino de
  una app publicada.
- Las rutas de archivos son ejemplos de un proyecto llamado `mi_app`; cámbialas
  por las tuyas.
