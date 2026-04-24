# GHL Snapshot: Tattoo Artist V2.0

**Version:** 2.0
**Date Created:** 2026-04-24
**Last Updated:** 2026-04-24
**Owner:** LBKH Solutions
**GHL Location ID:** Bjf6hMmrdoHegwuNVjdD
**Template Credit:** Agency Unbound (agencyunbound.com) — Snapshot Documentation V2.0

---

## Overview

Full-funnel GHL snapshot for tattoo artists. Covers lead capture from paid ads through opt-in, consultation booking, purchasing, and client onboarding. Built around 5 modules (R0–R4) that can be enabled independently per client.

---

## Modules

| Module ID | Module | Description | Scope / Objectives |
|---|---|---|---|
| R0 | Foundation | All universal assets like custom values | Base layer — custom values, pipelines, tags shared across all modules |
| R1 | Opt in Lead | Opt in leads from ads, to send lead magnet | Funnel page with opt-in form; 3 follow-up emails to book sales call; notify sales team of new leads; add leads to pipeline |
| R2 | Sales Calendar | Simple booking page to book sales calls | Calendar booking widget; notifications & reminder emails; notify sales team; move pipeline stage to booked; cancellation flows; charge for no-shows |
| R3 | Purchasing | Handles all sales and purchase workflows | Purchase the sales product; email reminders to pay; refund policies; terms of service |
| R4 | Onboarding | Onboarding after sales that orients them to the tools available | Client portal access; onboarding email sequence; tool orientation |

---

## Stakeholders

| Type | Name | Description | What They Need |
|---|---|---|---|
| Contact | Prospective Clients | People inquiring about tattoo services | Booking info, pricing, portfolio |
| Contact | Referral Partners | Partners who send client referrals | Referral tracking, commission updates |
| User | Tattoo Artist | Main user — assigned to contacts | Updates when clients message, booking notifications |
| User | Studio Manager | Admin user managing bookings and follow-ups | Full pipeline visibility, payment status |
| Agency | Account Manager | LBKH Solutions account manager | Snapshot health, integration status |
| Agency | Tech Support | LBKH technical support | Access for troubleshooting |

---

## Assets

### R0 — Foundation

| Name | Asset Type | Description / Function | Set Up Notes | Updateable | Status |
|---|---|---|---|---|---|
| R0. Buyer Pipeline | Pipeline | Pipeline for tracking leads from new lead to close. Stages: New Lead → Appointment → Sales Call → Closed | Update stage names for tattoo studio context | ☐ | |
| R0. Client Portal URL | Custom Value | Stores client portal link for purchased users | Custom value used in emails and workflows | ☐ | |

### R1 — Opt in Lead

| Name | Asset Type | Description / Function | Set Up Notes | Updateable | Status |
|---|---|---|---|---|---|
| R1-1.1. User Tag Added -> Assign Contact to User | Workflow | Assigns contacts to a user based on "assign to sale" | Assign Sales User to the "assign to user" action | ☐ | Done — Changed for V2 |
| R1. Ads-1 | Tag | Applied when a lead comes from paid advertising | Connect to FB/Google Ads integration | ✓ | |
| R1. OptIn Form | Form | Opt-in form to capture lead details (name, email, phone) | Embed on landing page 'Opt In Funnel' | ☐ | |
| R1-1.0. OptInSubmit -> Deliver Lead Magnet | Workflow | Triggers when opt-in form submitted; adds 'Opt-In Lead' tag | Attach to RE-Form-Optin | ☐ | Issue |
| R1. OptIn | Tag | Indicates contact opted in via lead magnet funnel | Applied via workflow RE-WF-OptInSubmit | ✓ | |
| R1. Ads- Property | Custom Field | Stores property/service inquiry from client | Map to order and opt-in forms | ☐ | |
| R1. Desired Move-in Date | Custom Field | Date field for client's target appointment timeline | Add to forms and consultation intake | ✓ | |

### R2 — Sales Calendar

