import type { Config } from "tailwindcss";
import preset from "@shruti/shared/tailwind-preset";

export default {
  presets: [preset],
  content: ["./src/**/*.{astro,html,js,jsx,md,ts,tsx}"],
} satisfies Config;
