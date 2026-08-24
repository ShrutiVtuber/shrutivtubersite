The page-opening sky panel — dawn gradient in light, dusk with stars in dark, closed by the 1px horizon line. Designed art-absent first: without `art` a hairline moon disc holds the right side; with `art` the character stands on the horizon and the text column narrows.

```jsx
<Hero greeting="Welcome · Καλώς ήρθατε · स्वागत"
  title="I build instruments for magick."
  subtitle="Software for astrology, theurgy and divination — built live on stream from Athens."
  actions={<><Button>Watch live</Button><Button variant="secondary">See the work</Button></>}
  footnote={<SocialLinkRow links={socials} />}
  art={heroArt /* or null */} clouds={cloudsUrl /* optional */} />
```

Use exactly one per page. `clouds` accepts the brand clouds PNG when available.
