"""
Create and populate the Ghost Print Co. product pipeline sheets.

Pass the ID of a single Google Sheet workbook (shared with the service
account as Editor). The script will find or create two named tabs:
  - "Brand Profile"  — voice, tone, store config, AI prompt templates
  - "Item Input"     — product rows; Status = Approved triggers N8N

Usage:
    python scripts/create_product_pipeline_sheets.py --sheet-id <workbook_id>
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
    ["Brand Name",          "Ghost Print Co.",                                   "Display name used in all generated content"],
    ["Tagline",             "Printed in darkness. Worn with intent.",             "Short brand statement — used in email footers and social bios"],
    ["Store Platform",      "Shopify",                                            "Shopify | WooCommerce | Other"],
    ["Store URL",           "https://ghostprintco.com",                           "Base store URL — no trailing slash"],
    ["Product URL Pattern", "https://ghostprintco.com/products/{handle}",         "Replace {handle} with the product slug"],
    ["Instagram Handle",    "@ghostprintco",                                      "Used in social captions"],
    ["TikTok Handle",       "@ghostprintco",                                      "Leave blank if not active"],
    ["Price Point",         "Premium ($55–$150)",                                 "Informs tone of product copy"],
    [""],
    ["── Brand Identity ──", "", ""],
    ["Target Audience",
     "Tattoo artists, fine-art collectors, and streetwear enthusiasts aged 22–40. "
     "Predominantly male but inclusive. They buy selectively and wear intentionally. "
     "They follow artists before brands. They know Sullen. They know Supreme. "
     "They want something that sits between — more art-forward than Supreme, more street than Sullen. "
     "They do not need to be convinced. They either get it or they don't.",
     "Used to shape AI-generated copy"],
    ["Brand Voice",
     "Uncompromising. Art before commerce. Ghost Print Co. does not explain itself. "
     "Every piece is a limited screenprint run — when it's gone, it's gone, no restock. "
     "The voice is dark and restrained, like a tattoo artist who doesn't pitch, they just work. "
     "Speak to collectors, not shoppers. Never sell. Present.",
     "Core voice instruction passed to Claude on every run"],
    ["Tone Rules",
     "DO: Short declarative sentences. Present tense. Specific visual detail. Reference the craft. "
     "DON'T: Exclamation marks. Urgency tactics ('act now', 'selling fast'). The word 'luxury'. "
     "The word 'exclusive'. The word 'premium'. Emoji. Corporate language. Explaining the brand.",
     "Hard rules for all AI-generated content"],
    ["Visual Aesthetic",
     "Black-based garments. High-contrast screenprint in white, bone, and blood red. "
     "Tattoo flash meets gallery print. Heavy cotton. Structured silhouettes. "
     "Looks like it belongs in a tattoo studio and on a gallery wall simultaneously.",
     "Used for image alt text and social copy context"],
    ["Brand Influences",
     "Sullen Clothing — tattoo-art legitimacy, artist collaboration, collector culture. "
     "Supreme — strategic restraint, drop model, cultural capital through scarcity. "
     "Ghost Print Co. = Supreme's silence + Sullen's craft credibility.",
     "Reference only — do not name competitors in generated copy"],
    [""],
    ["── Hashtags ──", "", ""],
    ["Core Hashtags",
     "#ghostprintco #screenprint #ghostprint #streetwear #tattooculture #wearableart #darkstreet",
     "Always appended to every social post"],
    ["Drop Hashtags",
     "#limiteddrop #newdrop #collectorsonly #runof #screenprinted",
     "Added for new collection launch posts"],
    ["Niche Hashtags",
     "#tattooapparel #inkandthread #artdriven #premiumstreet #darkwear",
     "Rotate in for reach — do not use all at once"],
    [""],
    ["── AI Prompt Templates ──", "", "Edit these to tune Claude output. These are passed verbatim."],
    ["Product Description Prompt",
     "You are writing product copy for Ghost Print Co. — a premium screenprint streetwear brand rooted in tattoo culture and art-collector sensibility. "
     "Voice: uncompromising, restrained, art-forward. Never use hype language, urgency tactics, or the words 'luxury', 'exclusive', or 'premium'. "
     "Speak to someone who already understands the value of the craft — you are presenting, not selling. "
     "Write 2–3 sentences. Sentence 1: lead with the visual impact and artistic reference of the design. "
     "Sentence 2: garment construction — weight, fabric, print technique. "
     "Sentence 3: one short declarative brand statement. No call to action. No exclamation marks.",
     "Used for store product page body copy"],
    ["SEO Title Prompt",
     "Write an SEO-optimised product title for Ghost Print Co. "
     "Format: [Design Name] [Garment Type] — Ghost Print Co. "
     "Maximum 60 characters. The design name should reflect the most distinctive visual attribute. "
     "Do not use hype words.",
     "Used for store SEO title field"],
    ["SEO Description Prompt",
     "Write an SEO meta description for this Ghost Print Co. product. "
     "Under 155 characters. Include the garment type, the key visual detail, and 'Ghost Print Co.' "
     "Include one relevant search term naturally (e.g. 'screenprint tee', 'tattoo art hoodie', 'limited streetwear'). "
     "Natural sentence — not a keyword list.",
     "Used for store SEO description field"],
    ["Alt Text Prompt",
     "Write image alt text for a Ghost Print Co. product photo. "
     "Describe exactly what is visible: garment type, colourway, dominant print subject, any notable detail (distressing, texture, fit). "
     "Under 125 characters. Start with the garment type. Do not write 'Image of' or 'Photo of'.",
     "Used for product image accessibility and SEO"],
    ["Social Caption Prompt",
     "You are writing an Instagram caption for Ghost Print Co. "
     "Voice: dark, minimal, confident — like a tattoo artist who makes clothes, not a marketer who sells them. "
     "Write 3–4 short lines. No emojis. No hashtags (they go in the first comment). No exclamation marks. "
     "Never open with 'Introducing', 'Check out', or 'We're excited to'. "
     "Line 1: the visual or concept — what the piece is, stated plainly. "
     "Line 2: one specific detail about design or construction that signals craft knowledge. "
     "Line 3 (optional): a cultural statement or reference that resonates with collectors. "
     "Final line: a quiet, direct call to action. Examples: 'Link in bio.' / 'Drop live now.' / 'One run. No restock.'",
     "Used for Instagram feed posts — caption only, hashtags separate"],
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


def get_or_create_tab(ss: gspread.Spreadsheet, title: str, rows: int = 1000, cols: int = 26) -> gspread.Worksheet:
    existing = {ws.title: ws for ws in ss.worksheets()}
    if title in existing:
        return existing[title]
    return ss.add_worksheet(title=title, rows=rows, cols=cols)


def main():
    parser = argparse.ArgumentParser(
        description="Set up Ghost Print Co. product pipeline tabs inside a single workbook."
    )
    parser.add_argument("--sheet-id", required=True,
                        help="ID of the Google Sheet workbook shared with the service account as Editor.")
    args = parser.parse_args()

    creds = service_account.Credentials.from_service_account_file(
        settings.google_service_account_file, scopes=SCOPES
    )
    gc = gspread.authorize(creds)
    ss = gc.open_by_key(args.sheet_id)
    url = f"https://docs.google.com/spreadsheets/d/{args.sheet_id}/edit"

    print("Setting up Brand Profile tab...")
    ws_brand = get_or_create_tab(ss, "Brand Profile")
    setup_brand_profile(ws_brand)
    print("  Done.")

    print("Setting up Item Input tab...")
    ws_items = get_or_create_tab(ss, "Item Input")
    setup_item_input(ws_items)
    print("  Done.")

    print(f"""
Done. Workbook URL: {url}

Add to your .env:
  GHOST_PRINT_PIPELINE_SHEET_ID={args.sheet_id}

Next: Fill in the Brand Profile tab values, then add products to Item Input.
Set Status = Approved on any row to queue it for the N8N workflow.
""")


if __name__ == "__main__":
    main()
