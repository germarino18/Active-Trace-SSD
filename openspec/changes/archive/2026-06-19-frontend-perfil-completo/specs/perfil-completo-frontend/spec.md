## ADDED Requirements

### Requirement: Profile page loads real data from API on mount

The system SHALL call `GET /api/v1/perfil` when `ProfilePage` mounts and populate all form fields with the returned data. While loading, form inputs SHALL be disabled. On error, the page SHALL display an error state with a retry option.

#### Scenario: Successful profile load
- **WHEN** a user navigates to the Profile page
- **THEN** the page calls `GET /api/v1/perfil` and pre-fills `nombre`, `apellidos`, `email`, `cuil`, `dni`, `banco`, `cbu`, `alias_cbu`, `regional`, `legajo_profesional`, and `facturador` with the returned values

#### Scenario: Loading state disables inputs
- **WHEN** the profile data fetch is in progress
- **THEN** all form inputs are disabled and a loading indicator is visible

#### Scenario: Fetch error shows error state
- **WHEN** `GET /api/v1/perfil` returns a non-2xx response
- **THEN** the page displays an error message and a button to retry the fetch

### Requirement: Profile page displays all F11.1 fields

The system SHALL render the following fields in the profile form, split across two sections — "Información personal" and "Datos bancarios":

**Información personal section**: `nombre` (editable), `apellidos` (editable), `email` (read-only), `cuil` (read-only), `dni` (editable), `regional` (editable), `legajo_profesional` (editable).

**Datos bancarios section**: `banco` (editable), `cbu` (editable), `alias_cbu` (editable), `modalidad_cobro` selector (editable, maps to `facturador: boolean`).

#### Scenario: CUIL rendered as read-only
- **WHEN** the user views the Profile page
- **THEN** the `cuil` field is visible but cannot be focused or edited, regardless of editing mode

#### Scenario: Email rendered as read-only
- **WHEN** the user views the Profile page
- **THEN** the `email` field is visible but cannot be focused or edited

#### Scenario: Modalidad de cobro selector maps to facturador
- **WHEN** the user selects "Factura" in the modalidad selector
- **THEN** the PATCH request body includes `facturador: true`
- **WHEN** the user selects "Liquidación"
- **THEN** the PATCH request body includes `facturador: false`

### Requirement: Profile form submits PATCH on save

The system SHALL call `PATCH /api/v1/perfil` with the changed editable fields when the user clicks "Guardar cambios" within a section. The request body SHALL NOT include `cuil`, `email`, or `id`. On success, the form SHALL exit edit mode and display a success banner. On error, the form SHALL remain in edit mode and display the API error message.

#### Scenario: Successful save
- **WHEN** the user edits `banco` to "Nación" and clicks "Guardar cambios"
- **THEN** `PATCH /api/v1/perfil` is called with `{"banco": "Nación"}` and a success message appears

#### Scenario: CUIL excluded from PATCH body
- **WHEN** the user submits the form
- **THEN** the PATCH request body does not contain the `cuil` field

#### Scenario: API error shown inline
- **WHEN** `PATCH /api/v1/perfil` returns 422
- **THEN** the error message from the API response is displayed below the submit button and the form stays in edit mode

### Requirement: Extended Zod schema validates new fields

The profile form schema SHALL validate: `nombre` and `apellidos` as non-empty strings; `dni` as optional string of 7–8 digits; `cbu` as optional string of exactly 22 digits; `alias_cbu` as optional string matching `[a-zA-Z0-9.\-]{6,20}`; `banco` as optional string max 100 chars; `regional` as optional string max 100 chars; `legajo_profesional` as optional string max 50 chars.

#### Scenario: Invalid CBU rejected client-side
- **WHEN** the user enters a CBU that is not 22 digits
- **THEN** the form shows a validation error "El CBU debe tener 22 dígitos" before submitting

#### Scenario: Valid partial update accepted
- **WHEN** the user submits the form with only `banco` filled (all other optional fields empty)
- **THEN** no Zod validation error is raised and the PATCH request proceeds

### Requirement: Independent edit mode per section

Each data section ("Información personal", "Datos bancarios") SHALL have its own independent "Editar" / "Cancelar" + "Guardar cambios" controls. Activating edit mode in one section SHALL NOT affect the other section's state.

#### Scenario: Sections are independently editable
- **WHEN** the user clicks "Editar" on "Información personal"
- **THEN** only the personal fields become editable; "Datos bancarios" fields remain read-only

#### Scenario: Cancel restores original values
- **WHEN** the user enters edit mode, changes `banco`, then clicks "Cancelar"
- **THEN** `banco` reverts to the value received from the last API fetch and edit mode closes
