"""
Create and populate the Ghost Print Co. product pipeline sheets.

Two sheets are needed — create each as a blank Google Sheet, share with
the service account as Editor, then pass both IDs to this script.

Usage:
    python scripts/create_product_pipeline_sheets.py \
        --brand-sheet-id <id> \
        --items-sheet-id <id>

Sheet 1 — Brand Profile:
    Brand voice, tone, audience, store config, and AI prompt templates.
    Fill this in once per client. N8N reads it on every workflow run.

Sheet 2 — Item Input:
    One row per product. Set Status = Approved to trigger the N8N workflow.
    N8N writes enhanced content back into this sheet, then exports CSVs.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from google.oauth2 import service_account
import gspread

from config import settings

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# ── Brand Profile tab layout ──────────────────────────────────────────────────
BRAND_PROFILE_ROWS = [
    # Field, Value, Notes
    ["Brand Name",               "Ghost Print Co.",                              "Display name used in all generated content"],
    ["Tagline",                  "Printed in darkness. Worn with intent.",        "Short brand statement — used in email footers and social bios"],
    ["Store Platform",           "Shopify",                                       "Shopify | WooCommerce | Other"],
    ["Store URL",                "https://ghostprintco.com",                      "Base store URL — no trailing slash"],
    ["Product URL Pattern",      "https://ghostprintco.com/products/{handle}",    "Replace {handle} with the product slug"],
    ["Instagram Handle",         "@ghostprintco",                                 "Used in social captions and hashtag sets"],
    ["TikTok Handle",            "@ghostprintco",                                 "Leave blank if not active"],
    ["Price Point",              "Premium ($45–$120)",                            "Informs tone of product copy"],
    ["Target Audience",          "Tattoo artists, streetwear collectors, art-forward consumers aged 22–40",
                                                                                  "Used to shape AI-generated copy"],
    ["Brand Voice",              "Dark. Minimal. Confident. No fluff. Speaks to collectors, not shoppers.",
                                                                                  "Core voice instruction passed to Claude on every run"],
    ["Visual Aesthetic",         "High-contrast screenprint. Black, white, blood red. Tattoo flash meets streetwear.",
                                                                                  "Used for image alt text and social copy context"],
    ["Core Hashtags",            "#ghostprintco #screenprint #streetwear #tattooculture #limiteddrop #premiumapparel",
                                                                                  "Always appended to social posts"],
    ["Drop Hashtags",            "#newdrop #limitededition #dropsoon",            "Added for new collection launches"],
    [""],
    ["── AI Prompt Templates ──", "", "These are passed directly to Claude. Edit to tune output."],
    ["Product Description Prompt",
     "Write a product description for a premium screenprint streetwear item from Ghost Print Co. "
     "Voice: dark, minimal, confident — speaks to collectors not shoppers. "
     "2–3 sentences. No fluff. Lead with the visual impact of the design, then the quality of the garment. "
     "End with one short brand-statement line.",
     "Used for store product page body copy"],
    ["SEO Title Prompt",
     "Write an SEO-optimised product title. Format: [Product Name] | Ghost Print Co. "
     "Under 60 characters. Include one relevant keyword naturally.",
     "Used for store SEO title field"],
    ["SEO Description Prompt",
     "Write an SEO meta description for this Ghost Print Co. product. "
     "Under 155 characters. Include brand name, product type, and one key attribute. "
     "Natural language — not a keyword list.",
     "Used for store SEO description field"],
    ["Alt Text Prompt",
     "Write image alt text for a Ghost Print Co. product photo. "
     "Describe what is visible: garment type, colour, print subject. "
     "Under 125 characters. Do not start with 'Image of'.",
     "Used for product image accessibility and SEO"],
    ["Social Caption Prompt",
     "Write an Instagram caption for a Ghost Print Co. product drop. "
     "Voice: underground, exclusive, art-forward. "
     "Mention the product name naturally in the first sentence. "
     "2–4 lines. End with a one-line call to action directing to the link in bio. "
     "Do not use emojis unless they fit the dark aesthetic.",
     "Used for Instagram feed posts"],
]

# ── Item Input column headers ─────────────────────────────────────────────────
ITEM_INPUT_HEADERS = [
    # Input columns (user fills these in)
    "SKU",
    "Product Name",
    "Category",           # T-Shirt / Hoodie / Hat / Tote / Other
    "Base Colour",
    "Price",
    "Sizes Available",    # e.g. XS,S,M,L,XL,XXL
    "Raw Notes",          # brief description or design notes from the artist
    "Image URL 1",
    "Image URL 2",
    "Image URL 3",
    "Status",             # Draft | Approved | Processing | Done | Error
    # Output columns (N8N fills these in)
    "Enhanced Title",
    "Enhanced Description",
    "SEO Title",
    "SEO Description",
    "Image Alt Text",
    "Social Caption",
    "Social Hashtags",
    "Product URL",        # filled by N8N from Store URL + handle
    "Shopify Handle",     # slug used in product URL
    "Error Notes",        # set by N8N if processing fails
]

# Sample row showing expected format
ITEM_INPUT_SAMPLE = [
    "GPC-001",
    "Reaper Flash Tee",
    "T-Shirt",
    "Washed Black",
    "65.00",
    "S,M,L,XL,XXL",
    "Traditional tattoo flash reaper design. Heavy 6oz cotton. Front chest print.",
    "https://drive.google.com/file/d/SAMPLE_IMAGE_ID_1/view",
    "",
    "",
    "Draft",
    "", "", "", "", "", "", "", "", "", "",
]


def setup_brand_profile(ws: gspread.Worksheet) -> None:
    ws.update_title("Brand Profile")
    ws.clear()
    ws.update("A1", [["Ghost Print Co. — Brand Profile"]], value_input_option="USER_ENTERED")
    ws.update("A2", [["Field", "Value", "Notes"]], value_input_option="USER_ENTERED")
    ws.update("A3", BRAND_PROFILE_ROWS, value_input_option="USER_ENTERED")

    # Freeze header rows, widen columns
    ws.freeze(rows=2)
    ws.format("A2:C2", {
        "backgroundColor": {"red": 0.47, "green": 0.08, "blue": 0.17},
        "textFormat": {"foregroundColor": {"red": 1, "green": 1, "blue": 1}, "bold": True},
    })
    # Make Value column wide
    ws.columns_auto_resize(0, 3)


def setup_item_input(ws: gspread.Worksheet) -> None:
    ws.update_title("Item Input")
    ws.clear()
    ws.update("A1", [["Ghost Print Co. — Item Input"]], value_input_option="USER_ENTERED")
    ws.update("A2", [ITEM_INPUT_HEADERS], value_input_option="USER_ENTERED")
    ws.update("A3", [ITEM_INPUT_SAMPLE], value_input_option="USER_ENTERED")

    ws.freeze(rows=2)
    ws.format("A2:U2", {
        "backgroundColor": {"red": 0.47, "green": 0.08, "blue": 0.17},
        "textFormat": {"foregroundColor": {"red": 1, "green": 1, "blue": 1}, "bold": True},
    })

    # Highlight the Status column (K) to make it obvious
    ws.format("K2:K200", {
        "backgroundColor": {"red": 1.0, "green": 0.95, "blue": 0.8},
    })


def main():
    parser = argparse.ArgumentParser(
        description="Set up Ghost Print Co. product pipeline sheets."
    )
    parser.add_argument("--brand-sheet-id", required=True,
                        help="ID of blank Google Sheet for Brand Profile (shared with service account).")
    parser.add_argument("--items-sheet-id", required=True,
                        help="ID of blank Google Sheet for Item Input (shared with service account).")
    args = parser.parse_args()

    creds = service_account.Credentials.from_service_account_file(
        settings.google_service_account_file, scopes=SCOPES
    )
    gc = gspread.authorize(creds)

    print("Setting up Brand Profile sheet...")
    brand_ss = gc.open_by_key(args.brand_sheet_id)
    setup_brand_profile(brand_ss.sheet1)
    print(f"  Done. URL: https://docs.google.com/spreadsheets/d/{args.brand_sheet_id}/edit")

    print("Setting up Item Input sheet...")
    items_ss = gc.open_by_key(args.items_sheet_id)
    setup_item_input(items_ss.sheet1)
    print(f"  Done. URL: https://docs.google.com/spreadsheets/d/{args.items_sheet_id}/edit")

    print(f"""
Done. Add to your .env:
  GHOST_PRINT_BRAND_SHEET_ID={args.brand_sheet_id}
  GHOST_PRINT_ITEMS_SHEET_ID={args.items_sheet_id}

Next: Fill in the Brand Profile values, then add products to Item Input.
Set Status = Approved on any row to queue it for the N8N workflow.
""")


if __name__ == "__main__":
    main()
