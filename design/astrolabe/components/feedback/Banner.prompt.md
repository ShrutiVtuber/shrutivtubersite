The app telling you something about itself, in place, without a dialog.

```jsx
<Banner tone="offline" title="Her half is out of reach">
  The instruments all still work — they compute on your phone. Readings and the practice room will return.
</Banner>
<Banner tone="error" title="Sign-in failed" action="Try again" onAction={retry}>The site answered, but not with a token.</Banner>
```

- One banner at a time, directly under the AppBar, inside the gutter.
- `caution` is the astrological one (a station, an undefined angle); `error` is the app's own fault.
