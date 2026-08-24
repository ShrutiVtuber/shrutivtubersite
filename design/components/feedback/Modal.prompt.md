Modal dialog on a blurred veil — Esc / backdrop / ✕ close. `variant="lightbox"` turns it into the fan-art lightbox (dark surface, floating close, credit as caption).

```jsx
<Modal open={open} onClose={close} title="Submit fan art"
  footer={<><Button variant="ghost" onClick={close}>Cancel</Button><Button>Submit</Button></>}>
  <TextField label="Link to your post" required />
</Modal>
<Modal open={!!img} onClose={()=>setImg(null)} variant="lightbox">
  <img src={img} alt="" style={{maxHeight:'80vh'}} />
</Modal>
```
