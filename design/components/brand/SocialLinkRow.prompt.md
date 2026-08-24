Social/platform link row — icon glyphs tinted to the current ink via CSS mask, so they follow both themes automatically. Every link is labelled for screen readers.

```jsx
<SocialLinkRow links={[
  {platform:'twitch', href:'#'}, {platform:'youtube', href:'#'},
  {platform:'discord', href:'#'}, {platform:'github', href:'#'}]} />
```

`variant="pills"` adds bordered pills with names (footer, press kit). Also exports `SocialIcon` for standalone glyph use (e.g. inside VideoCard platform badges).
