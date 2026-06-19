// DashboardScreen — welcome summary: stat tiles, cursos activos, notificaciones.
const { Card, StatCard, Badge, ProgressBar, Button } = window.ActiviaTraceDesignSystem_944743;

function DashboardScreen({ onOpenMaterias }) {
  const cursos = [
    { code: "CS-402", name: "Algoritmos Avanzados", comision: "Comisión A", alumnos: 48, prog: 78, tone: "primary" },
    { code: "DS-301", name: "Sistemas Distribuidos", comision: "Comisión B", alumnos: 56, prog: 42, tone: "tertiary" },
    { code: "MAT-102", name: "Lógica y Matemática", comision: "Comisión C", alumnos: 38, prog: 91, tone: "primary" },
  ];
  const notifs = [
    { icon: "mail", tint: "primary", text: "Nuevas calificaciones importadas en Algoritmos Avanzados", time: "hace 2 horas" },
    { icon: "warning", tint: "error", text: "14 alumnos por debajo del umbral en Sistemas Distribuidos", time: "ayer, 16:15" },
    { icon: "check_circle", tint: "tertiary", text: "Comunicación enviada a 9 alumnos atrasados", time: "20 sep 2024" },
  ];
  const tintBg = { primary: "color-mix(in srgb, var(--primary) 18%, transparent)", error: "var(--error-container)", tertiary: "var(--tertiary-container)" };
  const tintFg = { primary: "var(--primary)", error: "var(--error)", tertiary: "var(--tertiary)" };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginBottom: 24, gap: 16, flexWrap: "wrap" }}>
        <div>
          <h1 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: "-0.01em", color: "var(--on-surface)" }}>Hola, Elena</h1>
          <p style={{ margin: "4px 0 0", fontSize: 15, color: "var(--on-surface-variant)" }}>Tenés 14 alumnos en riesgo y 3 importaciones pendientes hoy.</p>
        </div>
        <div style={{ textAlign: "right" }}>
          <div style={{ fontSize: 11, letterSpacing: "0.05em", textTransform: "uppercase", color: "var(--outline)" }}>Cuatrimestre</div>
          <div style={{ fontSize: 14, fontWeight: 700, color: "var(--on-surface)" }}>2° Cuatrimestre 2024</div>
        </div>
      </div>

      {/* KPI row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 24, marginBottom: 24 }}>
        <StatCard tone="primary" label="Materias activas" value="06" icon="menu_book" trend="2 con entregas pendientes" />
        <StatCard label="Alumnos totales" value="142" icon="group" progress={88} trend="+8 este cuatrimestre" />
        <StatCard label="En riesgo" value="14" icon="warning" trendDir="down" trend="−3 esta semana" progress={32} />
        <StatCard label="Promedio general" value="7.4" icon="trending_up" trend="+0.3 vs. parcial" progress={74} />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr", gap: 24 }}>
        {/* Cursos activos */}
        <Card title="Cursos activos" icon="menu_book" action={<Button variant="ghost" size="sm" trailingIcon="arrow_forward" onClick={onOpenMaterias}>Ver todas</Button>}>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {cursos.map((c) => (
              <div key={c.code} onClick={onOpenMaterias} style={{ display: "flex", alignItems: "center", gap: 16, padding: 12, background: "var(--surface-container-low)", border: "1px solid var(--outline-variant)", borderRadius: "var(--radius-md)", cursor: "pointer" }}>
                <div style={{ width: 44, height: 44, borderRadius: "var(--radius-md)", display: "flex", alignItems: "center", justifyContent: "center", background: `color-mix(in srgb, var(--${c.tone}) 18%, transparent)`, color: `var(--${c.tone})` }}>
                  <span className="material-symbols-outlined">terminal</span>
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <span style={{ fontSize: 14, fontWeight: 700, color: "var(--on-surface)" }}>{c.name}</span>
                    <Badge tone="neutral">{c.code}</Badge>
                  </div>
                  <div style={{ fontSize: 12, color: "var(--on-surface-variant)", marginTop: 2 }}>{c.comision} · {c.alumnos} alumnos</div>
                </div>
                <div style={{ width: 120 }}><ProgressBar value={c.prog} showValue tone={c.tone === "tertiary" ? "success" : "primary"} /></div>
              </div>
            ))}
          </div>
        </Card>

        {/* Notificaciones */}
        <Card title="Notificaciones" icon="notifications" action={<Badge tone="primary">3 nuevas</Badge>}>
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            {notifs.map((n, i) => (
              <div key={i} style={{ display: "flex", gap: 12 }}>
                <div style={{ width: 32, height: 32, flexShrink: 0, borderRadius: "var(--radius-full)", display: "flex", alignItems: "center", justifyContent: "center", background: tintBg[n.tint], color: tintFg[n.tint] }}>
                  <span className="material-symbols-outlined" style={{ fontSize: 18 }}>{n.icon}</span>
                </div>
                <div>
                  <p style={{ margin: 0, fontSize: 13, color: "var(--on-surface)", lineHeight: 1.4 }}>{n.text}</p>
                  <p style={{ margin: "2px 0 0", fontSize: 11, color: "var(--outline)" }}>{n.time}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}

Object.assign(window, { DashboardScreen });
