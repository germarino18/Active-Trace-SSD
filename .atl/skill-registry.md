# Skill Registry

**Delegator use only.** Any agent that launches sub-agents reads this registry to resolve compact rules, then injects them directly into sub-agent prompts. Sub-agents do NOT read this registry or individual SKILL.md files.

## User Skills (Framework — OpenCode)

| Trigger | Skill | Path |
|---------|-------|------|
| When initializing a project, setting up foundation, or running openspec init | openspec-init | C:\Users\German\.config\opencode\skills\openspec-init\SKILL.md |
| When creating, generating, or updating project knowledge base | kb-creator | C:\Users\German\.config\opencode\skills\kb-creator\SKILL.md |
| When creating, generating, or updating CHANGES.md / roadmap | roadmap-generator | C:\Users\German\.config\opencode\skills\roadmap-generator\SKILL.md |
| When starting a new proposal or feature request | openspec-proposal | C:\Users\German\.config\opencode\skills\openspec-proposal\SKILL.md |
| When creating or updating a technical design document | openspec-design | C:\Users\German\.config\opencode\skills\openspec-design\SKILL.md |
| When writing or updating specifications | openspec-spec | C:\Users\German\.config\opencode\skills\openspec-spec\SKILL.md |
| When creating implementation task checklists | openspec-tasks | C:\Users\German\.config\opencode\skills\openspec-tasks\SKILL.md |
| When implementing approved change proposals | openspec-apply | C:\Users\German\.config\opencode\skills\openspec-apply\SKILL.md |
| When archiving completed changes | openspec-archive | C:\Users\German\.config\opencode\skills\openspec-archive\SKILL.md |
| When verifying implementation matches specs | openspec-verify | C:\Users\German\.config\opencode\skills\openspec-verify\SKILL.md |
| When exploring ideas or investigating problems | openspec-explore | C:\Users\German\.config\opencode\skills\openspec-explore\SKILL.md |
| When onboarding to OPSX workflow | openspec-onboard | C:\Users\German\.config\opencode\skills\openspec-onboard\SKILL.md |
| When finding or discovering skills | find-skill | C:\Users\German\.config\opencode\skills\find-skill\SKILL.md |
| When creating or optimizing skills | skill-creator | C:\Users\German\.config\opencode\skills\skill-creator\SKILL.md |
| When registering or synchronizing skill registry | skill-registry | C:\Users\German\.config\opencode\skills\skill-registry\SKILL.md |
| When running foundation flow from scratch | jr-orchestrator | C:\Users\German\.config\opencode\skills\jr-orchestrator\SKILL.md |
| When doing adversarial review / judgment day | judgment-day | C:\Users\German\.config\opencode\skills\judgment-day\SKILL.md |
| When generating AGENTS.md / CLAUDE.md | agents-md-generator | C:\Users\German\.config\opencode\skills\agent-instruction\SKILL.md |

## Project Skills (`.agents/skills/` — active-trace-ssd)

| Trigger | Skill | Path |
|---------|-------|------|
| When creating CRUD pages in Dashboard | dashboard-crud-page | E:\Facultad German\Active-Trace-SSD\.agents\skills\dashboard-crud-page\SKILL.md |
| When creating UI components with Tailwind | tailwind-design-system | E:\Facultad German\Active-Trace-SSD\.agents\skills\tailwind-design-system\SKILL.md |
| When optimizing React performance | vercel-react-best-practices | E:\Facultad German\Active-Trace-SSD\.agents\skills\vercel-react-best-practices\SKILL.md |
| When writing React components or researching React APIs | react-expert | E:\Facultad German\Active-Trace-SSD\.agents\skills\react-expert\SKILL.md |
| When implementing TanStack Query data fetching | tanstack-query | E:\Facultad German\Active-Trace-SSD\.agents\skills\tanstack-query\SKILL.md |
| When building forms with validation | react-hook-form-zod | E:\Facultad German\Active-Trace-SSD\.agents\skills\react-hook-form-zod\SKILL.md |
| When writing advanced TypeScript types | typescript-advanced | E:\Facultad German\Active-Trace-SSD\.agents\skills\typescript-advanced\SKILL.md |
| When writing async Python / FastAPI code | async-python-patterns | E:\Facultad German\Active-Trace-SSD\.agents\skills\async-python-patterns\SKILL.md |
| When creating FastAPI endpoints / ABM | fastapi-templates | E:\Facultad German\Active-Trace-SSD\.agents\skills\fastapi-templates\SKILL.md |
| When designing PostgreSQL schemas | postgresql-table-design | E:\Facultad German\Active-Trace-SSD\.agents\skills\postgresql-table-design\SKILL.md |
| When writing Python tests with pytest | python-testing-patterns | E:\Facultad German\Active-Trace-SSD\.agents\skills\python-testing-patterns\SKILL.md |
| When implementing features with TDD | test-driven-development | E:\Facultad German\Active-Trace-SSD\.agents\skills\test-driven-development\SKILL.md |
| When creating project knowledge base | kb-creator | E:\Facultad German\Active-Trace-SSD\.agents\skills\kb-creator\SKILL.md |

