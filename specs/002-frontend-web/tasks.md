# Tasks: Frontend Web Application

**Input**: Design documents from `/specs/002-frontend-web/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Not explicitly requested - test tasks excluded per specification.

**Organization**: Tasks grouped by user story to enable independent implementation. Auth stories (US1, US2) are foundational since task operations require authentication.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1-US8 maps to user stories from spec.md
- All paths relative to `frontend/` directory

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Initialize Next.js project structure and dependencies

- [ ] T001 Create Next.js 16+ project with TypeScript, Tailwind, App Router in frontend/
- [ ] T002 Install dependencies: better-auth, lucide-react in frontend/package.json
- [ ] T003 [P] Create .env.example with NEXT_PUBLIC_API_URL, BETTER_AUTH_SECRET in frontend/.env.example
- [ ] T004 [P] Create .env.local with development values in frontend/.env.local
- [ ] T005 [P] Configure tailwind.config.ts with custom theme in frontend/tailwind.config.ts

**Checkpoint**: `npm run dev` starts without errors

---

## Phase 2: Foundational (Core Library)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Create lib/utils.ts with cn() helper for className merging in frontend/src/lib/utils.ts
- [ ] T007 Create lib/types.ts with User, Task, ApiResponse TypeScript interfaces in frontend/src/lib/types.ts
- [ ] T008 Create lib/api.ts with fetchWithAuth wrapper function in frontend/src/lib/api.ts
- [ ] T009 [P] Add taskApi methods (getTasks, createTask, updateTask, deleteTask) to frontend/src/lib/api.ts
- [ ] T010 [P] Add authApi methods (login, register) to frontend/src/lib/api.ts
- [ ] T011 Create lib/auth.ts with Better Auth configuration in frontend/src/lib/auth.ts
- [ ] T012 Export getSession, signIn, signOut from auth module in frontend/src/lib/auth.ts

**Checkpoint**: API client compiles with proper types

---

## Phase 3: UI Components (Shared Components)

**Purpose**: Build reusable UI components used across multiple stories

- [ ] T013 [P] Create components/ui/Button.tsx with variants (primary, secondary, danger, ghost) in frontend/src/components/ui/Button.tsx
- [ ] T014 [P] Create components/ui/Input.tsx with label and error states in frontend/src/components/ui/Input.tsx
- [ ] T015 [P] Create components/ui/Card.tsx for content containers in frontend/src/components/ui/Card.tsx
- [ ] T016 [P] Create components/ui/Skeleton.tsx for loading states in frontend/src/components/ui/Skeleton.tsx
- [ ] T017 [P] Create components/ui/Label.tsx for form labels in frontend/src/components/ui/Label.tsx

**Checkpoint**: UI components render in isolation

---

## Phase 4: User Story 1 - User Registration (Priority: P1) MVP

**Goal**: Enable visitors to create an account

**Independent Test**: Navigate to /register, fill form, submit, verify redirect to /tasks with authenticated session

### Implementation for US1

- [ ] T018 [P] [US1] Create app/(auth)/layout.tsx with centered card layout in frontend/src/app/(auth)/layout.tsx
- [ ] T019 [US1] Create components/auth/RegisterForm.tsx with email, password, confirmPassword fields in frontend/src/components/auth/RegisterForm.tsx
- [ ] T020 [US1] Add client-side validation for password match in RegisterForm
- [ ] T021 [US1] Add client-side validation for min 8 characters in RegisterForm
- [ ] T022 [US1] Create app/(auth)/register/page.tsx with RegisterForm and link to login in frontend/src/app/(auth)/register/page.tsx
- [ ] T023 [US1] Handle 409 "Email already registered" error inline in RegisterForm
- [ ] T024 [US1] Redirect to /tasks on successful registration in RegisterForm

**Checkpoint**: User can register new account and be redirected to /tasks

---

## Phase 5: User Story 2 - User Login (Priority: P1)

**Goal**: Enable returning users to login

**Independent Test**: Navigate to /login, enter credentials, submit, verify redirect to /tasks

### Implementation for US2

- [ ] T025 [US2] Create components/auth/LoginForm.tsx with email, password fields in frontend/src/components/auth/LoginForm.tsx
- [ ] T026 [US2] Add client-side validation for required fields in LoginForm
- [ ] T027 [US2] Create app/(auth)/login/page.tsx with LoginForm and link to register in frontend/src/app/(auth)/login/page.tsx
- [ ] T028 [US2] Handle 401 "Invalid credentials" error inline in LoginForm
- [ ] T029 [US2] Redirect to /tasks on successful login in LoginForm

**Checkpoint**: User can login and be redirected to /tasks

---

## Phase 6: User Story 3 - View Task Dashboard (Priority: P1)

**Goal**: Display task list for authenticated users

**Independent Test**: Login, navigate to /tasks, verify task list loads with user's tasks only

### Implementation for US3

- [ ] T030 [US3] Create app/tasks/loading.tsx with skeleton placeholders in frontend/src/app/tasks/loading.tsx
- [ ] T031 [US3] Create components/tasks/EmptyState.tsx for when no tasks exist in frontend/src/components/tasks/EmptyState.tsx
- [ ] T032 [US3] Create components/tasks/TaskItem.tsx with checkbox and delete button in frontend/src/components/tasks/TaskItem.tsx
- [ ] T033 [US3] Create components/tasks/TaskList.tsx as client component with initialTasks prop in frontend/src/components/tasks/TaskList.tsx
- [ ] T034 [US3] Create app/tasks/page.tsx as Server Component that fetches tasks in frontend/src/app/tasks/page.tsx
- [ ] T035 [US3] Pass fetched tasks to TaskList client component in page.tsx

**Checkpoint**: Authenticated users can view their task list

---

## Phase 7: User Story 4 - Create Task (Priority: P1)

**Goal**: Allow authenticated users to create new tasks

**Independent Test**: On /tasks, enter title, submit, verify task appears in list

### Implementation for US4

- [ ] T036 [US4] Create components/tasks/TaskForm.tsx with title input and submit button in frontend/src/components/tasks/TaskForm.tsx
- [ ] T037 [US4] Add client-side validation for non-empty title in TaskForm
- [ ] T038 [US4] Call taskApi.createTask on form submit in TaskForm
- [ ] T039 [US4] Clear input field on successful creation in TaskForm
- [ ] T040 [US4] Add TaskForm to app/tasks/page.tsx above task list
- [ ] T041 [US4] Wire onTaskCreated callback to update TaskList state in page.tsx

**Checkpoint**: Users can create tasks that appear immediately in list

---

## Phase 8: User Story 5 - Toggle Task Completion (Priority: P1)

**Goal**: Allow users to mark tasks as complete/incomplete

**Independent Test**: Click task checkbox, verify immediate visual update, verify persists after refresh

### Implementation for US5

- [ ] T042 [US5] Add checkbox click handler in TaskItem.tsx that calls onToggle prop
- [ ] T043 [US5] Implement optimistic update in TaskList.tsx handleToggle function
- [ ] T044 [US5] Call taskApi.updateTask with toggled completed status
- [ ] T045 [US5] Revert optimistic update on API error with error message
- [ ] T046 [US5] Add visual styling for completed tasks (strikethrough, muted colors) in TaskItem

**Checkpoint**: Tasks toggle immediately with rollback on error

---

## Phase 9: User Story 6 - Delete Task (Priority: P2)

**Goal**: Allow users to delete tasks

**Independent Test**: Click delete button on task, verify task removed from list

### Implementation for US6

- [ ] T047 [US6] Add delete button click handler in TaskItem.tsx that calls onDelete prop
- [ ] T048 [US6] Implement optimistic delete in TaskList.tsx handleDelete function
- [ ] T049 [US6] Call taskApi.deleteTask with task ID
- [ ] T050 [US6] Refetch tasks on API error to restore state

**Checkpoint**: Users can delete tasks with immediate removal

---

## Phase 10: User Story 7 - Filter Tasks (Priority: P2)

**Goal**: Allow users to filter tasks by completion status

**Independent Test**: Click filter buttons, verify list updates to show only matching tasks

### Implementation for US7

- [ ] T051 [US7] Create components/tasks/TaskFilter.tsx with All/Active/Completed buttons in frontend/src/components/tasks/TaskFilter.tsx
- [ ] T052 [US7] Add filter state to TaskList.tsx (default: 'all')
- [ ] T053 [US7] Implement filteredTasks computed value based on filter state
- [ ] T054 [US7] Add TaskFilter component to TaskList.tsx above task items
- [ ] T055 [US7] Display task count in TaskFilter component

**Checkpoint**: Filter buttons correctly show/hide tasks by status

---

## Phase 11: User Story 8 - Logout (Priority: P1)

**Goal**: Allow users to end their session

**Independent Test**: Click logout, verify redirect to /login, verify /tasks inaccessible

### Implementation for US8

- [ ] T056 [US8] Create components/auth/LogoutButton.tsx that calls signOut in frontend/src/components/auth/LogoutButton.tsx
- [ ] T057 [US8] Redirect to /login after signOut completes in LogoutButton
- [ ] T058 [US8] Create components/layout/Navbar.tsx with app title and user info in frontend/src/components/layout/Navbar.tsx
- [ ] T059 [US8] Add LogoutButton to Navbar component

**Checkpoint**: Users can logout and are redirected to login

---

## Phase 12: Route Protection (Middleware)

**Purpose**: Implement middleware for auth redirects

- [ ] T060 Create middleware.ts at frontend root with route protection logic in frontend/middleware.ts
- [ ] T061 Define protected routes array (/tasks) in middleware.ts
- [ ] T062 Define auth routes array (/login, /register) in middleware.ts
- [ ] T063 Redirect unauthenticated users to /login from protected routes
- [ ] T064 Redirect authenticated users away from auth pages to /tasks

**Checkpoint**: Routes properly protected

---

## Phase 13: Layout & App Shell

**Purpose**: Complete app layout and root pages

- [ ] T065 Update app/layout.tsx with Navbar for authenticated users in frontend/src/app/layout.tsx
- [ ] T066 Create app/page.tsx that redirects to /tasks or /login in frontend/src/app/page.tsx
- [ ] T067 Create app/error.tsx for error boundary in frontend/src/app/error.tsx
- [ ] T068 Create app/not-found.tsx for 404 page in frontend/src/app/not-found.tsx
- [ ] T069 Update globals.css with Tailwind imports in frontend/src/app/globals.css

**Checkpoint**: App shell complete with proper routing

---

## Phase 14: Polish & Verification

**Purpose**: Final verification and documentation

- [ ] T070 [P] Create frontend/CLAUDE.md with implementation notes in frontend/CLAUDE.md
- [ ] T071 [P] Verify mobile responsiveness at 375px width
- [ ] T072 [P] Verify tablet responsiveness at 768px width
- [ ] T073 [P] Verify desktop responsiveness at 1024px width
- [ ] T074 Run quickstart.md verification checklist
- [ ] T075 Verify all acceptance scenarios from spec.md pass

**Checkpoint**: All tasks complete, frontend verified against specification

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) → Phase 2 (Foundational) → Phase 3 (UI Components)
                                                    ↓
                               ┌────────────────────┴────────────────────┐
                               ↓                                         ↓
                    Phase 4-5 (Auth: US1, US2)              Phase 6-11 (Task Stories)
                               ↓                                         ↓
                    Phase 12 (Middleware)                                │
                               ↓                                         │
                    Phase 13 (Layout)  ←─────────────────────────────────┘
                               ↓
                    Phase 14 (Polish)
```

