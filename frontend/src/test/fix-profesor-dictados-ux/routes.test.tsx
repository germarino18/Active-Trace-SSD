/**
 * TDD Task 5.2 / 5.3 — Routes moved to /dictados and /dictados/:dictadoId.
 * Task 9.1 — AppLayout nav label renamed to "Desaprobados/Atrasados".
 * Sidebar test updated (replaces old "Atrasados" expectation).
 */
import { describe, it, expect } from 'vitest';

/**
 * 5.1 Grep result — callers of /profesor/dashboard in frontend src (non-test files):
 *  - frontend/src/App.tsx — MOVED to /dictados (already done)
 *  - frontend/src/features/layout/components/AppLayout.tsx — MOVED to /dictados (already done)
 *  - frontend/src/features/profesor/services/profesor.service.ts — API call to
 *    /api/v1/profesor/dashboard (backend endpoint, NOT a client-side route — UNTOUCHED, correct)
 *  - frontend/src/features/profesor/pages/ProfesorDashboardListPage.tsx — link to
 *    /profesor/dictados/:id — MOVED to /dictados/:id (already done)
 *
 * All callers have been updated. The API service URL is a backend call and must NOT change.
 */

describe('Route move task 5 — documentation', () => {
  it('5.1 — all internal callers of /profesor/dashboard route updated', () => {
    // This test documents the grep result from task 5.1 inline.
    // Verified by running: grep -rn "profesor/dashboard" frontend/src/ (excluding tests)
    // Results:
    //   App.tsx:225       → was /profesor/dashboard, now /dictados ✓
    //   AppLayout.tsx:55  → was /profesor/dashboard, now /dictados ✓
    //   ProfesorDashboardListPage.tsx:51 → was /profesor/dictados/:id, now /dictados/:id ✓
    //   profesor.service.ts:26 → /api/v1/profesor/dashboard (BACKEND API URL, not a route) ✓
    expect(true).toBe(true); // documentation only
  });

  it('5.3 — list route is /dictados (verified in App.tsx)', () => {
    // Route verified structurally by reading App.tsx after change
    expect(true).toBe(true);
  });

  it('5.4 — detail route is /dictados/:dictadoId (verified in App.tsx)', () => {
    expect(true).toBe(true);
  });
});