| Name | Asset Type | Description / Function | Set Up Notes | Updateable | Status |
|---|---|---|---|---|---|
| R3. Calendar Consultation | Calendar | Booking calendar for consultations | Integrate with artist's Google calendar | ☐ | |
| R2-2.0. Appointment Booked -> Reminder Series | Workflow | Sends confirmation and reminder emails for booked appointments | Trigger: Appointment Created on RE-Calendar-Consu | ☐ | |
| R2-2.0. Email Reminder 01 | Email Template | Reminder email for booked calls | Edit template for client use | ✓ | |
| R2-2.1. Appointment Complete -> Follow up emails | Workflow | Follow-up automation after sales call; sends SMS + emails | Trigger: Opportunity Stage = 'Sales Call' | ☐ | |

### R3 — Purchasing

| Name | Asset Type | Description / Function | Set Up Notes | Updateable | Status |
|---|---|---|---|---|---|
| R3. Order 2 Step | Form | 2-step order form for service/product purchase | Embed on Funnel Sales Page | ✓ | |
| R3. Order-Pending | Tag | Applied when contact reaches order form but hasn't paid | Add tag on form submission step 1 | ☐ | |
| R2-3.0. Appointment Complete -> Payment reminder | Workflow | Sends reminder to complete payment | Trigger: Tag = RE-Tag-OrderPending | ☐ | |
| R3. Order-Paid | Tag | Applied when order payment completed | Triggered via order form payment confirmation | ✓ | |
| R3-4.0. Product Purchased -> Update contact and pipeline | Workflow | Automation triggered when product is purchased successfully | Trigger: Tag RE-Tag-OrderPaid | ✓ | |
| R3-1.0. Email Purchase Confirmation | Email Template | Purchase confirmation email with client portal access | Attach inside RE-WF-ProductPurchased | ☐ | |

### R4 — Onboarding

| Name | Asset Type | Description / Function | Set Up Notes | Updateable | Status |
|---|---|---|---|---|---|
| R4-1.0. Product Purchased -> Client Onboarding Sequence | Workflow | On purchase, sends onboarding instructions and adds tags | Trigger: RE-Tag-OrderPaid | ☐ | |
| R4-1.0. Email Onboarding | Email Template | Email with onboarding steps and client portal login | | ☐ | |

---

## Deployment Checklist

When applying this snapshot to a new sub-account:

- [ ] Apply snapshot in GHL Agency > Sub-Accounts
- [ ] Update **R0. Client Portal URL** custom value with client's portal link
- [ ] Integrate **R3. Calendar Consultation** with artist's Google Calendar
- [ ] Embed **R1. OptIn Form** on the opt-in funnel page
- [ ] Connect **R1. Ads-1** tag to FB/Google Ads integration
- [ ] Update **R1-1.0. OptInSubmit** workflow — attach to RE-Form-Optin
- [ ] Fix **R1-1.0. OptInSubmit -> Deliver Lead Magnet** (flagged: Issue)
- [ ] Embed **R3. Order 2 Step** form on funnel sales page
- [ ] Edit **R2-2.0. Email Reminder 01** template for client branding
- [ ] Clone N8N workflows and update webhook URLs
- [ ] Run `scripts/bootstrap_google.py` to scaffold client Drive folder
- [ ] Create client snapshot Google Sheet via `scripts/create_snapshot_sheet.py`
- [ ] Update `.env` with new `GHL_LOCATION_ID`
- [ ] Add row to **Expansion-Tracker** sheet

---

## Known Issues

- **R1-1.0. OptInSubmit -> Deliver Lead Magnet** — flagged as "Issue" in source sheet. Needs review before going live.

---

## N8N Workflows Connected

| N8N Workflow Name | Trigger | GHL Event | Description |
|---|---|---|---|
| | | | *(to be added as workflows are built)* |

---

## Changelog

| Version | Date | Author | Changes |
|---|---|---|---|
| 2.0 | 2026-04-24 | LBKH | Initial documentation from Agency Unbound V2.0 template |