### User Story Dependencies

| Story | Depends On | Can Parallel With |
|-------|------------|-------------------|
| US1 (Register) | Phase 3 | US2 |
| US2 (Login) | Phase 3 | US1 |
| US3 (View Dashboard) | US1 or US2 | None (needs auth) |
| US4 (Create Task) | US3 | US5 |
| US5 (Toggle Task) | US3 | US4, US6 |
| US6 (Delete Task) | US3 | US5, US7 |
| US7 (Filter Tasks) | US3 | US6 |
| US8 (Logout) | US1 or US2 | US3-US7 |

### Within Each Phase

- Tasks marked [P] can run in parallel
- UI component tasks are all [P]
- Implementation tasks within a story are sequential

---

## Parallel Opportunities

### Phase 1 Parallel
```
T003: .env.example   }
T004: .env.local     } → Run together
T005: tailwind.config}
```

### Phase 2 Parallel
```
T009: taskApi methods  }
T010: authApi methods  } → Run together (different sections)
```

### Phase 3 Parallel (All UI Components)
```
T013: Button.tsx   }
T014: Input.tsx    }
T015: Card.tsx     } → Run together (different files)
T016: Skeleton.tsx }
T017: Label.tsx    }
```

### Phase 14 Parallel
```
T070: CLAUDE.md        }
T071: Mobile verify    }
T072: Tablet verify    } → Run together
T073: Desktop verify   }
```

