/* The site's 404 page with a real 404 status (a rewrite keeps the status of
   the request it came from, so /404 rendered through one would answer 200). */
export async function notFound(astro: any): Promise<Response> {
  const page: Response = await astro.rewrite("/404");
  return new Response(page.body, { status: 404, headers: page.headers });
}
