// MateriaTabs — the 5 tab panels for a subject (Materia) detail view.
const { Card, Button, Badge, Tag, Input, Select, Checkbox, ProgressBar, StatCard, Avatar } = window.ActiviaTraceDesignSystem_944743;

const ALUMNOS = [
  { name: "Martín Suárez", comision: "A", comp: 38, nota: 4.2, rank: 18 },
  { name: "Lucía Fernández", comision: "A", comp: 52, nota: 5.1, rank: 14 },
  { name: "Diego Romero", comision: "B", comp: 41, nota: 4.8, rank: 16 },
  { name: "Sofía Castro", comision: "B", comp: 95, nota: 9.2, rank: 1 },
  { name: "Tomás Gil", comision: "C", comp: 88, nota: 8.7, rank: 3 },
  { name: "Valentina Ríos", comision: "A", comp: 29, nota: 3.4, rank: 22 },
];

function SectionTitle({ children, hint }) {
  return (
    <div style={{ display: "flex", alignItems: "baseline", gap: 10, marginBottom: 14 }}>
      <h3 style={{ margin: 0, fontSize: 14, fontWeight: 700, letterSpacing: "0.04em", textTransform: "uppercase", color: "var(--on-surface-variant)" }}>{children}</h3>
      {hint && <span style={{ fontSize: 12, color: "var(--outline)" }}>{hint}</span>}
    </div>
  );
}

function Th({ children, align }) {
  return <th style={{ textAlign: align || "left", padding: "10px 12px", fontSize: 11, fontWeight: 600, letterSpacing: "0.05em", textTransform: "uppercase", color: "var(--outline)", borderBottom: "1px solid var(--outline-variant)", whiteSpace: "nowrap" }}>{children}</th>;
}
function Td({ children, align }) {
  return <td style={{ textAlign: align || "left", padding: "12px", fontSize: 13, color: "var(--on-surface)", borderBottom: "1px solid var(--outline-variant)" }}>{children}</td>;
}

/* ---- 1. Importar Calificaciones ---- */
function ImportarPanel() {
  const [threshold, setThreshold] = React.useState(60);
  const acts = [
    { name: "Parcial 1", type: "Examen", rows: 142 },
    { name: "TP Integrador", type: "Trabajo Práctico", rows: 138 },
    { name: "Quiz Semanal 4", type: "Quiz", rows: 140 },
  ];
  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, alignItems: "start" }}>
      <Card title="Subir archivo" icon="upload_file">
        <div style={{ border: "2px dashed var(--outline-variant)", borderRadius: "var(--radius-lg)", padding: 40, display: "flex", flexDirection: "column", alignItems: "center", textAlign: "center", background: "var(--surface-container-lowest)", marginBottom: 20 }}>
          <div style={{ width: 56, height: 56, borderRadius: "var(--radius-full)", background: "var(--surface-container-high)", display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 14 }}>
            <span className="material-symbols-outlined" style={{ fontSize: 28, color: "var(--primary)" }}>cloud_upload</span>
          </div>
          <p style={{ margin: 0, fontSize: 14, fontWeight: 700, color: "var(--on-surface)" }}>Arrastrá tu archivo de notas</p>
          <p style={{ margin: "6px 0 16px", fontSize: 12, color: "var(--on-surface-variant)" }}>Formatos: CSV o XLSX · Máx 10MB</p>
          <Button variant="secondary" size="sm" icon="folder_open">Seleccionar archivo</Button>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 10, padding: 12, background: "var(--surface-container-low)", border: "1px solid var(--outline-variant)", borderRadius: "var(--radius-md)" }}>
          <span className="material-symbols-outlined" style={{ color: "var(--tertiary)" }}>description</span>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 13, fontWeight: 600 }}>notas_cs402_2c2024.xlsx</div>
            <div style={{ fontSize: 11, color: "var(--outline)" }}>2.4 MB · 142 filas detectadas</div>
          </div>
          <Badge tone="success" dot>Listo</Badge>
        </div>
      </Card>

      <Card title="Previsualización" icon="preview" action={<Badge tone="primary">{acts.length} actividades</Badge>}>
        <table style={{ width: "100%", borderCollapse: "collapse", marginBottom: 20 }}>
          <thead><tr><Th>Actividad</Th><Th>Tipo</Th><Th align="right">Registros</Th></tr></thead>
          <tbody>
            {acts.map((a) => (
              <tr key={a.name}><Td><span style={{ fontWeight: 600 }}>{a.name}</span></Td><Td><Tag>{a.type}</Tag></Td><Td align="right">{a.rows}</Td></tr>
            ))}
          </tbody>
        </table>
        <div style={{ padding: 16, background: "var(--surface-container-low)", borderRadius: "var(--radius-md)", border: "1px solid var(--outline-variant)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
            <span style={{ fontSize: 13, fontWeight: 600, color: "var(--on-surface)" }}>Umbral de aprobación</span>
            <span style={{ fontSize: 18, fontWeight: 800, color: "var(--primary)", fontFamily: "var(--font-mono)" }}>{threshold}%</span>
          </div>
          <input type="range" min="0" max="100" value={threshold} onChange={(e) => setThreshold(+e.target.value)} style={{ width: "100%", accentColor: "var(--primary)" }} />
          <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 16 }}>
            <Button variant="primary" icon="check">Confirmar importación</Button>
          </div>
        </div>
      </Card>
    </div>
  );
}

