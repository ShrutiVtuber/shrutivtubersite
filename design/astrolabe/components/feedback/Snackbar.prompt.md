Confirms a reversible thing: a draft saved, a vote cast, a chart deleted.

```jsx
<Snackbar open={saved} action="Undo" onAction={undo}>Draft saved.</Snackbar>
```

- Always offer the undo when there is one; a snackbar with no action is usually a line of copy on the screen instead.
- Never use it for validation — that belongs in the field.
