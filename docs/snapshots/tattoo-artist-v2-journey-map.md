# Customer Journey Map — Tattoo Artist V2

**Snapshot:** Tattoo Artist V2.0
**End Goal:** Client books and pays for a tattoo service
**Mapped:** 2026-04-24
**Method:** Pacitto Visual Mapping — work backwards from the product

---

## The Journey (End to Start)

```
PAID ADS (FB / Google)
        │
        ▼
[R1] OPT-IN FUNNEL
  • R1. OptIn Form — captures name, email, phone
  • R1-1.0. OptInSubmit -> Deliver Lead Magnet  ⚠️ ISSUE — needs fix
  • R1. Ads-1 tag applied (tracks ad source)
  • R1. OptIn tag applied
  • R1-1.1. Assign Contact to User (sales person)
  • Added to R0. Buyer Pipeline → Stage: New Lead
        │
        ▼
[R1 → R2] EMAIL FOLLOW-UP SEQUENCE
  • 3 follow-up emails pushing to book a sales/consultation call
  • Goal: get contact to the booking calendar
        │
        ▼
[R2] SALES CALENDAR
  • R3. Calendar Consultation — contact self-books
  • R2-2.0. Appointment Booked -> Reminder Series fires
    └── R2-2.0. Email Reminder 01 sent
  • Pipeline stage moves → Appointment
        │
        ▼
[R2] CONSULTATION / SALES CALL
  • R2-2.1. Appointment Complete -> Follow up emails fires
  • SMS + email follow-up sequence
  • Pipeline stage moves → Sales Call
        │
        ▼
[R3] ORDER / PAYMENT
  • R3. Order 2 Step form — 2-step order form on funnel sales page
  • Step 1: R3. Order-Pending tag applied
    └── R2-3.0. Payment Reminder fires if not completed
  • Step 2: Payment completed
    └── R3. Order-Paid tag applied
    └── R3-4.0. Product Purchased -> Update contact and pipeline fires
    └── R3-1.0. Email Purchase Confirmation sent
  • Pipeline stage moves → Closed
        │
        ▼
[R4] ONBOARDING
  • R4-1.0. Product Purchased -> Client Onboarding Sequence fires
    └── R4-1.0. Email Onboarding sent (portal login + next steps)
  • R0. Client Portal URL custom value delivers client portal access
        │
        ▼
CLIENT IN PORTAL ✓
```

---

## Module Boundaries

| Module | Entry Point | Exit Point | Hand-off |
|---|---|---|---|
| R1 Lead Capture | Ad click → opt-in form | OptIn tag applied, assigned to user | Triggers email follow-up, enters pipeline |
| R2 Appointments | Email follow-up → calendar booking | Appointment completed, Sales Call stage | Triggers order flow |
| R3 Purchasing | Order form visited | Order-Paid tag applied | Triggers onboarding sequence |
| R4 Onboarding | Order-Paid tag | Onboarding email sent, portal delivered | Client self-serves in portal |

---

## Assets That Do NOT Connect Back to the Core Product

*(Any asset added in the future that doesn't fit the above flow should be questioned before inclusion)*

None currently identified — all 21 assets map directly to the journey above.

---

## Key Decision Points (Where Clients Drop Off)

1. **Opt-in → Calendar** — email sequence quality determines conversion here
2. **Calendar → Order Form** — sales call outcome; no automation can fix a bad sales call
3. **Order Form Step 1 → Step 2** — payment reminder workflow (`R2-3.0`) handles abandonment

---

## Updateable Risk Map

| Stage | Assets at Risk if Updated Without Checking |
|---|---|
| Lead Capture | R1. OptIn Form (clients may have customized fields) |
| Purchasing | R3. Order 2 Step (clients may have changed pricing/products) |
| Onboarding | R4-1.0. Email Onboarding (clients always customize this) |

---

## Notes

- `R1-1.0. OptInSubmit -> Deliver Lead Magnet` is flagged **Issue** — must resolve before deploying to new accounts
- `R3. Calendar Consultation` must be manually connected to each artist's Google Calendar on deploy — cannot be automated via snapshot
- `R0. Client Portal URL` custom value must be updated per client before going live
