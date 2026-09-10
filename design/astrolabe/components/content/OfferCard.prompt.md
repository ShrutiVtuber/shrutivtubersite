Her classes, reading slots, shop and support links on Home — the only gilt-highlighted card in the app.

```jsx
<OfferCard title="Six weeks of Hellenistic basics" body="Live on Thursdays, recorded for members."
  price="€120" cadence="for six weeks" href="https://shrutivtuber.com/classes" mark="♃" />
<OfferCard title="Members' chart clinic" price="Included" membersOnly locked onOpen={explain} />
```

- Always `external` in effect: the card opens a browser, never an in-app purchase.
- Never more than two on Home; offers are a section, not a shop.