## Compact Rules

Pre-digested rules per skill. Delegators copy matching blocks into sub-agent prompts as `## Project Standards (auto-resolved)`.

### react-expert
- Skepticism mandate: Treat source material as sole authority, not LLM training knowledge
- Flag discrepancies when findings contradict prior understanding
- No web search (no Stack Overflow, blog posts); use GitHub API (`gh`) only
- Research priority: React repo tests → source code → git history → PRs → issues → WG discussions → Flow types → TS types → current docs
- Clone/clone react repo locally to `.claude/react` for research

### tanstack-query
- Use TanStack Query for ALL server state — minimize useEffect/useState for server data
- Structure: `src/api/client.ts` + `src/api/endpoints/*.ts` for calls, `src/hooks/queries/*.ts` + `src/hooks/mutations/*.ts` for hooks
- Configure QueryClient with staleTime (5min default), gcTime (30min), retry: 3, refetchOnWindowFocus: true
- Use `useQuery` for reads, `useMutation` for writes, invalidate queries on mutation success
- Type all query responses and mutation variables with TypeScript generics
- Use `enabled` option for dependent queries, `placeholderData` for skeletons
- Error handling: Use `error` from query result, display user-friendly messages

### react-hook-form-zod
- Single schema approach: define Zod schema → `z.infer` for TS types → `zodResolver` for validation
- Use `useForm<FormData>({ resolver: zodResolver(schema), defaultValues: {...} })`
- For multi-step wizards: use `useForm` per step or `schema.partial()` for multi-step validation
- Dynamic arrays: use `useFieldArray` with `fields.map((field, index) => ...)`
- File uploads: use `z.instanceof(File)` or `z.array(z.instanceof(File))`, NOT `z.any()`
- Controlled components: use `Controller` wrapper or register with `value`/`onChange` props
- Avoid uncontrolled-to-controlled warnings by always providing `defaultValues`

### typescript-advanced
- Use `extends` constraints on generics: `<T extends HasId>` for type-safe generics
- Conditional types: `T extends X ? Y : Z`, use `infer` inside extends for type extraction
- Mapped types: `{ [K in keyof T]: Transform<T[K]> }`, use `as` clause for key remapping
- Template literal types: `` `${Protocol}://${Domain}${Path}` `` for URL/path type patterns
- Brand types: use intersection `type Brand<T, B> = T & { __brand: B }` for nominal typing
- Discriminated unions: use `type Shape = { kind: 'circle'; radius: number } | { kind: 'rect'; w: number; h: number }`
- Utility types: `Partial<T>`, `Required<T>`, `Pick<T,K>`, `Omit<T,K>`, `Record<K,T>`, `Readonly<T>`

### dashboard-crud-page
- Use `useFormModal` hook for create/edit modals, `useConfirmDialog` for delete confirmation
- Use `usePagination` hook for paginated tables
- Use `useActionState` in forms for async submit handling with loading/error states
- Structure: page must include `<DataTable>`, `<FormModal>`, and `<ConfirmDialog>`
- Cascade delete: always ask confirmation showing affected items

