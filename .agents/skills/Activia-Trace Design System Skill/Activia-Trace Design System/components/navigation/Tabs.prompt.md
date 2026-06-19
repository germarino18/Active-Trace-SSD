Underlined horizontal tab bar — the Mis Materias layout uses it for its 5 sub-views. Controlled.

```jsx
const [tab, setTab] = React.useState("atrasados");
<Tabs value={tab} onChange={setTab} tabs={[
  { id: "importar", label: "Importar", icon: "upload_file" },
  { id: "atrasados", label: "Atrasados", icon: "warning", badge: 14 },
  { id: "comunicar", label: "Comunicar", icon: "send" },
]} />
```

Active tab = violet text + 2px violet underline. Each tab takes `icon` (Material Symbols) and `badge` (count chip).
