Labelled single-line input. Validation renders as a ✕/✓ prefixed line (never colour alone); invalid fields get a live-red border + wash. 44px min hit target.

```jsx
<TextField label="Email" type="email" required placeholder="you@example.com" hint="Business enquiries get a reply within 3 days." />
<TextField label="Email" required error="Enter a valid email address." />
<TextField label="Company" optionalLabel />
```
