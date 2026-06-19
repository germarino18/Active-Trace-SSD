## ADDED Requirements

### Requirement: Login con diseño Obsidian
La pantalla de login SHALL implementarse con el UI kit `ui_kits/activia-trace/` del DS. El formulario MUST incluir campos email, contraseña y tenant, botón de submit con estado de carga, y enlace a recupero de contraseña. Los errores de credenciales SHALL mostrarse inline bajo el formulario, no en alertas del navegador.

#### Scenario: Submit con credenciales válidas
- **WHEN** el usuario completa email, contraseña y tenant y hace submit
- **THEN** si el backend responde con token, redirige a `/dashboard`

#### Scenario: Submit con credenciales inválidas
- **WHEN** el backend responde con error de autenticación
- **THEN** se muestra mensaje de error en español debajo del formulario, el formulario permanece visible

#### Scenario: Requiere 2FA
- **WHEN** el backend responde con `requires_2fa: true`
- **THEN** se muestra el componente de desafío 2FA sin navegar a otra ruta

#### Scenario: Estado de carga
- **WHEN** el submit está en progreso
- **THEN** el botón muestra spinner y está deshabilitado

---

### Requirement: Pantalla 2FA
La pantalla de segundo factor SHALL mostrar un campo de código OTP de 6 dígitos con teclado numérico. MUST incluir feedback de error cuando el código es incorrecto y opción de cancelar y volver al login.

#### Scenario: Código correcto
- **WHEN** el usuario ingresa un código OTP válido
- **THEN** el sistema autentica y redirige a `/dashboard`

#### Scenario: Código incorrecto
- **WHEN** el usuario ingresa un código OTP inválido
- **THEN** se muestra error inline y el campo se limpia para reintento

---

### Requirement: Recupero y reset de contraseña
Las pantallas de `ForgotPassword` y `ResetPassword` SHALL seguir la identidad visual Obsidian. `ForgotPassword` MUST tener solo el campo email. `ResetPassword` MUST validar que las dos contraseñas coincidan antes del submit.

#### Scenario: Solicitud de recupero exitosa
- **WHEN** el usuario envía su email en ForgotPassword
- **THEN** se muestra confirmación de que el email fue enviado (aunque el email no exista — seguridad)

#### Scenario: Reset con contraseñas no coincidentes
- **WHEN** el usuario ingresa contraseñas distintas en ResetPassword
- **THEN** se muestra error de validación antes de hacer cualquier request al backend
