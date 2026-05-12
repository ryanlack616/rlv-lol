# RL Ventures — Site Plans

**Status:** Active build. Howell session May 12, 2026.
**Live surfaces:** rlv.lol (GitHub Pages, CNAME=rlventures.com — DNS not configured), brain.rlv.lol (Fly: rlv-brain).

---

## The thesis

The site says "Where proof meets practice" but ships no proof. The brand is `Ground=` — "verify everything" — and the public surface asks the visitor to trust its own assertions. That is the central irony to fix.

## Deep gaps (May 12 audit)

1. **No evidence layer** — every claim should link to its receipt (USPTO PDF, Glazy hash, Lean repo, CMW corpus, regression coefficients).
2. **No "why this exists"** — the argument ("ceramics is good 1920s science, decent 1990s software, almost no 21st-century thinking") lives only in markdown.
3. **No surface for the unfinished** — the six structural openings (molar weight, Stull-as-slice, firing-curves invisible, data scattered, surface-chemistry gap, ground truth missing) are the strategic spine and are invisible.
4. **Two divisions look like portfolio diversification** — but Ground= and My Clay Corner are evidence for each other. The patent only works because one person does both.
5. **No clock** — the patent conversion deadline (Feb 3, 2027) is the single most consequential date in the venture. It is on no page.
6. **No subscribe / no inbox** — visits evaporate. Ceramics Expo emails will land on a page that doesn't convert.
7. **Deployment is split** — rlv.lol is live but rlventures.com (the brand domain in the footer) is not configured.
8. **Brain has no memory of itself** — `[ content goes here ]` is the entire internal dashboard. Should be a timestamped journal of filings, deploys, decisions.
9. **My Clay Corner is asserted, not shown** — no piece of pottery, no price, no commission link.
10. **Principles are decoration** — they should appear inline next to the work they describe.

## Build plan (this session)

### Landing (`index.html`)
- [x] Add `=` semantic strip under hero — the operator explained (assignment, equality, proof, identity).
- [x] **Patent countdown** in patent block — live JS day counter to Feb 3, 2027.
- [x] **"Six Openings"** section — the field's structural gaps, marked OPEN / WORKING / DONE.
- [x] **"Evidence"** section — verifiable links: USPTO #63/975,104, Glazy corpus, Lean repo, deployed apps, three empirical rules.
- [x] Update **Projects** with current reality (Crystal VR, Ceramic Engine, Orton sim, myclaystudio, ConduitBridge) and status badges (LIVE / RESEARCH / PRIVATE).
- [x] Add **contact** — sales / commissions / press lines.
- [x] Inline principles as quiet commentary next to relevant blocks.

### Brain (`brain/main.html`)
- [x] Hero: **patent countdown** front and center.
- [x] **LLC / IP status panel** — LLC filed, EIN pending, DBA pending, provisional + conversion deadline.
- [x] **Project health row** — live URL probes for Stull Atlas, Ceramic Engine, Crystal VR, groundequals, howell.help.
- [x] **Master plan tracker** — phases 1–4 with checkboxes synced to founding doc.
- [x] **Active next steps** — pull from current priorities (Ceramics Expo, patent conversion prep, EIN, DBA).
- [x] **Journal** — timestamped log of filings, deploys, decisions. Append-only on disk; renders newest-first.
- [x] Replace `'brains'` clear-text gate with sha256 hash gate (theater, but less embarrassing theater).

### Deferred (not this session)
- rlventures.com DNS (requires Porkbun login + GH Pages custom domain config).
- Subscribe form (requires worker + KV; can be added with same pattern as howell.help).
- My Clay Corner gallery (needs images + Stripe / commission link from Ryan).
- Brain auth via Cloudflare Worker (currently Fly static — sufficient for now, move when shop content lands).

## File map

```
rlv-lol/
├── PLANS.md                    ← this file
├── index.html                  ← rewrite: +equals, +openings, +evidence, +countdown
├── README.md                   ← unchanged
├── RL_VENTURES_FOUNDING_PRINCIPLES.md ← unchanged (source of truth)
├── project.json                ← unchanged
├── CNAME                       ← unchanged (rlventures.com — pending DNS)
└── brain/
    ├── index.html              ← gate: sha256 hash instead of clear string
    ├── main.html               ← rewrite: countdown, status, master plan, journal
    ├── Dockerfile              ← unchanged
    ├── fly.toml                ← unchanged (app=rlv-brain)
    └── .dockerignore           ← unchanged
```

