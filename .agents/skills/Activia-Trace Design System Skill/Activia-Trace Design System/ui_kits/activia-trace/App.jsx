// App — orchestrates auth + routing across the Activia-Trace screens.
const { AppShell, LoginScreen, DashboardScreen, MateriasScreen, ProfileScreen, ErrorScreen } = window;

function App() {
  const [authed, setAuthed] = React.useState(false);
  const [route, setRoute] = React.useState("dashboard");
  const [materia, setMateria] = React.useState(null);

  if (!authed) return <LoginScreen onLogin={() => setAuthed(true)} />;

  const crumbs = {
    dashboard: ["Activia-Trace", "Dashboard"],
    materias: materia ? ["Activia-Trace", "Mis Materias", materia] : ["Activia-Trace", "Mis Materias"],
    profile: ["Activia-Trace", "Mi Perfil"],
    "403": ["Activia-Trace", "Error 403"],
    "404": ["Activia-Trace", "Error 404"],
  };

  const navigate = (r) => { setRoute(r); if (r !== "materias") setMateria(null); };

  return (
    <AppShell route={route} onNavigate={navigate} onLogout={() => { setAuthed(false); setRoute("dashboard"); setMateria(null); }} breadcrumb={crumbs[route]}>
      {route === "dashboard" && <DashboardScreen onOpenMaterias={() => navigate("materias")} />}
      {route === "materias" && <MateriasScreen selected={materia} onSelect={setMateria} onBack={() => setMateria(null)} />}
      {route === "profile" && <ProfileScreen />}
      {route === "403" && <ErrorScreen code="403" onHome={() => navigate("dashboard")} />}
      {route === "404" && <ErrorScreen code="404" onHome={() => navigate("dashboard")} />}
    </AppShell>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
