Voting on a practice reading. Lives at the left edge of WorkCard and at the head of a work's own screen.

```jsx
<VoteControl value={14} mine={1} onVote={setVote} />
<VoteControl value={0} disabled />
```

- Tapping your own vote again clears it.
- Down-vote is rose, up-vote is accent blue; the arrow weight changes too.
