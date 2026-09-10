Waiting, in the four shapes the app actually needs.

```jsx
<Progress kind="refresh" />
<Progress kind="bar" value={62} label="Greek pack" />
<Skeleton lines={3} />
```

- Instruments do not need a spinner: they compute on device in a frame. Only her half of the app waits.
- A skeleton must have the silhouette of the real card, or it reads as a broken screen.
