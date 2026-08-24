Toast notice — glyph-carried tone (☾ info, ✓ success, ✕ error), shadow-3 floating card. Consumer owns positioning (fixed bottom-right stack) and timing.

```jsx
<Toast tone="success" title="Message sent." body="Business enquiries get a reply within 3 days." onDismiss={close} />
<Toast tone="error" title="Could not save." action={<Button size="sm" variant="ghost">Retry</Button>} onDismiss={close} />
```
