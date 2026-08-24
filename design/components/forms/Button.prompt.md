Button in four variants — primary (filled blue), secondary (hairline outline), ghost (text), live (red, reserved for the watch-live CTA). Press = darken + 1px sink, never scale.

```jsx
<Button size="lg">Watch live</Button>
<Button variant="secondary">See the work</Button>
<Button variant="ghost" iconRight={<span aria-hidden>→</span>}>Read the journal</Button>
<Button loading>Sending…</Button>
```

States: hover, focus-visible ring, active, `disabled`, `loading` (spinner keeps button width; label hidden, aria-busy set). `href` renders an anchor.
