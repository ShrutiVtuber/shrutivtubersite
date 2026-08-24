/// <reference types="astro/client" />

declare namespace App {
  interface Locals {
    /** Minted in middleware, rendered by <CsrfField />, checked by verifyCsrf. */
    csrf: string;
  }
}
