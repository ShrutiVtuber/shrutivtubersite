A confirm, or the sky drawer.

```jsx
<Dialog title="Delete this draft?" subtitle="This cannot be undone." onClose={close}
  actions={<><Button variant="text" onClick={close}>Keep</Button>
            <Button variant="outlined" destructive onClick={del}>Delete</Button></>} />

<Dialog size="fullscreen" title="Sky drawer" subtitle="Ephemeris · September 2026" onClose={close}>
  <DataTable columns={cols} rows={rows} />
</Dialog>
```

- A confirm always names the thing and its consequence in the title and subtitle.
- The full-screen dialog keeps the hour hem; the small one does not.
