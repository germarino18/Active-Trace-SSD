Base surface container — hairline border, no shadow (Obsidian separates with borders, not elevation).

```jsx
<Card title="Performance Metrics" icon="monitoring" action={<Badge tone="success" dot>Live</Badge>}>
  …content…
</Card>
<Card variant="glass">…floating panel…</Card>
```

Variants: `default`, `low` (sunken), `glass` (backdrop blur — headers, floating menus). The optional `title` renders as an uppercase eyebrow; `action` is a right-aligned slot. `hover` lifts the card 2px and brightens the border. Default radius 12px, padding 24px.
