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
