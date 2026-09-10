The workhorse of Settings, Account, Notifications, Licences and the place picker.

```jsx
<ListGroup>
  <ListRow label="Place" description="Used for sunrise and the hours" value="Athens, Greece" onClick={pickPlace} />
  <ListRow label="Notifications" value="3 on" onClick={go} />
  <ListRow label="Support her work" external href="https://shrutivtuber.com/support" />
</ListGroup>
```

- `external` swaps the chevron for the leave-the-app mark — required for anything that takes money.
- `danger` is for delete only, and always behind a confirm Dialog.
