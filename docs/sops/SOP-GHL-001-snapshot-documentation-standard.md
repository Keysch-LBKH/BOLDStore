# SOP-GHL-001: Snapshot Documentation Standard (Pacitto Method)

**SOP ID:** SOP-GHL-001
**Category:** GHL
**Version:** 1.0.0
**Last Reviewed:** 2026-04-24
**Owner:** LBKH Solutions
**Estimated Time:** 20–60 min per snapshot (depending on complexity)

---

## Purpose

Establish a consistent, minimum viable documentation standard for every GHL snapshot built or managed by LBKH Solutions — based on Michael Pacitto's methodology (Agency Unbound / Snapshot Manager PRO).

The goal is not to document everything. It is to document *just enough* that any team member, VA, or future version of yourself can pick it up and understand it without asking questions.

> "GHL doesn't just scale your revenue — it also scales your mistakes."
> — Michael Pacitto

---

## The Core Philosophy: MVD (Minimum Viable Documentation)

There are two cardinal sins of scale:
1. **Documenting too much** — a 97-page manual nobody reads
2. **Documenting nothing** — no idea what anything does when it breaks

MVD is the skeleton: not everything, but everything you *need*.

---

## The 5 Methods — Applied to BOLDStore

### Method 1: The Asset Spreadsheet (5-Column System)

Every asset in a snapshot gets a row in the documentation sheet. Minimum columns:

| Column | What Goes Here |
|---|---|
| **Name** | Exact name of the asset as it appears in GHL, using the module naming prefix |
| **Asset Type** | Workflow / Tag / Form / Pipeline / Calendar / Email Template / Custom Value / Custom Field |
| **Module** | Which module this asset belongs to (R0–RX) |
| **Description / Function** | One sentence: what does this do and when does it fire? |
| **Set Up Notes** | What must a human do when deploying this to a new account? |
| **Updateable?** | **YES** = safe to push snapshot updates. **NO** = clients may have customized this — DO NOT overwrite without checking first |
| **Status** | Blank / Done / Issue / In Progress |
| **Status Notes** | Why is it flagged? What changed in this version? |

**The Updateable column is the most important field.** It is the difference between a clean update and a support emergency.

### Method 2: Modular Structure with Naming Conventions

Never build one giant tangled snapshot. Group assets into logical modules, then prefix every asset name with its module ID so anyone can instantly tell what connects to what.

**Standard module prefix format:**
```
R{module_number}-{step_number}.{sub_step}. {AssetType shortcode} {Description}
```

Example:
```
R2-2.0. Appointment Booked -> Reminder Series    (Workflow, Module R2)
R2-2.0. Email Reminder 01                        (Email Template, Module R2)
R3. Order-Paid                                   (Tag, Module R3)
```

**Standard module IDs for BOLDStore snapshots:**

| ID | Name | Purpose |
|---|---|---|
| R0 | Foundation | Universal assets — custom values, core pipelines, base tags |
| R1 | Lead Capture | Opt-in / ad lead entry point |
| R2 | Appointments | Booking, reminders, no-show handling |
| R3 | Purchasing | Order forms, payment, purchase confirmation |
| R4 | Onboarding | Post-purchase client orientation |
| R5+ | Custom | Add additional modules as the snapshot grows |

### Method 3: Visual Customer Journey Map (Before You Build)

Before adding a single asset to GHL, draw the full customer journey from first touch to end goal. Work backwards from the product.

**The 3 questions at every step:**
1. What needs to happen here?
2. What must be true for someone to reach this step?
3. Does this asset connect back to the core product? If not, it doesn't belong in the snapshot.

See `docs/snapshots/[snapshot-name]-journey-map.md` for each snapshot's visual map.

### Method 4: RIP — Repetitive Improvement Plan

Never do one giant 6-month overhaul. Push small, frequent improvements instead.

**RIP rules:**
- Only update assets marked **Updateable = YES**
- Bump the snapshot version number for every push (V2.0 → V2.1)
- Log every change in the snapshot doc changelog
- Test one client account before pushing to all

### Method 5: Minimum Viable Documentation (The Philosophy)

Before calling any snapshot "documented," confirm these are complete:
- [ ] Every asset has a row in the sheet
- [ ] Every asset has a Description/Function (one sentence minimum)
- [ ] Every asset has an Updateable flag (YES or NO — blank is not acceptable)
- [ ] All module prefixes follow the naming convention
- [ ] Customer journey map exists
- [ ] Deployment checklist exists

---

## When to Document

| Trigger | Action |
|---|---|
| New asset added to snapshot | Add row to sheet immediately |
| Asset updated/changed | Update Description + Status Notes + bump version |
| Asset removed | Mark as removed in Status Notes, do not delete the row |
| New client deployed | Add row to Expansion-Tracker sheet |
| Snapshot version pushed | Log in Changelog tab |

---

## BOLDStore Sheet Structure (per snapshot)

Each snapshot gets its own Google Sheet with 4 tabs:

| Tab | Contents |
|---|---|
| **Overview** | Snapshot name, version, GHL location ID, owner, date |
| **Assets** | The full Pacitto-style asset table (8 columns) |
| **Modules** | Module ID, name, description, scope/objectives |
| **Stakeholders** | Who interacts with the snapshot (Contact / User / Agency) and what they need |

Create the sheet by running:
```bash
python scripts/create_snapshot_sheet.py \
  --snapshot "Snapshot Name" \
  --folder-id <google_drive_snapshots_folder_id>
```

---

## Related Files

- `docs/snapshots/SNAPSHOT_TEMPLATE.md` — blank snapshot doc template
- `docs/snapshots/tattoo-artist-v2.md` — Tattoo Artist V2 documentation
- `scripts/create_snapshot_sheet.py` — Google Sheet builder
- `docs/snapshots/tattoo-artist-v2-journey-map.md` — customer journey map

---

## Changelog

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-04-24 | LBKH | Initial — based on Pacitto/Agency Unbound methodology |
