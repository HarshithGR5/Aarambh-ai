# Aarambh AI — India's Developmental Digital Twin Platform

> AI-powered child development tracking for India's 1.36 million Anganwadi workers, CDPO officers, health workers, and state administrators.

[![TypeScript](https://img.shields.io/badge/TypeScript-5.9-blue?logo=typescript)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## What is Aarambh AI?

India has **158 million children under 6** serviced by 1.36 million Anganwadi centres (AWCs). Developmental delays often go undetected because frontline workers lack tools to observe, record, and escalate systematically.

Aarambh AI solves this with:

- A **Developmental Digital Twin** — a living AI profile of each child across 6 NEP 2020 domains
- **Voice observation** in any Indian language — no typing required
- **PDRS scoring** (0–100, GREEN/AMBER/RED) at child, AWC, block, and district level
- **Automated referral letters** matched to government schemes (RBSK, NPPCD, DEIC)
- **Role-tailored dashboards** from field worker to state officer

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Tech Stack](#tech-stack)
- [Monorepo Structure](#monorepo-structure)
- [User Roles & Access](#user-roles--access)
- [Key Features](#key-features)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Database](#database)
- [API Reference](#api-reference)
- [Authentication Flow](#authentication-flow)
- [AI Features](#ai-features)
- [Development Notes](#development-notes)
- [Deployment](#deployment)
- [Roadmap](#roadmap)
- [Contributing](#contributing)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Clients                               │
│   AWW Mobile (React)  ·  CDPO Dashboard  ·  State Officer   │
└────────────────┬────────────────────────────────────────────┘
                 │  HTTP / REST
┌────────────────▼────────────────────────────────────────────┐
│              Vite + React Frontend (port $PORT)              │
│   Wouter routing  ·  TanStack Query  ·  Zustand store        │
│   /api  →  proxy  →  Express API Server (port 5000)          │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│              Express 5 API Server (TypeScript)               │
│   JWT auth middleware  ·  Drizzle ORM  ·  Zod validation     │
│   /api/v1/auth  ·  /api/v1/children  ·  /api/v1/dashboard   │
└──────┬─────────────────────┬───────────────────────────────┘
       │                     │
┌──────▼──────┐    ┌─────────▼──────────────────────────────┐
│ PostgreSQL  │    │          OpenAI API                      │
│ (Drizzle)   │    │  GPT-4o · Whisper · Vision              │
└─────────────┘    └─────────────────────────────────────────┘
```

### Data flow for a voice observation

1. AWW taps the mic button on mobile
2. Audio streamed to `/api/v1/observations/voice`
3. Whisper transcribes → multilingual text
4. GPT-4o extracts developmental markers (domain, severity, context)
5. Observation saved; PDRS score recalculated for child
6. Child risk level updated (GREEN / AMBER / RED)
7. CDPO dashboard reflects updated block-level risk distribution

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 19, Vite 6, Tailwind CSS v4, Wouter, TanStack Query v5, Zustand v5 |
| **API Server** | Express 5, TypeScript, Drizzle ORM, Zod v4 |
| **Database** | PostgreSQL 16 |
| **Auth** | Phone + OTP, JWT (cookie + Zustand persist) |
| **AI** | OpenAI GPT-4o (text + vision), Whisper (voice transcription) |
| **Validation** | Zod v4, drizzle-zod |
| **Package Manager** | pnpm workspaces (monorepo) |
| **Language** | TypeScript 5.9 throughout |
| **Fonts** | Inter, Plus Jakarta Sans |

---

## Monorepo Structure

```
/
├── artifacts/
│   ├── aarambh-ai/               # Vite + React frontend
│   │   └── src/
│   │       ├── components/
│   │       │   ├── aww/          # AWW worker mobile components
│   │       │   ├── dashboard/    # CDPO / admin dashboard widgets
│   │       │   ├── ddt/          # Developmental Digital Twin visuals
│   │       │   ├── layouts/      # AWWLayout, DashboardLayout
│   │       │   ├── shared/       # EmptyState, LoadingSpinner, etc.
│   │       │   └── ui/           # shadcn/ui primitives
│   │       ├── lib/
│   │       │   ├── api.ts        # Axios API clients per domain
│   │       │   ├── store.ts      # Zustand stores (auth, UI)
│   │       │   ├── types.ts      # All TypeScript interfaces
│   │       │   └── utils.ts      # formatAge, getRiskBg, DOMAIN_META
│   │       ├── pages/
│   │       │   ├── Landing.tsx
│   │       │   ├── Login.tsx
│   │       │   ├── aww/          # Home, Children, ChildDetail, Observe, etc.
│   │       │   └── dashboard/    # Overview, AWCs, District, Referrals, Reports
│   │       ├── App.tsx           # Role-based routing
│   │       └── index.css         # Tailwind v4 theme (brand colors, CSS vars)
│   │
│   └── api-server/               # Express 5 REST API
│       └── src/
│           ├── routes/           # auth, children, observations, referrals, dashboard
│           ├── middleware/       # JWT auth, role guards
│           ├── db/               # Drizzle schema + connection
│           └── index.ts          # Server entry
│
├── packages/
│   └── db/                       # Shared Drizzle schema package
│       └── src/schema.ts
│
├── .migration-backup/
│   ├── frontend/                 # Original Next.js 14 frontend (reference)
│   └── backend/                  # Original FastAPI (Python) backend (reference)
│
└── package.json                  # pnpm workspace root
```

---

## User Roles & Access

Aarambh AI has **5 distinct roles**, each with a tailored view and permissions:

### 1. AWW — Anganwadi Worker
**Login:** Phone + OTP → Redirects to `/home`

The primary field user. Uses the **mobile-optimized** app (max-width 512px, bottom nav).

| Feature | Details |
|---|---|
| Child registry | Register new children (name, DOB, guardian, village) |
| Voice observation | Record 10–30s audio in Hindi/Kannada/Telugu; AI transcribes and extracts markers |
| Milestone tracker | NCERT/WHO milestone checklist per age group |
| Drawing analysis | Upload a child's drawing; GPT-4 Vision scores cognitive/creative domains |
| Referral generation | One-tap referral letter to RBSK/NPPCD/DEIC with AI scheme matching |
| Attendance | Mark daily attendance for all enrolled children |

---

### 2. CDPO — Child Development Project Officer
**Login:** Phone + OTP → Redirects to `/overview`

Block-level supervisor. Uses the **desktop dashboard** (sidebar + content area).

| Page | Details |
|---|---|
| `/overview` | Total children, AWC count, referral completion %, risk distribution (G/A/R) |
| `/awcs` | AWC-by-AWC breakdown — PDRS score, active AWW, last activity |
| `/referrals` | All block referrals — status tracking, scheme, date |
| `/reports` | Bar charts for risk distribution, referral trends, AWC performance |
| `/district` | District heatmap (AWC locations color-coded by risk level) |

---

### 3. HEALTH_WORKER — RBSK Health Worker
**Login:** Phone + OTP → Redirects to `/referrals`

Medical professional. Receives referrals from AWCs and tracks health outcomes.

| Feature | Details |
|---|---|
| `/referrals` | View all referred children, update assessment status |
| Child records | Read-only access to child developmental profile |

---

### 4. STATE_OFFICER — State Programme Officer
**Login:** Phone + OTP → Redirects to `/district`

District and state level analytics. No operational write access.

| Feature | Details |
|---|---|
| `/district` | Multi-AWC heatmap with PDRS score overlays |
| `/reports` | Aggregate district-level analytics |

---

### 5. ADMIN — System Administrator
**Login:** Phone + OTP → Redirects to `/overview`

Full system access.

| Feature | Details |
|---|---|
| All dashboard pages | Full read/write across all blocks |
| User management | Create/deactivate users, assign roles and districts |
| Scheme database | Maintain RBSK, NPPCD, DEIC scheme eligibility criteria |
| Master data | AWC register, village lists, district hierarchy |

---

## Key Features

### Developmental Digital Twin (DDT)

Each child has a **PDRS profile** across 6 domains (NEP 2020 aligned):

| Domain | Code | Description |
|---|---|---|
| Motor | MOT | Gross + fine motor skills |
| Cognitive | COG | Problem solving, attention, memory |
| Language | LAN | Receptive + expressive communication |
| Social-Emotional | SOC | Relationships, self-regulation |
| Aesthetic | AES | Creative arts, drawing, music |
| Wellbeing | WEL | Nutrition, health, sleep |

Each domain scored 0–100. Composite = weighted average. Risk:
- **GREEN** ≥ 70 — on track
- **AMBER** 50–69 — monitor closely
- **RED** < 50 — immediate referral recommended

### Voice Observation Engine

```
AWW speaks → Whisper (multilingual) → GPT-4o → structured JSON
{
  domain: "Language",
  observation_text: "...",
  severity: "MODERATE",
  extracted_markers: ["no two-word phrases at 24m", "prefers gestures"],
  confidence: 0.87
}
```

Supports: Hindi, Kannada, Telugu, Tamil, Marathi, Bengali, Gujarati, and 15+ more.

### Smart Referral Generation

When PDRS drops below threshold or AWW flags a concern:

1. System queries the scheme database (RBSK / NPPCD / DEIC criteria)
2. Matches child profile to eligible schemes
3. GPT-4o drafts a pre-filled referral letter (English + regional language)
4. AWW reviews, one-tap submit
5. Letter PDF generated with child photo, PDRS breakdown, recommended schemes

---

## Getting Started

### Prerequisites

- Node.js 20+
- pnpm 9+
- PostgreSQL 16
- OpenAI API key (for AI features)

### 1. Clone the repository

```bash
git clone https://github.com/your-org/aarambh-ai.git
cd aarambh-ai
```

### 2. Install dependencies

```bash
pnpm install
```

### 3. Set up environment variables

```bash
cp .env.example .env
# Edit .env with your values (see Environment Variables section)
```

### 4. Set up the database

```bash
# Create the database
createdb aarambh_ai

# Push schema
pnpm --filter @workspace/db run push

# (Optional) Seed demo data
pnpm --filter @workspace/api-server run seed
```

### 5. Run in development

```bash
# Terminal 1: API server
pnpm --filter @workspace/api-server run dev

# Terminal 2: Frontend
pnpm --filter @workspace/aarambh-ai run dev
```

The app will be available at `http://localhost:5173` (or the port assigned by your environment).

---

## Environment Variables

Create a `.env` file at the repo root:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/aarambh_ai

# JWT
JWT_SECRET=your-super-secret-jwt-key-min-32-chars
JWT_EXPIRY=7d

# OpenAI (required for voice observation, drawing analysis, referral generation)
OPENAI_API_KEY=sk-...

# Optional: SMS gateway for OTP
SMS_API_KEY=
SMS_SENDER_ID=AARAMB

# App
NODE_ENV=development
PORT=5000
```

> **Note:** In development, if `SMS_API_KEY` is not set, OTPs are logged to the API server console.

---

## Database

Schema managed with **Drizzle ORM** in `packages/db/src/schema.ts`.

### Core tables

| Table | Description |
|---|---|
| `users` | All users (AWW, CDPO, HEALTH_WORKER, STATE_OFFICER, ADMIN) |
| `children` | Child registry — name, DOB, guardian, AWC assignment |
| `observations` | Voice/text observations linked to a child and domain |
| `pdrs_scores` | PDRS scores per domain per child, timestamped |
| `referrals` | Referral records — scheme, status, letter PDF URL |
| `awcs` | AWC register — name, village, district, assigned AWW |
| `attendance` | Daily child attendance records |
| `schemes` | Government scheme database (RBSK, NPPCD, DEIC criteria) |
| `milestones` | NCERT/WHO milestone definitions per age bucket |

### Useful commands

```bash
# Push schema changes to DB
pnpm --filter @workspace/db run push

# Generate migration SQL (for production deploys)
pnpm --filter @workspace/db run generate

# Open Drizzle Studio (visual DB browser)
pnpm --filter @workspace/db run studio
```

---

## API Reference

Base URL: `http://localhost:5000/api/v1`

Interactive docs: `http://localhost:5000/api/v1/docs`

### Auth

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/request-otp` | Send OTP to phone number |
| `POST` | `/auth/verify-otp` | Verify OTP, receive JWT |
| `GET` | `/auth/me` | Get current user profile |
| `POST` | `/auth/logout` | Invalidate session |

### Children

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/children` | List children (AWW: own AWC only) |
| `POST` | `/children` | Register a new child |
| `GET` | `/children/:id` | Child profile + latest PDRS |
| `PUT` | `/children/:id` | Update child record |
| `POST` | `/children/:id/generate-ddt` | Trigger AI DDT synthesis |

### Observations

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/observations/voice` | Submit voice recording for AI processing |
| `POST` | `/observations/text` | Submit text observation |
| `GET` | `/observations/:childId` | List observations for a child |

### Dashboard

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/dashboard/overview` | Global stats |
| `GET` | `/dashboard/cdpo` | Block-level CDPO summary |
| `GET` | `/dashboard/heatmap/:districtId` | AWC heatmap data |

### Referrals

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/referrals` | List referrals (filtered by role) |
| `POST` | `/referrals` | Create referral with AI letter generation |
| `PATCH` | `/referrals/:id/status` | Update referral status |

---

## Authentication Flow

```
┌──────────┐        POST /auth/request-otp       ┌───────────┐
│  Client  │  ─────────────────────────────────►  │ API Server│
│          │                                       │           │
│          │  ◄─────────────────────────────────── │ 200 OK    │
│          │     { message: "OTP sent" }            │ (OTP →    │
│          │                                       │  SMS/log) │
│          │        POST /auth/verify-otp          │           │
│          │  ─────────────────────────────────►  │           │
│          │     { phone, otp }                    │           │
│          │                                       │  Verify   │
│          │  ◄─────────────────────────────────── │  Sign JWT │
│          │     { user, access_token }            │           │
└──────────┘                                       └───────────┘

Token storage:
- Zustand persist (localStorage key: "aarambh-auth") → React state
- js-cookie ("aarambh_token") → Axios Authorization header interceptor

Role → Redirect:
  AWW           → /home
  CDPO          → /overview
  HEALTH_WORKER → /referrals
  STATE_OFFICER → /district
  ADMIN         → /overview
```

---

## AI Features

### Voice Observation (Whisper + GPT-4o)

```typescript
// POST /api/v1/observations/voice
// Body: FormData { audio: File, child_id: number }

// Pipeline:
// 1. Whisper: audio → transcript (any Indian language)
// 2. GPT-4o: transcript → structured JSON
//    { domain, severity, markers[], confidence, observation_text }
// 3. PDRS recalculated for child
```

### Drawing Analysis (GPT-4 Vision)

```typescript
// POST /api/v1/observations/drawing
// Body: FormData { image: File, child_id: number, age_months: number }

// GPT-4 Vision scores:
// - Fine motor control (line quality, grip control)
// - Cognitive representation (figure complexity)
// - Aesthetic expression (color use, composition)
// Returns: domain scores + narrative feedback
```

### DDT Synthesis (GPT-4o)

```typescript
// POST /api/v1/children/:id/generate-ddt
// Aggregates all observations → AI narrative portrait
// Outputs: 6-domain summary, school readiness prediction, parent recommendations
```

### Referral Letter (GPT-4o)

```typescript
// POST /api/v1/referrals
// Input: child_id, concern, scheme_ids[]
// Output: AI-drafted letter (formal government format)
//   - Child details pre-filled
//   - PDRS scores attached
//   - Referring AWW + supervisor signature block
//   - Scheme-specific eligibility rationale
```

---

## Development Notes

### Tailwind v4

This project uses Tailwind v4 with `@theme inline` in CSS, **not** `tailwind.config.js`. Brand colors are in `artifacts/aarambh-ai/src/index.css`:

```css
@theme inline {
  --color-brand-50: oklch(97% 0.015 220);
  /* ... brand-100 through brand-950 */
}
```

### Routing (Wouter, not React Router)

```typescript
// useLocation returns [pathname, navigate]
const [pathname, navigate] = useLocation();

// NOT: const pathname = usePathname(); // that's Next.js
```

### Badge variants

Custom variants `green`, `amber`, `red`, `blue`, `purple` are added to `src/components/ui/badge.tsx`. Always check they're defined before using.

### Auth token pattern

```typescript
// Token lives in TWO places intentionally:
// 1. Zustand (localStorage persist) — for React state / UI
// 2. js-cookie — for Axios interceptor (reads cookie, not Zustand)
// Both must be set on login, both cleared on logout.
```

### API offline fallback

All dashboard pages (`Overview`, `AWCs`, `Reports`, `District`) detect `isError: true` from TanStack Query and fall back to `DEMO_*` constants. An amber warning banner is shown. This lets the frontend be demoed without a running backend.

---

## Deployment

### Frontend

```bash
pnpm --filter @workspace/aarambh-ai run build
# Output: artifacts/aarambh-ai/dist/
# Serve with any static host (Vercel, Netlify, Nginx)
```

### API Server

```bash
pnpm --filter @workspace/api-server run build
pnpm --filter @workspace/api-server run start
# Requires DATABASE_URL + JWT_SECRET + OPENAI_API_KEY in environment
```

### Docker (recommended for production)

```dockerfile
# See docker-compose.yml for full setup
# Services: postgres, api-server, frontend (nginx)
```

### Environment checklist before go-live

- [ ] `DATABASE_URL` points to production Postgres
- [ ] `JWT_SECRET` is ≥ 32 chars, randomly generated, never committed
- [ ] `OPENAI_API_KEY` is set (AI features will silently degrade without it)
- [ ] `NODE_ENV=production`
- [ ] SMS gateway configured for real OTPs (remove dev fallback)
- [ ] HTTPS enforced (JWT in cookie requires `Secure` flag)
- [ ] Database migrations run: `pnpm --filter @workspace/db run migrate`

---

## Roadmap

- [ ] **Offline mode** — IndexedDB sync for AWW field use in low-connectivity areas
- [ ] **WhatsApp bot** — Submit observations via WhatsApp voice messages
- [ ] **VITS TTS** — AI reads out milestones and recommendations in regional languages
- [ ] **Photo milestones** — AWW photos tagged with milestone, AI confirms achievement
- [ ] **Programme comparison** — District vs. national benchmark analytics
- [ ] **Parent app** — View-only child profile for guardians with translated summaries
- [ ] **Federated learning** — Privacy-preserving model improvement across states

---

## Contributing

1. Fork the repo and create a feature branch (`git checkout -b feat/your-feature`)
2. Run typechecks before committing: `pnpm run typecheck`
3. Follow the existing file structure (see [Monorepo Structure](#monorepo-structure))
4. Do not commit `.env`, secrets, or `node_modules`
5. Open a PR against `main` with a clear description

---

## License

MIT © 2025 Aarambh AI / ICDS Digital Initiative

---

<div align="center">
  <strong>Built for India's children. Built with ❤️ by the ICDS Digital team.</strong>
  <br />
  RBSK · NPPCD · DEIC · NEP 2020 Aligned
</div>
