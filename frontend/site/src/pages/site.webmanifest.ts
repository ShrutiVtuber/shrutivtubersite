/* The web app manifest — what a phone uses when someone adds the site to a
 * home screen. Small, and worth having: an installed page with no manifest
 * gets the browser's own chrome and a screenshot for an icon.
 */
import type { APIRoute } from "astro";

export const GET: APIRoute = () =>
  new Response(
    JSON.stringify({
      name: "Shruti",
      short_name: "Shruti",
      description: "Instruments for magick, astrology and divination.",
      start_url: "/",
      display: "standalone",
      background_color: "#121829",
      theme_color: "#121829",
      icons: [
        { src: "/icon-192.png", sizes: "192x192", type: "image/png" },
        { src: "/apple-touch-icon.png", sizes: "180x180", type: "image/png" },
      ],
    }),
    {
      headers: {
        "Content-Type": "application/manifest+json",
        "Cache-Control": "public, max-age=86400",
      },
    },
  );
