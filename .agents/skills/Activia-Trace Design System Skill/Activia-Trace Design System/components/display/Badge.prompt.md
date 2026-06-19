Status pill for states like Active / Aprobado / En riesgo. Color carries meaning — emerald=positive, red=negative, violet=interactive/active.

```jsx
<Badge tone="success" dot>Aprobado</Badge>
<Badge tone="danger" dot>Desaprobado</Badge>
<Badge tone="primary" icon="bolt">Active</Badge>
<Badge tone="warning">En riesgo</Badge>
<Badge tone="neutral">Midterm</Badge>
```

Tones: `primary` `success` `danger` `warning` `neutral`. `variant`: `soft` (tinted, default) or `solid`. Optional `dot` and `icon`.
