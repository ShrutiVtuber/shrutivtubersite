Multi-line input sharing TextField's label/hint/error/success grammar. Controlled `value` + `maxLength` adds a tabular character counter.

```jsx
<TextArea label="Your message" required rows={6} maxLength={2000} value={msg} onChange={e=>setMsg(e.target.value)}
  hint="For business enquiries use the business route — it goes to a different inbox." />
```
