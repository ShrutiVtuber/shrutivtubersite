The natal, transit or period wheel — Chart's result screen and the sky drawer.

```jsx
<ChartWheel size={320} asc={214.3} mc={128.9} cusps={cusps} bodies={bodies} aspects={aspects} />
<ChartWheel mode="period" span="1–30 Sep" bodies={bodies} phases={phases} housesKnown={false} />
```

- Signs are gilt on alternating washes; bodies are ink, retrogrades rose with ℞ printed beside the degree.
- Glyphs that would collide are nudged apart along the ring; the leader line still points at the true degree.
- `housesKnown={false}` is a real, common state — say so on the screen as well as in the drawing.
