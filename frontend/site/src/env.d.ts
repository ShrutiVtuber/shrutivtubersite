/// <reference types="astro/client" />

declare namespace App {
  interface Locals {
    /** Minted in middleware, rendered by <CsrfField />, checked by verifyCsrf. */
    csrf: string;
    /** True when the operator is seeing the site past the holding page. */
    bypassingHolding?: boolean;
    /** Set when she is looking at a section the public gets a 404 for. */
    previewingSection?: string;
    /** Which sections visitors may reach; the nav drops the rest. */
    sectionsLive?: Record<string, boolean>;
  }
}
