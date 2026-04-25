"""
Fix Items tab headers and populate Prompts tab with category-specific prompts.
Run once, then delete.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from google.oauth2 import service_account
import gspread

from config import settings

SHEET_ID = "1HUajSpYtnnP2iM4vWCR8dJxGeAl947FTzH7SoTNmvOU"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# ── Updated Items headers ─────────────────────────────────────────────────────
ITEMS_HEADERS = [
    # ── Input (user fills) ──────────────────────────────────────────
    "SKU",
    "Product Name",
    "Category",           # t-shirt | hoodie | hat | tote | other
    "Base Colour",
    "Price",
    "Sizes Available",    # comma-separated: S,M,L,XL,XXL
    "Available Quantity", # total stock for this product
    "Raw Notes",          # design notes from the artist
    "Image URL 1",
    "Image URL 2",
    "Image URL 3",
    "Status",             # Draft | Approved | Processing | Done | Error
    # ── Output (N8N fills) ──────────────────────────────────────────
    "Enhanced Title",
    "Enhanced Description",
    "SEO Title",
    "SEO Description",
    "Image Alt Text",
    "Social Caption",
    "Social Hashtags",
    "Product URL",
    "Handle",             # URL slug — was "Shopify Handle"
    "Error Notes",
]

# ── Category-specific Claude prompts ─────────────────────────────────────────
PROMPTS_ROWS = [
    [
        "t-shirt",
        (
            "You are writing product copy for a Ghost Print Co. screenprint t-shirt. "
            "Voice: uncompromising, art-forward, collector-focused. No hype, no urgency. "
            "Write 2-3 sentences. "
            "Sentence 1: describe the print subject and its visual impact — this is the centrepiece. "
            "Sentence 2: garment quality — reference the cotton weight, screenprint technique, and fit. "
            "Sentence 3: one short declarative brand statement. No call to action."
        ),
        (
            "Write an Instagram caption for a Ghost Print Co. t-shirt drop. "
            "Voice: dark, minimal, art-forward — like a tattoo artist who makes clothes, not a marketer. "
            "3-4 short lines. No emojis. No exclamation marks. "
            "Line 1: the design concept or reference, stated plainly. "
            "Line 2: one specific craft detail — ink coverage, print registration, or fabric weight. "
            "Line 3 (optional): a cultural statement that resonates with collectors. "
            "Final line: a quiet call to action. e.g. 'Link in bio.' or 'One run. No restock.'"
        ),
        "Default category for most Ghost Print Co. drops",
    ],
    [
        "hoodie",
        (
            "You are writing product copy for a Ghost Print Co. screenprint hoodie. "
            "Voice: uncompromising, art-forward. "
            "Write 2-3 sentences. "
            "Sentence 1: the print — design subject, placement, and visual weight. "
            "Sentence 2: construction — fabric weight (oz), hood structure, kangaroo pocket, ribbing. "
            "Sentence 3: brand statement."
        ),
        (
            "Write an Instagram caption for a Ghost Print Co. hoodie drop. "
            "Dark, minimal, art-forward. 3-4 lines. No emojis. No exclamation marks. "
            "Open with the visual concept or design reference. "
            "Include one construction detail that signals quality. "
            "Close with a quiet, direct call to action."
        ),
        "Heavyweight hoodies — key selling point is construction quality",
    ],
    [
        "hat",
        (
            "You are writing product copy for a Ghost Print Co. hat. "
            "Voice: minimal, collector-focused. "
            "Write 2-3 sentences. "
            "Sentence 1: the design or emblem and what it references — treat it as a piece, not an accessory. "
            "Sentence 2: construction — structured or unstructured, material, closure type. "
            "Sentence 3: brand statement."
        ),
        (
            "Write an Instagram caption for a Ghost Print Co. hat. "
            "3 lines maximum. Treat it as a print first, a hat second. "
            "No emojis. No exclamation marks. "
            "Line 1: the design. Line 2: one detail. Final line: 'Link in bio.'"
        ),
        "Structured snapbacks and fitted caps",
    ],
    [
        "tote",
        (
            "You are writing product copy for a Ghost Print Co. screenprint tote bag. "
            "Voice: minimal. Write 2 sentences. "
            "Sentence 1: the print and what it communicates. "
            "Sentence 2: construction — canvas weight (oz), handle drop length, print placement."
        ),
        (
            "Write an Instagram caption for a Ghost Print Co. tote. "
            "2-3 lines. Treat it as a print first, a bag second. "
            "Minimal copy. No emojis. Close with 'Link in bio.'"
        ),
        "Heavy canvas totes — art object framing",
    ],
    [
        "other",
        (
            "You are writing product copy for a Ghost Print Co. item. "
            "Voice: dark, minimal, art-forward. "
            "Write 2-3 sentences. "
            "Sentence 1: what makes this piece visually distinct. "
            "Sentence 2: construction and materials. "
            "Sentence 3: brand statement."
        ),
        (
            "Write an Instagram caption for a Ghost Print Co. product. "
            "3 lines. Focus on the visual first. "
            "No emojis. No exclamation marks. Close with 'Link in bio.'"
        ),
        "Fallback for accessories, collabs, or misc items",
    ],
]


def main():
    creds = service_account.Credentials.from_service_account_file(
        settings.google_service_account_file, scopes=SCOPES
    )
    gc = gspread.authorize(creds)
    ss = gc.open_by_key(SHEET_ID)
    tabs = {ws.title: ws for ws in ss.worksheets()}

    # ── Fix Items headers ─────────────────────────────────────────────────────
    ws_items = tabs["Items"]
    ws_items.update("A1", [ITEMS_HEADERS], value_input_option="USER_ENTERED")
    ws_items.format("A1:V1", {
        "backgroundColor": {"red": 0.47, "green": 0.08, "blue": 0.17},
        "textFormat": {"foregroundColor": {"red": 1, "green": 1, "blue": 1}, "bold": True},
    })
    # Status column is now col L (12)
    ws_items.format("L1:L200", {"backgroundColor": {"red": 1.0, "green": 0.95, "blue": 0.8}})
    print("  Updated: Items headers")

    # ── Populate Prompts ──────────────────────────────────────────────────────
    ws_prompts = tabs["Prompts"]
    ws_prompts.clear()
    ws_prompts.update("A1", [["category_key", "product_page_prompt", "social_caption_prompt", "notes"]],
                      value_input_option="USER_ENTERED")
    ws_prompts.update("A2", PROMPTS_ROWS, value_input_option="USER_ENTERED")
    ws_prompts.freeze(rows=1)
    ws_prompts.format("A1:D1", {
        "backgroundColor": {"red": 0.47, "green": 0.08, "blue": 0.17},
        "textFormat": {"foregroundColor": {"red": 1, "green": 1, "blue": 1}, "bold": True},
    })
    print("  Populated: Prompts (5 categories)")

    print("\nDone.")


if __name__ == "__main__":
    main()
