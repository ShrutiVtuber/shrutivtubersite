Whether she is live — the first thing most people open the app for, and the moment it earns its place.

```jsx
<LiveBanner status="live" title="Casting charts for the chat" game="Just Chatting" viewers={412} onOpen={openStream} />
<LiveBanner status="offline" nextStream="Thursday 20:00 Athens" />
<LiveBanner status="unknown" />
```

- Three states, always. `unknown` is not `offline` — the copy must not claim a fact the app could not check.
- When live, also stamp `data-live="true"` on the app shell so the tab bar hem and Masthead follow.
- Never render this without a status; there is no fourth, silent state.