---

## Implementation Strategy

### MVP First (US1 + US2 + US3 + US4)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: UI Components
4. Complete Phase 4: US1 (Register) - **Users can sign up**
5. Complete Phase 5: US2 (Login) - **Users can login**
6. Complete Phase 6: US3 (View Dashboard) - **Users can see tasks**
7. Complete Phase 7: US4 (Create Task) - **Users can add tasks**
8. **STOP and VALIDATE**: Test core functionality
9. Deploy MVP if needed

### Full Implementation

Continue with:
10. Complete Phase 8: US5 (Toggle)
11. Complete Phase 9: US6 (Delete)
12. Complete Phase 10: US7 (Filter)
13. Complete Phase 11: US8 (Logout)
14. Complete Phase 12: Middleware
15. Complete Phase 13: Layout
16. Complete Phase 14: Polish

### Single Developer Sequence

```
T001-T005 (Setup) → T006-T012 (Foundation) → T013-T017 (UI) → T018-T024 (US1) → T025-T029 (US2) → T030-T035 (US3) → T036-T041 (US4) → T042-T046 (US5) → T047-T050 (US6) → T051-T055 (US7) → T056-T059 (US8) → T060-T064 (Middleware) → T065-T069 (Layout) → T070-T075 (Polish)
```

---

