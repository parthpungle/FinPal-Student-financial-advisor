# Building FinPal's Frontend with IBM Bob

FinPal's entire user-facing layer — the landing page, the voice/chat advisor, the
financial dashboard, the design system that ties them together, and the JavaScript
that talks to the API — was designed and implemented with
**[IBM Bob](https://www.ibm.com/products/watsonx/bob)**, IBM's AI software-engineering
agent from the watsonx family.

This document records what Bob actually produced, how it was briefed, and how the
output was verified, so anyone reading the repository can trace the UI back to the
process that created it.

---

## Table of contents

1. [Where the boundary sits](#1-where-the-boundary-sits)
2. [What Bob delivered](#2-what-bob-delivered)
3. [The design system](#3-the-design-system)
4. [Page-by-page breakdown](#4-page-by-page-breakdown)
5. [The API layer](#5-the-api-layer)
6. [Voice capture in the browser](#6-voice-capture-in-the-browser)
7. [Session handling](#7-session-handling)
8. [Accessibility and the performance strip-down](#8-accessibility-and-the-performance-strip-down)
9. [How Bob was briefed and how it delivered](#9-how-bob-was-briefed-and-how-it-delivered)
10. [Verification before hand-off](#10-verification-before-hand-off)
11. [What changed afterwards](#11-what-changed-afterwards)
12. [Takeaways](#12-takeaways)

---

## 1. Where the boundary sits

Bob's remit was the presentation layer. The Python side of FinPal — the FastAPI
service, the conversation orchestrator, the deterministic rules engine, and the Groq
speech pipeline — was built separately and was already running when the frontend work
began.

| Layer | Built with |
|---|---|
| `frontend/index.html`, `app.html`, `dashboard.html` | **IBM Bob** |
| `frontend/styles.css` — full design system | **IBM Bob** |
| `frontend/api.js` — API client + browser helpers | **IBM Bob** |
| `backend/app/**` — FastAPI, orchestrator, rules engine, STT/TTS | Built outside Bob |

This split is stated in three places in the main [README](README.md): the overview
callout, the "Design Tool" row of the tech-stack table, and the Frontend Development
section.

The practical consequence is that Bob worked **against a frozen contract**. It could
not reach into the backend and reshape an endpoint to make the UI easier to write; it
had to consume `backend/app/api/voice.py` exactly as it stood. Most of the design
decisions below follow from that constraint.

---

## 2. What Bob delivered

Roughly 3,800 lines across five files, with no bundler, no framework, no npm
dependency tree, and no build step of any kind:

```
frontend/
  index.html       461 lines   landing page
  app.html         835 lines   voice + text advisor
  dashboard.html  1494 lines   financial snapshot
  styles.css       585 lines   the entire design system
  api.js           401 lines   API client + shared browser helpers
  README.md                    install, dev, deploy and design notes
```

The only network request the pages make outside the API is the Google Fonts stylesheet
for Sora and Manrope — and Bob documented how to drop even that: remove two `<link>`
tags per page and the CSS falls back to a system sans-serif stack. A fully offline
build is a two-minute edit rather than a refactor.

The "no build step" choice was deliberate and worth naming. A vanilla-JS bundle drops
straight into a FastAPI `StaticFiles` mount and ships; a React app would have dragged
in a toolchain, a lockfile, and a build stage for a three-page UI that renders a
handful of numbers.

---

## 3. The design system

Bob authored a single stylesheet organised around CSS custom properties, so the whole
look is retuned from one `:root` block rather than by hunting hex codes through markup.

### Colour

The palette is deliberately narrow — a dark ink, a deep pine green, a mint accent, and
a pale mist background:

| Token | Value | Role |
|---|---|---|
| `--ink` | `#101F1A` | Primary text |
| `--ink-soft` / `--ink-muted` | `#2C3E38` / `#5A6B65` | Secondary and tertiary text |
| `--pine` / `--pine-dark` / `--pine-tint` | `#17594A` / `#10402F` / `#E4EFEA` | Primary actions, emphasis |
| `--mint` / `--mint-tint` | `#6FD6A6` / `#E3F8ED` | Accent, positive highlight |
| `--mist` | `#EFF4F1` | Page background |
| `--surface` | `#FFFFFF` | Cards and panels |
| `--border` / `--border-strong` | `#D5E1DB` / `#B9CCC3` | Hairlines and dividers |

Status colours were kept **inside the same family** rather than pulled from a generic
traffic-light set — `--good` reuses pine, `--warn` is a muted ochre `#9A6B12`, `--bad`
is a desaturated brick `#A2382C`, each with a matching tint for backgrounds. A budget
warning therefore reads as part of the product rather than as a browser alert.

### Type, shape and spacing

- **Sora** for headings, **Manrope** for body, each with a full system fallback stack.
- Radii capped at three steps: `--r-sm: 4px`, `--r: 6px`, `--r-lg: 8px`. Nothing rounder.
- One shadow token, and it is almost invisible: `0 1px 0 rgba(16,31,26,.04)`. Depth
  comes from 1px borders, not from elevation.
- A single spacing rhythm: `--gap: 16px`, `--pad: 20px`, `--maxw: 1080px`.
- One motion token: `--t: 120ms ease`, used only for colour and border changes.

### Layout

Every grid is a responsive bento built on `repeat(auto-fit, minmax(…))`, so pages
reflow by available width instead of by breakpoint. Two details Bob added because
Indian rupee figures run long: `overflow-wrap: anywhere` plus `min-width: 0` on grid
children, so a ₹ figure wraps rather than blowing out its column, and horizontal
scrolling contained *inside* the chart boxes so the page body never scrolls sideways.

The stylesheet also sets `text-align: center` globally — a deliberate direction, with
headings, labels, metrics, body copy, profile values, and chat messages all sharing the
same axis.

### The design brief

Bob was steered toward one idea, recorded in the frontend README as a **compact
snapshot hero**: real numbers above the fold on every page, not decoration. That is why
all three pages open with a metrics panel rather than a marketing banner.

---

## 4. Page-by-page breakdown

### `index.html` — landing

The entry point. Explains what FinPal does, leads into the advisor, and follows the
snapshot-hero rule by showing figures rather than stock imagery.

### `app.html` — the advisor

The most stateful page. Bob assembled it from semantic elements — `<form>`, `<button>`,
`<nav>`, `<section>` — with named hooks for the behaviour layer:

- `#transcript` — the conversation log, marked `role="log" aria-live="polite"`
- `#mic-btn` — hold-to-speak capture
- `#text-input` / `#send-btn` — the text composer, always available as a fallback
- `#status-label` — a `role="status"` line narrating *connecting → ready → recording →
  thinking → speaking → error*
- `#phase-badge` — which stage of the advisory conversation is active
- `#profile-content` — the live profile panel, repainted whenever the backend sends a
  `done` event
- `#clear-chat-btn`, `#theme-toggle`, `#dashboard-btn` — session and view controls

### `dashboard.html` — the financial snapshot

The largest file, and the one doing the most rendering work: it turns a profile object
into readable output — budget allocation, savings position, debt view, and DOM-drawn
column charts built from divs and CSS rather than from a charting library. No chart
dependency was added; the bars are styled elements carrying explicit accessible labels.

---

## 5. The API layer

[`api.js`](frontend/api.js) is the seam between Bob's UI and the untouched Python
backend. It attaches a single `window.FinPal` object — no modules, no imports, works
from a plain `<script src="api.js">` tag.

| Group | Members |
|---|---|
| Session / API | `apiBase`, `createSession`, `getProfile`, `streamChat`, `sendVoice` |
| Voice | `startRecording`, `micSupported`, `pickMimeType`, `extForMime`, `stopAudio` |
| Session URL | `sessionFromQuery`, `linkWithSession`, `rememberSessionInUrl` |
| Formatting | `inr`, `pct`, `clamp`, `titleise` |

### Streaming

`streamChat` reads the SSE body of `POST /api/sessions/{id}/chat/stream` and dispatches
the three event shapes the backend emits:

| `type` | Fields | UI effect |
|---|---|---|
| `token` | `text` | Appended to the live advisor message |
| `done` | `profile`, `user_text` | Stream closed; profile panel repainted |
| `error` | `text` | Surfaced on the status line, composer stays usable |

### Where the API lives

Rather than hard-coding a host, Bob wrote a four-tier resolution order, first match
winning:

1. `window.FINPAL_API_BASE`, if set before `api.js` loads
2. an `?api=` query parameter — handy for testing against a LAN address
3. a `file://` fallback to `http://localhost:8000`
4. **same origin** — the production default

One bundle therefore covers the two-terminal development setup (static files on `:5500`,
API on `:8000`, CORS already permitted by the backend's middleware) and the single-origin
production deployment, with no edit in between.

### Deployment guidance

Bob also documented the production path in the frontend README: mount the folder from
`backend/app/main.py` with `StaticFiles(directory=FRONTEND, html=True)`, and mount it
**last**, because a `StaticFiles` mount at `/` is a catch-all that will shadow
`/api/...` if registered first. That single ordering note is the kind of thing that
costs an afternoon when it is missing.

---

## 6. Voice capture in the browser

Browser audio support is uneven, so Bob probed for it rather than assuming. On recording
start, `pickMimeType` walks a preference list and takes the first that
`MediaRecorder.isTypeSupported` accepts:

```
audio/webm;codecs=opus  →  audio/webm  →  audio/ogg;codecs=opus  →  audio/ogg  →  audio/mp4
```

If none is supported, the browser default is used. `extForMime` then sets a matching
file extension on the uploaded blob, because the backend's `_EXT_MAP` names the
temporary file for Whisper from that extension — get it wrong and transcription fails on
an otherwise valid recording. A good example of Bob working *to* the existing backend
contract rather than around it.

Failure paths are handled explicitly instead of thrown:

- **Permission denied** — the status line explains it and the text composer stays live
- **`NotFoundError` (no microphone)** — "Could not open the microphone. Type your message instead."
- **No `MediaRecorder`** — voice controls step aside, text keeps working
- **Blocked TTS autoplay** — reported on the status line; the reply text is already on
  screen, so nothing is lost

The guiding rule: a microphone problem should never be able to end the conversation.

---

## 7. Session handling

The session ID lives in the URL as `?session=<id>` — and nowhere else. No
`localStorage`, no cookies.

That is a design decision, not an omission. It gives a clean-slate default: opening
`app.html` starts a fresh conversation, while `app.html?session=<id>` resumes an
existing one. `app.html` writes the new ID into the address bar with
`history.replaceState`, so a reload keeps the thread, and `linkWithSession` rewrites the
nav links so the ID travels between the landing page, the advisor, and the dashboard.

Stale IDs degrade rather than fail. If the API answers 404, `app.html` says so and opens
a new session; `dashboard.html` shows a "session unavailable" notice with a link back to
the advisor.

---

## 8. Accessibility and the performance strip-down

An earlier iteration of the UI had been visually heavy. Bob's pass removed GSAP and
ScrollTrigger, the hero canvas, the particle field, cursor tracking, 3D tilt effects,
decorative timers, and heavy backdrop blur. What survives is a 120ms colour/border
transition and a 1px press offset on direct interaction — no animation loops, no
scroll-driven work, and no JavaScript animation library in the bundle at all.

On top of that:

- `prefers-reduced-motion: reduce` collapses every transition to roughly zero
- The transcript uses `scroll-behavior: auto` and is scrolled by direct assignment, so
  streaming tokens never trigger a smooth-scroll animation on every chunk
- Transcript is `role="log" aria-live="polite"`; the status line is `role="status"`
- DOM charts carry `role="img"` with an `aria-label` listing their values, so the data is
  available without seeing the bars
- Every control is a real `<button>` or form element, keyboard-operable, with a visible
  `:focus-visible` ring
- **All user and model text is inserted with `textContent`, never `innerHTML`** — model
  output is untrusted input, and this closes the obvious injection path

---

## 9. How Bob was briefed and how it delivered

**The brief.** Bob was given the live backend contract from `backend/app/api/voice.py`,
the design direction (compact snapshot hero, the four-colour palette, the Sora/Manrope
pairing), and a hard constraint: no build step, no framework, no CDN JavaScript, and no
changes to any Python file.

**The delivery model.** Bob shipped a complete, self-contained static folder rather than
a stream of small commits — the packaged archive `frontend_finpal_dark.zip` is still in
the repository root. Its install instruction is literally
`rm -rf frontend && unzip finpal-frontend.zip`, with "no Python code changes are
required" stated up front.

That shows up plainly in the git history. Commit `606cea5` ("Frontend updation") replaced
all three pages in one move and introduced `api.js` and `styles.css` as new files —
roughly +2,310 / −2,317 lines in a single step, the moment the inline styles and scripts
of the previous build were factored into a real design system and a real API layer.

The trade-off is honest: whole-folder delivery gives a coherent, internally consistent
result and a much noisier diff. For a UI rewrite where the design system is the point,
that was the right side of the trade — and commit `7f7267f` later reverted a change that
had undone the `api.js` / `styles.css` split, which is the history confirming the split
was worth keeping.

**The documentation.** Bob wrote [`frontend/README.md`](frontend/README.md) alongside the
code: install steps, the two-terminal dev setup with its CORS note, the API-base
resolution table, the FastAPI mount snippet with the ordering warning, the backend
contract it consumes, the session model, the voice negotiation order, the design
rationale, and its own pre-hand-off test checklist. The UI arrived explained, not just
built.

---

## 10. Verification before hand-off

Bob's checklist was run over `http://localhost` against the live FastAPI backend — not
against mocks, and over HTTP rather than `file://`, because `getUserMedia` needs a secure
context and would otherwise have failed silently:

- [x] Landing → advisor → dashboard navigation with the session ID carried through
- [x] Session creation, streamed chat tokens, profile panel updating on `done`
- [x] `dashboard.html?session=<id>` rendering the profile-derived snapshot
- [x] `dashboard.html` with no `?session`, and with an unknown ID
- [x] Desktop (1280px) and mobile (375px) layouts, no horizontal page scroll
- [x] Browser console clean — no errors, no warnings

---

## 11. What changed afterwards

Bob's output was the foundation, not the final state. Later commits hand-tuned it for
conversation-lifecycle edge cases the initial build did not cover — most visibly
`5e1a79a` ("Local frontend rewrite"), which reworked `app.html` and `dashboard.html` for
session resume/replay and more defensive profile rendering.

The accurate summary: **Bob produced the complete initial UI, design system, and API
layer; subsequent work hardened them against real session behaviour.** The palette, the
type pairing, the layout system, the API-base resolution, the voice negotiation order,
and the accessibility model are all still Bob's, and all still in the shipped product.

---

## 12. Takeaways

- **Give the agent a frozen contract.** Bob could not modify the backend, so it wrote a
  UI that fits the API as built — including the `_EXT_MAP` extension detail that would
  have broken transcription if guessed at.
- **Constraints improved the output.** "No build step, no framework, no CDN JS" produced
  a five-file bundle that deploys as a single `StaticFiles` mount.
- **Whole-folder delivery suits design work.** One coherent system beats fifteen partial
  commits when the deliverable *is* the consistency.
- **Ask for the documentation with the code.** The frontend README made the hand-off
  reviewable instead of archaeological.
- **Accessibility is cheaper when it is in the brief.** ARIA roles, keyboard operability,
  reduced-motion support, and `textContent`-only insertion were part of the first build
  rather than a later retrofit.

---

<div align="center">
  Frontend designed and developed with
  <a href="https://www.ibm.com/products/watsonx/bob">IBM Bob</a>
</div>
