Primary action control — solid violet for the main action, outlined/ghost for secondary.

```jsx
<Button variant="primary" icon="add">New Entry</Button>
<Button variant="secondary" icon="filter_list">Filters</Button>
<Button variant="tertiary" icon="save">Commit Changes</Button>
<Button variant="ghost">Cancel</Button>
<Button variant="danger" icon="delete">Delete</Button>
```

Variants: `primary` (solid violet, default), `secondary` (raised surface + border), `tertiary` (emerald), `ghost` (text-only), `danger`. Sizes: `sm` `md` `lg`. Props: `icon`/`trailingIcon` (Material Symbols name), `fullWidth`, `disabled`. One primary action per view; pair with a secondary, never two primaries.