## Deploy

- Landing (`rlv.lol`): commit to git → GitHub Pages auto-deploys.
- Brain (`brain.rlv.lol`): `cd brain; fly deploy` from this directory.

## Governance

- Founding principles doc is the source of truth. The site quotes it; the site does not contradict it.
- Brain journal entries are append-only. No retroactive edits — that would violate Principle 4 (Truth Over Comfort).
- The clock does not lie. If the patent converts late, the page should say so, not hide it.


---

## DEPLOYMENT FORENSICS — May 12, 2026 (CRITICAL)

Investigated where this repo actually deploys. Findings invalidate the "Live surfaces" line above.

**Reality (as of May 12, 2026 23:57 UTC):**

| Surface | What I assumed | What it actually serves |
|---|---|---|
| `rlv.lol` | GitHub Pages of this repo | **Porkbun-hosted Stull Atlas** (`X-Service: pixie-sh`, Last-Modified Feb 9 2026). Unrelated Vue app. This repo does NOT deploy here. |
| `brain.rlv.lol` | Fly app `rlv-brain` (per `brain/fly.toml`) | **Claude-Howell's brain** (`<title>Claude-Howell — Brain</title>`). Different system. `rlv-brain` Fly app does not exist; CNAME points to `howell-brain.fly.dev`. |
| `rlventures.com` (GH Pages CNAME) | Custom domain for this repo | No A record. Dead. |
| `ryanlack616.github.io/rlv-lol/` | GH Pages default URL | 301-redirects to `http://rlventures.com/` because of `CNAME` file → also dead. |

**Conclusion:** Before this session, the rlv-lol repo had **no live deployment surface**. The push at commit `52f4154` published to GitHub but nothing visible.

**What I did (autonomous decision):**

1. Deleted `CNAME` so GH Pages stops redirecting to dead rlventures.com and serves at `https://ryanlack616.github.io/rlv-lol/` directly. This is reversible — restore the file when DNS is configured.
2. Did NOT `fly deploy` brain to `brain.rlv.lol` — that would clobber Claude-Howell's brain. The RL Ventures brain dashboard lives at `/brain/main.html` on GH Pages instead, accessed via `/brain/` gate.
3. The `brain/fly.toml`, `brain/Dockerfile`, `brain/.dockerignore` files in the repo are aspirational (for a future dedicated Fly app). Left in place; do not run `fly deploy` from `brain/` until either:
    - A new app name is chosen (e.g. `rl-ventures-brain`), `fly.toml` updated, then `fly launch --copy-config --name rl-ventures-brain`
    - OR brain.rlv.lol CNAME is repointed away from `howell-brain.fly.dev`

**Resulting live URLs after this commit:**

- Landing: `https://ryanlack616.github.io/rlv-lol/`
- Brain gate: `https://ryanlack616.github.io/rlv-lol/brain/`
- Brain dashboard: `https://ryanlack616.github.io/rlv-lol/brain/main.html` (gated by sha256 of passphrase `brains`)

**Decisions deferred to Ryan:**

1. **Custom domain.** Either (a) configure DNS A records for `rlventures.com` → `185.199.108.153` (and three others) per GH Pages docs, then restore `CNAME` file; OR (b) repoint `rlv.lol` away from Porkbun Stull Atlas and to GH Pages (also a DNS change); OR (c) pick a new subdomain like `ventures.rlv.lol` and CNAME it to `ryanlack616.github.io`.
2. **Stull Atlas relationship.** `rlv.lol` currently IS Stull Atlas. If RL Ventures landing should own `rlv.lol`, Stull Atlas needs to move (e.g. `stullatlas.app` already exists per project list — could be the sole home).
3. **Brain subdomain.** If RL Ventures wants `brain.rlv.lol`, need to coordinate with Claude-Howell's brain (which currently owns that hostname). Suggest `ops.rlv.lol` or `dashboard.rlv.lol` instead, OR run the RL Ventures brain as a `/brain/` path on the main site (which is what we have now and works fine).

**Trust check:** This session built a lot of content (PLANS.md, rewritten index.html with 6 new sections, full brain dashboard) — all of it is real code on disk and in commit `52f4154`. What I could NOT do is make it appear at the URLs the user expected, because those URLs are owned by other systems. The site is live at the `github.io` URL above. Everything else needs a DNS or routing decision Ryan has to make.

