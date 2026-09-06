/* Configuration, read where it can actually be read.
 *
 * **`import.meta.env` is substituted at BUILD time.** Astro compiles those
 * reads into literals when the bundle is made, which for a container image
 * happens before it is ever deployed and long before anybody sets a variable
 * on it. A value supplied to the running container is then not ignored with an
 * error — it is ignored silently, and the fallback that was compiled in takes
 * its place. The site keeps working, on the wrong value, looking right.
 *
 * That is not hypothetical here. `SHRUTI_SOURCE_SHA` was read that way and the
 * licence link fell back to the repository while the container had the exact
 * commit in its environment the whole time.
 *
 * So: `process.env` first, which is the running process, with `import.meta.env`
 * behind it for anything genuinely fixed at build. One function, and it is the
 * only place in the site allowed to touch either — a test enforces that,
 * because the failure is invisible and the habit is easy.
 */

function read(name: string): string {
  const runtime =
    typeof process !== "undefined" && process.env ? process.env[name] : undefined;
  const built = (import.meta.env as Record<string, string | undefined>)[name];
  return (runtime ?? built ?? "").trim();
}

/** A configured value, or the fallback when nothing supplied one. */
export function env(name: string, fallback = ""): string {
  return read(name) || fallback;
}

/** The same, with any trailing slash removed — for anything used as an origin. */
export function origin(name: string, fallback: string): string {
  return env(name, fallback).replace(/\/+$/, "");
}