### tailwind-design-system
- Use OKLCH color space for CSS custom properties (lightness, chroma, hue)
- Use CVA (class-variance-authority) for component variants (size, intent, etc.)
- Use compound components pattern (Root, Trigger, Content, etc.)
- Responsive grid: use `grid-cols-1 sm:grid-cols-2 lg:grid-cols-3` pattern
- Dark mode: use `dark:` variants on the same element, never separate files
- Animations: use Tailwind's built-in `animate-*` utilities + `transition-*`

### vercel-react-best-practices
- Prefer Server Components by default, add 'use client' only when needed (hooks, browser APIs, interactivity)
- Minimize 'use client' boundaries — push them to leaf components
- Use React.memo sparingly — profile first, memoize only if rendering cost justifies it
- Bundle optimization: dynamic import() for heavy components, next/dynamic for lazy loading
- Use `useId()` for accessible IDs instead of manual counters
- Debounce rapid state updates (scroll, input, resize)

### async-python-patterns
- Use `async def` for all FastAPI endpoints, SQLAlchemy async sessions, and I/O operations
- Use `asyncio.gather()` for concurrent independent tasks, `asyncio.create_task()` for fire-and-forget
- Database: always use `async with session.begin():` for transactional boundaries
- Worker queues: use asyncio.Queue or Redis pub/sub for background job processing
- Never block the event loop with sync I/O — use `asyncio.to_thread()` if unavoidable

### fastapi-templates
- Structure: `routers/` (endpoints only) → `services/` (business logic) → `repositories/` (DB access)
- Use dependency injection for `get_db`, `get_current_user`, `require_permission`
- Error handling: use custom exceptions with middleware, never raw HTTPException in services
- Pydantic v2: all schemas with `ConfigDict(extra='forbid')`, `from_attributes=True` for ORM mode

### postgresql-table-design
- Prefer `UUID` primary keys over serial integers for distributed systems
- Use `TIMESTAMPTZ` for all timestamps, never `TIMESTAMP` without timezone
- Index foreign keys and frequently-queried columns; use partial indexes for filtered queries
- JSONB for dynamic/custom fields, but prefer normalized columns for queryable data
- Use `CHECK` constraints for domain invariants, `EXCLUDE` for overlapping ranges

### python-testing-patterns
- Use `pytest` fixtures for reusable test setup (DB session, auth client, test data factories)
- Use `pytest.mark.parametrize` for testing multiple input/output combinations
- Mock only external services (HTTP, email, Redis), NEVER the database
- Structure tests: `tests/unit/`, `tests/integration/`, `tests/e2e/`

### test-driven-development
- Three Laws: (1) No production code without a failing test, (2) No more test than needed to fail, (3) No more code than needed to pass
- Cycle: RED (failing test) → GREEN (minimum code to pass) → TRIANGULATE (second test case) → REFACTOR (improve without changing behavior)
- Safety net: run existing tests before modifying files, capture baseline
- Always return TDD Cycle Evidence table with results per task

### kb-creator
- Creates 10 canonical files in `knowledge-base/` from vision to open questions
- Silent mode: generate from existing docs/ directory
- Interactive mode: strategic accompaniment, ask questions to fill gaps
- Output: `01_vision` through `10_preguntas_abiertas.md` plus `11_historias_de_usuario.md`

## Project Conventions

| File | Path | Notes |
|------|------|-------|
| AGENTS.md / CLAUDE.md | E:\Facultad German\Active-Trace-SSD\AGENTS.md | Main project instructions — stack, KB, skills, hard rules, governance |
| CHANGES.md | E:\Facultad German\Active-Trace-SSD\CHANGES.md | Implementation roadmap — 24 changes, gates, dependencies |
| knowledge-base/ | E:\Facultad German\Active-Trace-SSD\knowledge-base/ | Domain knowledge — 11 canonical docs |
| docs/ARQUITECTURA.md | E:\Facultad German\Active-Trace-SSD\docs\ARQUITECTURA.md | Technical architecture & ADRs |
| docs/PRD.md | E:\Facultad German\Active-Trace-SSD\docs\PRD.md | Product requirements & RNFs |
