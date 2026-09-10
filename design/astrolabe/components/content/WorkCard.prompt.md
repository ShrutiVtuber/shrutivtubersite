The practice-room feed: a reading somebody wrote, with its votes and comment count.

```jsx
<WorkCard title="Saturn on the descendant, and what it asked of me" author="korax" date="9 Sep"
  votes={14} myVote={1} comments={6} sign="Capricorn" onOpen={open} onVote={vote} />
<WorkCard mine title="First pass at the eclipse" date="8 Sep" status="draft" votes={0} comments={0} />
```

- Signed-out readers see the vote control disabled, not hidden — the affordance explains itself on tap.
- `status` only ever appears on your own work.