/* ---- 2. Alumnos Atrasados (4 subvistas) ---- */
function AtrasadosPanel() {
  const [sub, setSub] = React.useState("atrasados");
  const atrasados = ALUMNOS.filter((a) => a.comp < 60).sort((a, b) => a.comp - b.comp);
  const ranking = [...ALUMNOS].sort((a, b) => a.rank - b.rank);
  const subs = [
    { id: "atrasados", label: "Atrasados", icon: "warning" },
    { id: "ranking", label: "Ranking", icon: "leaderboard" },
    { id: "notas", label: "Notas Finales", icon: "grading" },
    { id: "reportes", label: "Reportes Rápidos", icon: "insights" },
  ];
  return (
    <div>
      <div style={{ display: "inline-flex", gap: 4, padding: 4, background: "var(--surface-container-low)", border: "1px solid var(--outline-variant)", borderRadius: "var(--radius-md)", marginBottom: 20 }}>
        {subs.map((s) => (
          <button key={s.id} onClick={() => setSub(s.id)} style={{ display: "inline-flex", alignItems: "center", gap: 6, padding: "7px 12px", borderRadius: "var(--radius-sm)", border: "none", cursor: "pointer", fontSize: 13, fontWeight: 600, background: sub === s.id ? "var(--primary)" : "transparent", color: sub === s.id ? "var(--on-primary)" : "var(--on-surface-variant)" }}>
            <span className="material-symbols-outlined" style={{ fontSize: 16 }}>{s.icon}</span>{s.label}
          </button>
        ))}
      </div>

      {sub === "atrasados" && (
        <Card padding={0}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead><tr><Th>Alumno</Th><Th>Comisión</Th><Th>Completitud</Th><Th align="right">Estado</Th></tr></thead>
            <tbody>
              {atrasados.map((a) => (
                <tr key={a.name}>
                  <Td><div style={{ display: "flex", alignItems: "center", gap: 10 }}><Avatar name={a.name} size="xs" /><span style={{ fontWeight: 600 }}>{a.name}</span></div></Td>
                  <Td>Comisión {a.comision}</Td>
                  <Td><div style={{ width: 160 }}><ProgressBar value={a.comp} showValue tone={a.comp < 40 ? "primary" : "primary"} /></div></Td>
                  <Td align="right"><Badge tone="danger" dot>En riesgo</Badge></Td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}

      {sub === "ranking" && (
        <Card padding={0}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead><tr><Th align="right">#</Th><Th>Alumno</Th><Th>Comisión</Th><Th align="right">Nota</Th></tr></thead>
            <tbody>
              {ranking.map((a) => (
                <tr key={a.name}>
                  <Td align="right"><span style={{ fontFamily: "var(--font-mono)", fontWeight: 700, color: a.rank <= 3 ? "var(--primary)" : "var(--on-surface-variant)" }}>{String(a.rank).padStart(2, "0")}</span></Td>
                  <Td><div style={{ display: "flex", alignItems: "center", gap: 10 }}><Avatar name={a.name} size="xs" />{a.name}</div></Td>
                  <Td>Comisión {a.comision}</Td>
                  <Td align="right"><span style={{ fontWeight: 700 }}>{a.nota.toFixed(1)}</span></Td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}

      {sub === "notas" && (
        <Card padding={0}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead><tr><Th>Alumno</Th><Th align="right">Nota final</Th><Th align="right">Resultado</Th></tr></thead>
            <tbody>
              {ALUMNOS.map((a) => (
                <tr key={a.name}>
                  <Td><div style={{ display: "flex", alignItems: "center", gap: 10 }}><Avatar name={a.name} size="xs" />{a.name}</div></Td>
                  <Td align="right"><span style={{ fontWeight: 700, fontFamily: "var(--font-mono)" }}>{a.nota.toFixed(1)}</span></Td>
                  <Td align="right">{a.nota >= 6 ? <Badge tone="success" dot>Aprobado</Badge> : <Badge tone="danger" dot>Desaprobado</Badge>}</Td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}

      {sub === "reportes" && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 24 }}>
          <StatCard label="Total alumnos" value="142" icon="group" />
          <StatCard tone="primary" label="En riesgo" value="14" icon="warning" trend="9.8% del total" />
          <StatCard label="Promedio general" value="7.4" icon="trending_up" progress={74} />
        </div>
      )}
    </div>
  );
}

/* ---- 3. Comunicar a Atrasados ---- */
function ComunicarPanel() {
  const targets = ALUMNOS.filter((a) => a.comp < 60);
  const [sel, setSel] = React.useState(() => new Set(targets.map((t) => t.name)));
  const [sent, setSent] = React.useState(false);
  const [statuses, setStatuses] = React.useState({});

  const toggle = (name) => { const n = new Set(sel); n.has(name) ? n.delete(name) : n.add(name); setSel(n); };

  const send = () => {
    setSent(true);
    const chosen = targets.filter((t) => sel.has(t.name));
    const init = {}; chosen.forEach((c) => (init[c.name] = "pendiente")); setStatuses(init);
    chosen.forEach((c, i) => {
      setTimeout(() => setStatuses((s) => ({ ...s, [c.name]: "enviando" })), 400 * (i + 1));
      setTimeout(() => setStatuses((s) => ({ ...s, [c.name]: i === 2 ? "fallido" : "ok" })), 400 * (i + 1) + 700);
    });
  };

  const statusBadge = (st) => {
    const map = { pendiente: ["neutral", "Pendiente", "schedule"], enviando: ["primary", "Enviando", "sync"], ok: ["success", "Enviado", "check_circle"], fallido: ["danger", "Fallido", "error"], cancelado: ["neutral", "Cancelado", "block"] };
    const [tone, label, icon] = map[st] || map.pendiente;
    return <Badge tone={tone} icon={icon}>{label}</Badge>;
  };

  return (
    <div style={{ display: "grid", gridTemplateColumns: sent ? "1fr 1fr" : "0.9fr 1.1fr", gap: 24, alignItems: "start" }}>
      <Card title="Destinatarios" icon="group" action={<Badge tone="primary">{sel.size} seleccionados</Badge>}>
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {targets.map((t) => (
            <label key={t.name} style={{ display: "flex", alignItems: "center", gap: 12, padding: 10, background: "var(--surface-container-low)", border: "1px solid var(--outline-variant)", borderRadius: "var(--radius-md)", cursor: "pointer" }}>
              <Checkbox checked={sel.has(t.name)} onChange={() => toggle(t.name)} />
              <Avatar name={t.name} size="xs" />
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 13, fontWeight: 600 }}>{t.name}</div>
                <div style={{ fontSize: 11, color: "var(--outline)" }}>Completitud {t.comp}%</div>
              </div>
              {sent && statuses[t.name] && statusBadge(statuses[t.name])}
            </label>
          ))}
        </div>
      </Card>

      <Card title={sent ? "Estado de envíos" : "Previsualización del mensaje"} icon={sent ? "mark_email_read" : "drafts"}>
        {!sent ? (
          <React.Fragment>
            <div style={{ padding: 18, background: "var(--surface-container-low)", border: "1px solid var(--outline-variant)", borderRadius: "var(--radius-md)", marginBottom: 18 }}>
              <p style={{ margin: "0 0 12px", fontSize: 13, fontWeight: 700, color: "var(--on-surface)" }}>Asunto: Recordatorio de actividades pendientes</p>
              <p style={{ margin: 0, fontSize: 13, lineHeight: 1.6, color: "var(--on-surface-variant)" }}>Hola <span style={{ color: "var(--primary)" }}>{"{nombre}"}</span>, notamos que tu completitud en <strong style={{ color: "var(--on-surface)" }}>Algoritmos Avanzados</strong> es del <span style={{ color: "var(--primary)" }}>{"{completitud}"}%</span>, por debajo del umbral del 60%. Te recomendamos ponerte al día con las entregas pendientes antes del cierre del cuatrimestre.</p>
            </div>
            <Button variant="primary" icon="send" fullWidth onClick={send}>Enviar a {sel.size} alumnos</Button>
          </React.Fragment>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {targets.filter((t) => sel.has(t.name)).map((t) => (
              <div key={t.name} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: 12, background: "var(--surface-container-low)", border: "1px solid var(--outline-variant)", borderRadius: "var(--radius-md)" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}><Avatar name={t.name} size="xs" /><span style={{ fontSize: 13, fontWeight: 600 }}>{t.name}</span></div>
                {statusBadge(statuses[t.name])}
              </div>
            ))}
            <Button variant="ghost" size="sm" icon="refresh" onClick={() => { setSent(false); setStatuses({}); }}>Volver a editar</Button>
          </div>
        )}
      </Card>
    </div>
  );
}

/* ---- 4. Entregas Pendientes ---- */
function EntregasPanel() {
  const rows = [
    { act: "TP Integrador", alumno: "Martín Suárez", entregado: true, corregido: false },
    { act: "Parcial 1", alumno: "Valentina Ríos", entregado: true, corregido: false },
    { act: "Quiz Semanal 4", alumno: "Diego Romero", entregado: true, corregido: true },
    { act: "TP Integrador", alumno: "Lucía Fernández", entregado: true, corregido: false },
  ];
  const pendientes = rows.filter((r) => !r.corregido);
  return (
    <Card title="Entregas sin corregir" icon="assignment_late" action={<Button variant="secondary" size="sm" icon="download">Exportar CSV</Button>}>
      <div style={{ display: "flex", gap: 12, marginBottom: 18 }}>
        <div style={{ flex: 1, padding: 14, background: "var(--surface-container-low)", border: "1px solid var(--outline-variant)", borderRadius: "var(--radius-md)" }}>
          <div style={{ fontSize: 11, textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--outline)" }}>Detectadas sin corregir</div>
          <div style={{ fontSize: 24, fontWeight: 800, color: "var(--error)" }}>{pendientes.length}</div>
        </div>
        <div style={{ flex: 1, padding: 14, background: "var(--surface-container-low)", border: "1px solid var(--outline-variant)", borderRadius: "var(--radius-md)" }}>
          <div style={{ fontSize: 11, textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--outline)" }}>Total en reporte</div>
          <div style={{ fontSize: 24, fontWeight: 800, color: "var(--on-surface)" }}>{rows.length}</div>
        </div>
      </div>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead><tr><Th>Actividad</Th><Th>Alumno</Th><Th align="right">Estado</Th></tr></thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i}>
              <Td><span style={{ fontWeight: 600 }}>{r.act}</span></Td>
              <Td>{r.alumno}</Td>
              <Td align="right">{r.corregido ? <Badge tone="success" dot>Corregido</Badge> : <Badge tone="warning" dot>Sin corregir</Badge>}</Td>
            </tr>
          ))}
        </tbody>
      </table>
    </Card>
  );
}

/* ---- 5. Monitor de Seguimiento ---- */
function MonitorPanel() {
  const [q, setQ] = React.useState("");
  const [minComp, setMinComp] = React.useState(0);
  const activities = ["Parcial 1", "TP Integrador", "Quiz 4"];
  const data = ALUMNOS.map((a) => ({ ...a, acts: [a.comp > 50, a.comp > 70, a.comp > 30] }));
  const filtered = data.filter((a) => a.name.toLowerCase().includes(q.toLowerCase()) && a.comp >= minComp);
  return (
    <Card title="Monitor de seguimiento" icon="monitoring">
      <div style={{ display: "flex", gap: 12, marginBottom: 18, flexWrap: "wrap" }}>
        <div style={{ width: 220 }}><Input icon="search" placeholder="Buscar por nombre..." value={q} onChange={(e) => setQ(e.target.value)} /></div>
        <div style={{ width: 160 }}><Select placeholder="Comisión" options={[{ value: "A", label: "Comisión A" }, { value: "B", label: "Comisión B" }, { value: "C", label: "Comisión C" }]} /></div>
        <div style={{ width: 160 }}><Select placeholder="Actividad" options={activities.map((a) => ({ value: a, label: a }))} /></div>
        <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "0 12px", background: "var(--surface-container-low)", border: "1px solid var(--outline-variant)", borderRadius: "var(--radius-md)" }}>
          <span style={{ fontSize: 12, color: "var(--on-surface-variant)", whiteSpace: "nowrap" }}>Compl. ≥ {minComp}%</span>
          <input type="range" min="0" max="100" value={minComp} onChange={(e) => setMinComp(+e.target.value)} style={{ width: 90, accentColor: "var(--primary)" }} />
        </div>
      </div>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead><tr><Th>Alumno</Th><Th>Comisión</Th>{activities.map((a) => <Th key={a} align="center">{a}</Th>)}<Th align="right">Completitud</Th></tr></thead>
        <tbody>
          {filtered.map((a) => (
            <tr key={a.name}>
              <Td><div style={{ display: "flex", alignItems: "center", gap: 10 }}><Avatar name={a.name} size="xs" />{a.name}</div></Td>
              <Td>Com. {a.comision}</Td>
              {a.acts.map((done, i) => (
                <Td key={i} align="center"><span className="material-symbols-outlined" style={{ fontSize: 18, color: done ? "var(--tertiary)" : "var(--outline)" }}>{done ? "check_circle" : "radio_button_unchecked"}</span></Td>
              ))}
              <Td align="right"><div style={{ width: 120, marginLeft: "auto" }}><ProgressBar value={a.comp} showValue /></div></Td>
            </tr>
          ))}
        </tbody>
      </table>
    </Card>
  );
}

Object.assign(window, { ImportarPanel, AtrasadosPanel, ComunicarPanel, EntregasPanel, MonitorPanel });
