The screen's top bar — one per screen, sticky, with the hour-tinted hem under it.

```jsx
<AppBar title="Sky" actions={<IconButton icon="menu_book" label="Sky drawer" />} />
<AppBar title="Cast a chart" back onBack={pop} hour={false} />
```

- Tab roots get no back arrow; pushed screens always do.
- Set `hour={false}` on screens where the tint would compete with content (the wheel, the writing screen).
