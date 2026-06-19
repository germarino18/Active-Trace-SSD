KPI tile — big number, label, optional trend caption and progress bar. Use `tone="primary"` for the one filled-violet highlight stat per group.

```jsx
<StatCard tone="primary" label="Promedio general" value="3.88" trend="Top 5% del depto." icon="trending_up" />
<StatCard label="Alumnos en riesgo" value="14" icon="warning" progress={32} trend="−3 esta semana" trendDir="down" />
```

`value` is any node; `unit` is a small suffix (e.g. "%"). `progress` (0–100) renders a bottom bar. `trendDir` flips the arrow + color (down=red, up=emerald). Used in the Reportes Rápidos cards.
