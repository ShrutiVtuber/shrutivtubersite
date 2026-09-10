An immediate on/off in Settings and Notifications — it saves the moment it is tapped, with no Save button.

```jsx
<Switch label="Tell me when she goes live" description="Within ninety seconds" checked={live} onChange={setLive} />
```

- Never use a switch for something that needs confirming; that is a ChoiceRow plus a button.
- The description carries the consequence, not a restatement of the label.
