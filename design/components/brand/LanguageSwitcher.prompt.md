Language switcher pill — EN / ΕΛ / हि / FR, each code set in its own script with `lang` attributes. Button mode (SPA) or link mode via `hrefFor` (static pages, journal language variants).

```jsx
<LanguageSwitcher current="en" onChange={setLang} />
<LanguageSwitcher current="el" hrefFor={l => `/${l}/journal/on-planetary-hours`} />
```
