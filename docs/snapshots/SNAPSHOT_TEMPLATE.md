# GHL Snapshot: [SNAPSHOT NAME]

**Version:** 1.0.0
**Date Created:** YYYY-MM-DD
**Last Updated:** YYYY-MM-DD
**Owner:** [Name]
**GHL Location ID:** [ID]

---

## Overview

[One paragraph describing what this snapshot is, what business it serves, and what it automates.]

---

## Included Components

### Pipelines
| Pipeline Name | Stages | Purpose |
|---|---|---|
| | | |

### Workflows / Automations
| Workflow Name | Trigger | Actions | Status |
|---|---|---|---|
| | | | Active/Inactive |

### Funnels & Websites
| Name | Type | URL | Purpose |
|---|---|---|---|
| | Funnel/Website | | |

### Forms & Surveys
| Name | Type | Connected To | Purpose |
|---|---|---|---|
| | Form/Survey | | |

### Calendars
| Name | Type | Team | Purpose |
|---|---|---|---|
| | Round Robin/Personal | | |

### Email Templates
| Name | Subject | Used In |
|---|---|---|
| | | |

### SMS Templates
| Name | Used In |
|---|---|
| | |

### Custom Values
| Key | Description | Example Value |
|---|---|---|
| | | |

### Custom Fields (Contact)
| Field Name | Type | Purpose |
|---|---|---|
| | | |

### Tags (system tags used in automations)
| Tag | Applied When | Removed When |
|---|---|---|
| | | |

### Trigger Links
| Name | Linked To | Purpose |
|---|---|---|
| | | |

---

## N8N Workflows Connected

| N8N Workflow Name | Trigger Type | GHL Event | Description |
|---|---|---|---|
| | Webhook | | |

---

## Deployment Checklist

When applying this snapshot to a new sub-account:

- [ ] Apply snapshot in GHL Agency > Sub-Accounts
- [ ] Update all **Custom Values** with client-specific data
- [ ] Re-authenticate any connected integrations (Google, FB, etc.)
- [ ] Verify calendar availability and team assignments
- [ ] Test each pipeline stage automation
- [ ] Clone N8N workflows and update webhook URLs
- [ ] Update `.env` with new `GHL_LOCATION_ID`
- [ ] Run `scripts/bootstrap_google.py` to scaffold client Drive folder
- [ ] Add row to **Expansion-Tracker** sheet

---

## Known Issues / Notes

- [Note any quirks, manual steps, or things that need attention on deploy]

---

## Changelog

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | YYYY-MM-DD | | Initial documentation |
