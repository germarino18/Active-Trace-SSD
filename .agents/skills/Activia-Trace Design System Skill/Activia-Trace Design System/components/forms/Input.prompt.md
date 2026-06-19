Text field with uppercase label, optional leading icon, helper/error text, and violet focus ring.

```jsx
<Input label="Email" icon="mail" placeholder="you@uni.edu" />
<Input label="Tenant ID" icon="domain" placeholder="institution-id" />
<Input pill icon="search" placeholder="Search records…" />
<Input label="Threshold" error="Required field" />
```

Surface-low fill, hairline border that turns violet on focus. `pill` for rounded search bars. `error` turns border + helper red. Spreads native input props (`type`, `value`, `onChange`, etc.).
