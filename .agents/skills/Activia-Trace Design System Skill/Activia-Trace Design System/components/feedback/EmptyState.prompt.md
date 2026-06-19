Centered placeholder for empty tables and the 403 / 404 error screens.

```jsx
<EmptyState code="403" title="Sin permisos" message="No tenés acceso a esta sección."
  action={<Button variant="secondary" icon="arrow_back">Volver al dashboard</Button>} />
<EmptyState icon="table_rows" title="Sin alumnos atrasados" message="Importá calificaciones para empezar." />
```

Pass `code` ("403"/"404") for the big violet numeral, or `icon` for a tinted-circle glyph. `action` is usually a Button.
