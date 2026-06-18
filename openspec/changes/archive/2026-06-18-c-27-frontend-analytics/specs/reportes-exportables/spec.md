## ADDED Requirements

### Requirement: Frontend — Exportar dashboard a PDF

The system SHALL allow exporting the visible dashboard content to PDF using `html2canvas` + `jsPDF`.

**Trigger**: Button "Exportar PDF" in each dashboard section (KPI section, chart section, prediction table section) and a global "Exportar todo como PDF" button in the header.

**Content included**:
- All visible charts (current filter state)
- KPI cards
- Prediction table (if visible)
- Footer with: "Generado el {fecha} | Filtros aplicados: {lista de filtros activos}"

**Implementation**: Capture the dashboard container DOM node with `html2canvas({ scale: 2 })`, then add the captured image to a new `jsPDF` document (A4, landscape for charts, portrait for tables).

#### Scenario: Click "Exportar PDF" exports current dashboard
- **WHEN** user clicks "Exportar PDF"
- **THEN** a PDF file downloads with the current dashboard state, filter metadata, and generation timestamp

#### Scenario: PDF includes filter context
- **WHEN** filters are active before export
- **THEN** the PDF footer lists which filters were applied

#### Scenario: Shows loading indicator during export
- **WHEN** export is processing
- **THEN** button shows a spinner and is disabled until complete

### Requirement: Frontend — Exportar datos tabulares a Excel

The system SHALL allow exporting the prediction table data to `.xlsx` format using the `xlsx` library (SheetJS).

**Trigger**: Button "Exportar Excel" above the prediction table.

**Content**: All rows currently displayed in the table (post-filter), with columns: Alumno, Materia, Promedio, Atrasos, Riesgo.

**File name**: `prediccion-abandono-{YYYY-MM-DD}.xlsx`

#### Scenario: Click "Exportar Excel" downloads .xlsx
- **WHEN** user clicks "Exportar Excel"
- **THEN** a `.xlsx` file downloads with the current table data

#### Scenario: Empty table shows disabled button
- **WHEN** prediction table has no rows
- **THEN** "Exportar Excel" button is disabled

#### Scenario: Export uses current filter state
- **WHEN** filters are applied
- **THEN** the exported Excel only includes rows matching the current filters
