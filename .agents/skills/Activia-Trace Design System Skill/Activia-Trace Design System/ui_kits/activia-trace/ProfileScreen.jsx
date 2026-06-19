// ProfileScreen & ErrorScreen.
const { Card, Avatar, Button, Badge, Input, EmptyState } = window.ActiviaTraceDesignSystem_944743;

function ProfileScreen() {
  return (
    <div>
      <h1 style={{ margin: "0 0 24px", fontSize: 32, fontWeight: 700, letterSpacing: "-0.01em", color: "var(--on-surface)" }}>Mi Perfil</h1>
      <div style={{ display: "grid", gridTemplateColumns: "320px 1fr", gap: 24, alignItems: "start" }}>
        <Card>
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", textAlign: "center", gap: 4 }}>
            <Avatar name="Elena Vance" size="lg" ring />
            <div style={{ fontSize: 18, fontWeight: 700, color: "var(--on-surface)", marginTop: 8 }}>Dra. Elena Vance</div>
            <div style={{ fontSize: 13, color: "var(--on-surface-variant)" }}>elena.vance@uni.edu</div>
            <div style={{ display: "flex", gap: 6, marginTop: 12, flexWrap: "wrap", justifyContent: "center" }}>
              <Badge tone="primary">Docente</Badge>
              <Badge tone="neutral">Coordinadora</Badge>
            </div>
          </div>
          <div style={{ height: 1, background: "var(--outline-variant)", margin: "20px 0" }} />
          <div style={{ display: "flex", flexDirection: "column", gap: 12, fontSize: 13 }}>
            <div style={{ display: "flex", justifyContent: "space-between" }}><span style={{ color: "var(--outline)" }}>Institución</span><span style={{ color: "var(--on-surface)", fontWeight: 600 }}>Universidad Central</span></div>
            <div style={{ display: "flex", justifyContent: "space-between" }}><span style={{ color: "var(--outline)" }}>Tenant ID</span><span style={{ fontFamily: "var(--font-mono)", color: "var(--on-surface-variant)" }}>universidad-central</span></div>
            <div style={{ display: "flex", justifyContent: "space-between" }}><span style={{ color: "var(--outline)" }}>2FA</span><Badge tone="success" dot>Activo</Badge></div>
          </div>
        </Card>

        <Card title="Información de la cuenta" icon="badge" action={<Button variant="secondary" size="sm" icon="edit">Editar</Button>}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
            <Input label="Nombre" value="Elena" readOnly />
            <Input label="Apellido" value="Vance" readOnly />
            <Input label="Email" icon="mail" value="elena.vance@uni.edu" readOnly />
            <Input label="Teléfono" icon="call" value="+54 11 5555-0142" readOnly />
          </div>
          <div style={{ height: 1, background: "var(--outline-variant)", margin: "24px 0" }} />
          <h3 style={{ margin: "0 0 14px", fontSize: 13, fontWeight: 700, letterSpacing: "0.05em", textTransform: "uppercase", color: "var(--on-surface-variant)" }}>Roles asignados</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {[["Docente", "Gestión de calificaciones y comunicación", "school"], ["Coordinadora", "Acceso a reportes de toda la carrera", "supervisor_account"]].map(([r, d, ic]) => (
              <div key={r} style={{ display: "flex", alignItems: "center", gap: 12, padding: 12, background: "var(--surface-container-low)", border: "1px solid var(--outline-variant)", borderRadius: "var(--radius-md)" }}>
                <div style={{ width: 36, height: 36, borderRadius: "var(--radius-md)", background: "color-mix(in srgb, var(--primary) 14%, transparent)", color: "var(--primary)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <span className="material-symbols-outlined" style={{ fontSize: 20 }}>{ic}</span>
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 13, fontWeight: 700, color: "var(--on-surface)" }}>{r}</div>
                  <div style={{ fontSize: 12, color: "var(--on-surface-variant)" }}>{d}</div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}

function ErrorScreen({ code, onHome }) {
  const cfg = code === "403"
    ? { title: "Sin permisos", message: "No tenés acceso a esta sección. Si creés que es un error, contactá a tu administrador." }
    : { title: "Página no encontrada", message: "La ruta que buscás no existe o fue movida. Verificá la dirección e intentá de nuevo." };
  return (
    <div style={{ minHeight: "60vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <EmptyState code={code} title={cfg.title} message={cfg.message}
        action={<Button variant="primary" icon="arrow_back" onClick={onHome}>Volver al dashboard</Button>} />
    </div>
  );
}

Object.assign(window, { ProfileScreen, ErrorScreen });
