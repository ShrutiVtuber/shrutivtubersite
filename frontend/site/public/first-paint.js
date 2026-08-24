/* Inlined in <head>, before any stylesheet, to stop the flash.
 *
 * A stored "dark" preference that is applied after first paint shows a white
 * page for a frame — small, ugly, and the thing people notice. This runs
 * synchronously so the attribute is on <html> before anything renders.
 *
 * Kept deliberately tiny and dependency-free; it is duplicated logic from
 * theme.js and that duplication is the point — it cannot wait for a module.
 */
(function () {
  try {
    var t = localStorage.getItem("shruti-theme");
    if (t === "light" || t === "dark") {
      document.documentElement.setAttribute("data-theme", t);
    }
  } catch (e) {
    /* No storage: fall through to prefers-color-scheme. */
  }
})();
