Fan-art gallery tile — square image button (opens the Modal lightbox), with the artist credit set prominently, never a footnote.

```jsx
<FanArtCard image={url} title="Dusk over Athens" artist="@aster_ink" artistHref="#" platform="X" onOpen={()=>setLightbox(url)} />
<FanArtCard image={null} artist="your art here" />  {/* empty slot invites submissions */}
```