## Task Summary

| Phase | Tasks | Parallel Opportunities | Status |
|-------|-------|------------------------|--------|
| Phase 1: Setup | 5 | 3 | Pending |
| Phase 2: Foundational | 7 | 2 | Pending |
| Phase 3: UI Components | 5 | 5 | Pending |
| Phase 4: US1 Register | 7 | 1 | Pending |
| Phase 5: US2 Login | 5 | 0 | Pending |
| Phase 6: US3 Dashboard | 6 | 0 | Pending |
| Phase 7: US4 Create | 6 | 0 | Pending |
| Phase 8: US5 Toggle | 5 | 0 | Pending |
| Phase 9: US6 Delete | 4 | 0 | Pending |
| Phase 10: US7 Filter | 5 | 0 | Pending |
| Phase 11: US8 Logout | 4 | 0 | Pending |
| Phase 12: Middleware | 5 | 0 | Pending |
| Phase 13: Layout | 5 | 0 | Pending |
| Phase 14: Polish | 6 | 4 | Pending |
| **Total** | **75** | **15** | **Pending** |

---

## Notes

- All task pages require JWT validation (Better Auth handles via cookies)
- User ID comes from JWT, NEVER from request (backend enforces)
- Use optimistic updates for toggle and delete operations
- Return 404 (not 403) for "wrong user" scenarios handled by backend
- Use Server Components by default, Client Components only when interactive
- Commit after each task or logical group
- Test each user story independently before proceeding

---

## User Story to Task Mapping

| User Story | Tasks | Primary Files |
|------------|-------|---------------|
| US1 Registration | T018-T024 | RegisterForm.tsx, register/page.tsx |
| US2 Login | T025-T029 | LoginForm.tsx, login/page.tsx |
| US3 View Dashboard | T030-T035 | TaskList.tsx, TaskItem.tsx, tasks/page.tsx |
| US4 Create Task | T036-T041 | TaskForm.tsx |
| US5 Toggle Task | T042-T046 | TaskItem.tsx, TaskList.tsx |
| US6 Delete Task | T047-T050 | TaskItem.tsx, TaskList.tsx |
| US7 Filter Tasks | T051-T055 | TaskFilter.tsx, TaskList.tsx |
| US8 Logout | T056-T059 | LogoutButton.tsx, Navbar.tsx |

---

## References

- @specs/002-frontend-web/spec.md - Feature specification
- @specs/002-frontend-web/plan.md - Implementation plan
- @specs/002-frontend-web/data-model.md - TypeScript interfaces
- @specs/002-frontend-web/quickstart.md - Setup guide
- @specs/ui/pages.md - Page layouts
- @specs/ui/components.md - Component specifications
