// MateriasScreen — list of subjects; selecting one opens the 5-tab detail layout.
const { Card, Badge, Tabs, Button, ProgressBar } = window.ActiviaTraceDesignSystem_944743;

const MATERIAS = [
  { code: "CS-402", name: "Algoritmos Avanzados", comisiones: 2, alumnos: 48, prog: 78, riesgo: 14, color: "primary", icon: "terminal" },
  { code: "DS-301", name: "Sistemas Distribuidos", comisiones: 1, alumnos: 56, prog: 42, riesgo: 9, color: "tertiary", icon: "database" },
  { code: "MAT-102", name: "Lógica y Matemática", comisiones: 3, alumnos: 38, prog: 91, riesgo: 2, color: "primary", icon: "functions" },
  { code: "AR-210", name: "Arquitectura y Diseño", comisiones: 1, alumnos: 38, prog: 64, riesgo: 6, color: "primary", icon: "memory" },
];

function MateriasScreen({ selected, onSelect, onBack }) {
  const [tab, setTab] = React.useState("importar");
  const materia = MATERIAS.find((m) => m.code === selected);

  if (!materia) {
    return (
      <div>
        <h1 style={{ margin: "0 0 4px", fontSize: 32, fontWeight: 700, letterSpacing: "-0.01em", color: "var(--on-surface)" }}>Mis Materias</h1>
        <p style={{ margin: "0 0 24px", fontSize: 15, color: "var(--on-surface-variant)" }}>Materias que dictás este cuatrimestre. Entrá a una para gestionar calificaciones.</p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 24 }}>
          {MATERIAS.map((m) => (
            <Card key={m.code} hover style={{ cursor: "pointer" }}>
              <div onClick={() => onSelect(m.code)}>
                <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 16 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                    <div style={{ width: 44, height: 44, borderRadius: "var(--radius-md)", display: "flex", alignItems: "center", justifyContent: "center", background: `color-mix(in srgb, var(--${m.color}) 18%, transparent)`, color: `var(--${m.color})` }}>
                      <span className="material-symbols-outlined">{m.icon}</span>
                    </div>
                    <div>
                      <div style={{ fontSize: 15, fontWeight: 700, color: "var(--on-surface)" }}>{m.name}</div>
                      <div style={{ fontSize: 12, color: "var(--on-surface-variant)", marginTop: 2 }}>{m.code} · {m.comisiones} comisión{m.comisiones > 1 ? "es" : ""}</div>
                    </div>
                  </div>
                  {m.riesgo > 10 ? <Badge tone="danger" dot>{m.riesgo} en riesgo</Badge> : <Badge tone="neutral">{m.riesgo} en riesgo</Badge>}
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
                  <div style={{ fontSize: 12, color: "var(--on-surface-variant)" }}><span style={{ fontWeight: 700, color: "var(--on-surface)" }}>{m.alumnos}</span> alumnos</div>
                  <div style={{ flex: 1 }}><ProgressBar value={m.prog} showValue label="Completitud" tone={m.color === "tertiary" ? "success" : "primary"} /></div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  const tabs = [
    { id: "importar", label: "Importar Calificaciones", icon: "upload_file" },
    { id: "atrasados", label: "Alumnos Atrasados", icon: "warning", badge: materia.riesgo },
    { id: "comunicar", label: "Comunicar", icon: "send" },
    { id: "entregas", label: "Entregas Pendientes", icon: "assignment_late" },
    { id: "monitor", label: "Monitor de Seguimiento", icon: "monitoring" },
  ];

  return (
    <div>
      <button onClick={onBack} style={{ display: "inline-flex", alignItems: "center", gap: 4, background: "none", border: "none", color: "var(--on-surface-variant)", fontSize: 13, cursor: "pointer", padding: 0, marginBottom: 16 }}>
        <span className="material-symbols-outlined" style={{ fontSize: 16 }}>arrow_back</span> Mis Materias
      </button>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 20, gap: 16, flexWrap: "wrap" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <div style={{ width: 48, height: 48, borderRadius: "var(--radius-md)", display: "flex", alignItems: "center", justifyContent: "center", background: `color-mix(in srgb, var(--${materia.color}) 18%, transparent)`, color: `var(--${materia.color})` }}>
            <span className="material-symbols-outlined" style={{ fontSize: 26 }}>{materia.icon}</span>
          </div>
          <div>
            <h1 style={{ margin: 0, fontSize: 26, fontWeight: 700, letterSpacing: "-0.01em", color: "var(--on-surface)" }}>{materia.name}</h1>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 4 }}>
              <Badge tone="neutral">{materia.code}</Badge>
              <span style={{ fontSize: 13, color: "var(--on-surface-variant)" }}>{materia.alumnos} alumnos · {materia.comisiones} comisión{materia.comisiones > 1 ? "es" : ""}</span>
            </div>
          </div>
        </div>
        <Button variant="secondary" size="sm" icon="settings">Configuración</Button>
      </div>

      <div style={{ marginBottom: 24 }}><Tabs tabs={tabs} value={tab} onChange={setTab} /></div>

      {tab === "importar" && <window.ImportarPanel />}
      {tab === "atrasados" && <window.AtrasadosPanel />}
      {tab === "comunicar" && <window.ComunicarPanel />}
      {tab === "entregas" && <window.EntregasPanel />}
      {tab === "monitor" && <window.MonitorPanel />}
    </div>
  );
}

Object.assign(window, { MateriasScreen });
