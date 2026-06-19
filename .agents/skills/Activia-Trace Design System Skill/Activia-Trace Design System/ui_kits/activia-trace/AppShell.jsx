// AppShell — sidebar + top header layout reused across every post-login screen.
const { NavItem, IconButton, Avatar, Button, Input } = window.ActiviaTraceDesignSystem_944743;

function Sidebar({ route, onNavigate, onLogout }) {
  return (
    <aside style={{
      position: "fixed", left: 0, top: 0, height: "100vh", width: 256,
      background: "var(--surface-container)", borderRight: "1px solid var(--outline-variant)",
      display: "flex", flexDirection: "column", padding: "24px 16px", zIndex: 50, boxSizing: "border-box",
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, padding: "0 8px", marginBottom: 32 }}>
        <div style={{ width: 36, height: 36, background: "var(--primary)", borderRadius: "var(--radius-md)", display: "flex", alignItems: "center", justifyContent: "center", color: "var(--on-primary)" }}>
          <span className="material-symbols-outlined" style={{ fontSize: 22, fontVariationSettings: "'FILL' 1" }}>analytics</span>
        </div>
        <div>
          <div style={{ fontSize: 17, fontWeight: 700, letterSpacing: "-0.02em", color: "var(--on-surface)" }}>Activia-Trace</div>
          <div style={{ fontSize: 9, letterSpacing: "0.18em", textTransform: "uppercase", color: "var(--on-surface-variant)", opacity: 0.6 }}>Academic Management</div>
        </div>
      </div>

      <nav style={{ display: "flex", flexDirection: "column", gap: 4, flex: 1 }}>
        <NavItem icon="dashboard" label="Dashboard" active={route === "dashboard"} onClick={(e) => { e.preventDefault(); onNavigate("dashboard"); }} />
        <NavItem icon="menu_book" label="Mis Materias" badge="6" active={route === "materias"} onClick={(e) => { e.preventDefault(); onNavigate("materias"); }} />
        <NavItem icon="person" label="Mi Perfil" active={route === "profile"} onClick={(e) => { e.preventDefault(); onNavigate("profile"); }} />
        <div style={{ height: 1, background: "var(--outline-variant)", margin: "8px 12px" }} />
        <NavItem icon="lock" label="Demo · 403" active={route === "403"} onClick={(e) => { e.preventDefault(); onNavigate("403"); }} />
        <NavItem icon="error" label="Demo · 404" active={route === "404"} onClick={(e) => { e.preventDefault(); onNavigate("404"); }} />
      </nav>

      <div style={{ marginTop: "auto", display: "flex", flexDirection: "column", gap: 16 }}>
        <Button variant="primary" icon="add" fullWidth>Nueva Materia</Button>
        <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "0 4px" }}>
          <Avatar name="Elena Vance" status="online" size="sm" />
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: 12, fontWeight: 700, color: "var(--on-surface)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>Dra. Elena Vance</div>
            <div style={{ fontSize: 10, color: "var(--on-surface-variant)" }}>Docente</div>
          </div>
          <IconButton icon="logout" size="sm" label="Cerrar sesión" onClick={onLogout} />
        </div>
      </div>
    </aside>
  );
}

function TopHeader({ breadcrumb = [] }) {
  return (
    <header style={{
      position: "sticky", top: 0, zIndex: 40, height: 64,
      display: "flex", alignItems: "center", justifyContent: "space-between",
      padding: "0 24px", background: "var(--glass-bg)", backdropFilter: "blur(12px)",
      WebkitBackdropFilter: "blur(12px)", borderBottom: "1px solid var(--outline-variant)",
    }}>
      <nav style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 13 }}>
        {breadcrumb.map((b, i) => (
          <React.Fragment key={i}>
            <span style={{ color: i === breadcrumb.length - 1 ? "var(--on-surface)" : "var(--on-surface-variant)", fontWeight: i === breadcrumb.length - 1 ? 600 : 400 }}>{b}</span>
            {i < breadcrumb.length - 1 && <span className="material-symbols-outlined" style={{ fontSize: 16, color: "var(--outline)" }}>chevron_right</span>}
          </React.Fragment>
        ))}
      </nav>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <div style={{ width: 240 }}><Input pill icon="search" placeholder="Buscar..." /></div>
        <IconButton icon="notifications" dot label="Notificaciones" />
        <IconButton icon="help" label="Ayuda" />
        <div style={{ width: 1, height: 28, background: "var(--outline-variant)", margin: "0 4px" }} />
        <Avatar name="Elena Vance" ring size="sm" />
      </div>
    </header>
  );
}

function AppShell({ route, onNavigate, onLogout, breadcrumb, children }) {
  return (
    <div style={{ minHeight: "100vh", background: "var(--background)" }}>
      <Sidebar route={route} onNavigate={onNavigate} onLogout={onLogout} />
      <main style={{ marginLeft: 256, minHeight: "100vh", display: "flex", flexDirection: "column" }}>
        <TopHeader breadcrumb={breadcrumb} />
        <div style={{ padding: 24, flex: 1 }}>{children}</div>
      </main>
    </div>
  );
}

Object.assign(window, { AppShell });
