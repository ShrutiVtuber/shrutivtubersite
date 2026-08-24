VOD card: 16:9 thumb (sky placeholder + horizon line when no thumbnail), mono duration chip, platform badge (Twitch/YouTube glyph + word), 2-line clamped title. Hover reveals the veiled play disc, strengthens the border, tints the title.

```jsx
<VideoCard title="Building the sigil compiler — part 3" platform="twitch" duration="2:04:11" date="3 days ago" href={vodUrl} thumb={thumbUrl /* or null */} />
<VideoCard loading />
```

`loading` (or `<VideoCardSkeleton/>`) renders the pulse skeleton for auto-pulled grids.
