A short, focused choice that does not deserve a screen of its own.

```jsx
<Sheet open={open} title="Sunrise convention" onClose={close}
  actions={<Button full onClick={close}>Done</Button>}>
  <ChoiceRow type="radio" label="Sunrise" rule="The Sun's upper limb clears the horizon." checked />
</Sheet>
```

- Rises over `--dur-2` on `--ease-sheet`. The scrim closes it; so does the handle.
- Anything taller than ~72% of the screen belongs in a full-screen Dialog instead.
