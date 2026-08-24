/* Theme handling — three states, not two.
 *
 *   "light" / "dark"  stamp data-theme on <html> and win over the OS
 *   "system"          stamps nothing, so prefers-color-scheme decides
 *
 * The listener matters: someone on "system" whose OS flips at sunset should
 * see the page follow, without reloading.
 */
export const THEMES = ["light", "dark", "system"];
const KEY = "shruti-theme";

export function readTheme() {
  try {
    const stored = localStorage.getItem(KEY);
    return THEMES.includes(stored) ? stored : "system";
  } catch {
    // Private windows and blocked site data both throw here. Falling back to
    // "system" is correct: it is the state that needs no storage at all.
    return "system";
  }
}

export function applyTheme(theme) {
  const root = document.documentElement;
  if (theme === "system") root.removeAttribute("data-theme");
  else root.setAttribute("data-theme", theme);
}

export function setTheme(theme) {
  if (!THEMES.includes(theme)) return;
  try {
    localStorage.setItem(KEY, theme);
  } catch {
    /* Not persisting is survivable; not applying is not. */
  }
  applyTheme(theme);
}

export function watchSystemTheme() {
  const mq = window.matchMedia("(prefers-color-scheme: dark)");
  const onChange = () => {
    if (readTheme() === "system") applyTheme("system");
  };
  mq.addEventListener?.("change", onChange);
  return () => mq.removeEventListener?.("change", onChange);
}
