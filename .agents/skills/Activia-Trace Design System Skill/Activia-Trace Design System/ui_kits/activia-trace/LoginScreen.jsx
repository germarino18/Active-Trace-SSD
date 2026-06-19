// LoginScreen — email + password + tenant ID, with optional 2FA step.
const { Input, Button } = window.ActiviaTraceDesignSystem_944743;

function LoginScreen({ onLogin }) {
  const [step, setStep] = React.useState("credentials"); // credentials | twofa
  const [email, setEmail] = React.useState("elena.vance@uni.edu");
  const [pwd, setPwd] = React.useState("••••••••••");
  const [tenant, setTenant] = React.useState("universidad-central");
  const [code, setCode] = React.useState(["", "", "", "", "", ""]);

  const setDigit = (i, v) => {
    if (!/^\d?$/.test(v)) return;
    const next = [...code]; next[i] = v; setCode(next);
    if (v && i < 5) { const el = document.getElementById("otp-" + (i + 1)); if (el) el.focus(); }
  };

  return (
    <div style={{ minHeight: "100vh", background: "var(--background)", display: "flex", alignItems: "center", justifyContent: "center", padding: 24, position: "relative", overflow: "hidden" }}>
      {/* subtle violet glow, matches product hero decoration */}
      <div style={{ position: "absolute", top: "-20%", right: "-10%", width: 600, height: 600, background: "color-mix(in srgb, var(--primary) 8%, transparent)", filter: "blur(140px)", borderRadius: "50%", pointerEvents: "none" }} />
      <div style={{ position: "absolute", bottom: "-20%", left: "-10%", width: 600, height: 600, background: "color-mix(in srgb, var(--tertiary) 5%, transparent)", filter: "blur(150px)", borderRadius: "50%", pointerEvents: "none" }} />

      <div style={{ width: 400, maxWidth: "100%", position: "relative", zIndex: 1 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12, justifyContent: "center", marginBottom: 28 }}>
          <div style={{ width: 44, height: 44, background: "var(--primary)", borderRadius: "var(--radius-md)", display: "flex", alignItems: "center", justifyContent: "center", color: "var(--on-primary)" }}>
            <span className="material-symbols-outlined" style={{ fontSize: 26, fontVariationSettings: "'FILL' 1" }}>analytics</span>
          </div>
          <div>
            <div style={{ fontSize: 22, fontWeight: 700, letterSpacing: "-0.02em", color: "var(--on-surface)" }}>Activia-Trace</div>
            <div style={{ fontSize: 9, letterSpacing: "0.18em", textTransform: "uppercase", color: "var(--on-surface-variant)", opacity: 0.6 }}>Academic Management</div>
          </div>
        </div>

        <div style={{ background: "var(--surface-container)", border: "1px solid var(--outline-variant)", borderRadius: "var(--radius-lg)", padding: 28 }}>
          {step === "credentials" ? (
            <React.Fragment>
              <h1 style={{ margin: "0 0 4px", fontSize: 22, fontWeight: 700, letterSpacing: "-0.01em", color: "var(--on-surface)" }}>Iniciar sesión</h1>
              <p style={{ margin: "0 0 24px", fontSize: 14, color: "var(--on-surface-variant)" }}>Ingresá a tu institución para continuar.</p>
              <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                <Input label="Email" icon="mail" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
                <Input label="Contraseña" icon="lock" type="password" value={pwd} onChange={(e) => setPwd(e.target.value)} />
                <Input label="ID de Institución (tenant)" icon="domain" value={tenant} onChange={(e) => setTenant(e.target.value)} helper="Identificador provisto por tu institución" />
                <div style={{ display: "flex", justifyContent: "flex-end", marginTop: -4 }}>
                  <a href="#" style={{ fontSize: 13, color: "var(--primary)", textDecoration: "none", fontWeight: 500 }}>¿Olvidaste tu contraseña?</a>
                </div>
                <Button variant="primary" size="lg" fullWidth trailingIcon="arrow_forward" onClick={() => setStep("twofa")}>Continuar</Button>
              </div>
            </React.Fragment>
          ) : (
            <React.Fragment>
              <button onClick={() => setStep("credentials")} style={{ display: "inline-flex", alignItems: "center", gap: 4, background: "none", border: "none", color: "var(--on-surface-variant)", fontSize: 13, cursor: "pointer", padding: 0, marginBottom: 16 }}>
                <span className="material-symbols-outlined" style={{ fontSize: 16 }}>arrow_back</span> Volver
              </button>
              <h1 style={{ margin: "0 0 4px", fontSize: 22, fontWeight: 700, letterSpacing: "-0.01em", color: "var(--on-surface)" }}>Verificación 2FA</h1>
              <p style={{ margin: "0 0 24px", fontSize: 14, color: "var(--on-surface-variant)" }}>Ingresá el código de 6 dígitos de tu app de autenticación.</p>
              <div style={{ display: "flex", gap: 8, justifyContent: "space-between", marginBottom: 24 }}>
                {code.map((d, i) => (
                  <input key={i} id={"otp-" + i} value={d} onChange={(e) => setDigit(i, e.target.value)} maxLength={1} inputMode="numeric"
                    style={{ width: 48, height: 56, textAlign: "center", fontSize: 22, fontWeight: 700, background: "var(--surface-container-low)", color: "var(--on-surface)", border: `1px solid ${d ? "var(--primary)" : "var(--outline-variant)"}`, borderRadius: "var(--radius-md)", outline: "none", fontFamily: "var(--font-mono)" }} />
                ))}
              </div>
              <Button variant="primary" size="lg" fullWidth onClick={onLogin}>Verificar e ingresar</Button>
              <p style={{ textAlign: "center", margin: "16px 0 0", fontSize: 13, color: "var(--on-surface-variant)" }}>¿No recibiste el código? <a href="#" style={{ color: "var(--primary)", textDecoration: "none" }}>Reenviar</a></p>
            </React.Fragment>
          )}
        </div>
        <p style={{ textAlign: "center", margin: "20px 0 0", fontSize: 11, letterSpacing: "0.1em", textTransform: "uppercase", color: "var(--outline)" }}>© 2024 Activia-Trace · Nexo Academic Systems</p>
      </div>
    </div>
  );
}

Object.assign(window, { LoginScreen });
