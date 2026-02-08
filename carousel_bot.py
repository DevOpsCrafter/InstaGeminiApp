"""
Instagram Carousel Post Bot — Astroboli only

Generates one 5-slide carousel for Astroboli's Instagram. Each slide has
MEANINGFUL TEXT ON THE IMAGE (like @projectwuhu, @sacredwhisperers, @revivalofwisdom):
short wisdom/quote lines that are interesting to read, overlaid on cosmic imagery.
One run = one carousel ready to post directly.
"""

import os
import random
import argparse
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

from PIL import Image, ImageDraw, ImageFont

# Reuse daily_bot components
from daily_bot import (
    GEMINI_API_KEY,
    YOUR_EMAIL,
    EMAIL_PASSWORD,
    POLLINATION_API_KEY,
    _extract_json_from_text,
    _clean_image_prompt,
    generate_image,
    process_for_instagram,
)
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import smtplib

# Number of carousel slides (Instagram allows 2–10)
CAROUSEL_SLIDES = 5

# Reference accounts: they put SHORT, MEANINGFUL TEXT ON EACH SLIDE — wisdom quotes
# that stop the scroll and are interesting to read. One idea per slide.
STYLE_REFERENCE_ACCOUNTS = (
    "@projectwuhu — creative projects, minimal wisdom, SHORT QUOTES ON IMAGE, modern spirituality, clean text overlay\n"
    "@sacredwhisperers — sacred wisdom, ancient knowledge, MEANINGFUL PHRASES ON EACH SLIDE, meditation, soulful\n"
    "@revivalofwisdom — revival of classic wisdom, QUOTE-STYLE TEXT ON IMAGES, philosophy, timeless one-liners"
)


def _get_carousel_font(size: int):
    """Load a bold, readable font for text overlay. Tries system fonts, falls back to default."""
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf",
        "C:\\Windows\\Fonts\\segoeuib.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in candidates:
        if os.path.isfile(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _wrap_text(draw, text: str, font, max_width: int) -> list:
    """Wrap text into lines that fit within max_width pixels."""
    words = text.split()
    lines = []
    current = []
    for w in words:
        test = " ".join(current + [w])
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current.append(w)
        else:
            if current:
                lines.append(" ".join(current))
            current = [w]
    if current:
        lines.append(" ".join(current))
    return lines[:3]  # Max 3 lines per slide


def overlay_text_on_slide(image_bytes: bytes, text_line: str) -> bytes:
    """
    Overlay one short wisdom/quote line on the image. High contrast, centered,
    readable — like projectwuhu / sacredwhisperers / revivalofwisdom.
    """
    img = Image.open(BytesIO(image_bytes)).convert("RGB")
    w, h = img.size
    draw = ImageDraw.Draw(img)

    # Font: large enough to read on mobile (guideline 36px+ for headlines)
    font_size = max(42, min(72, w // 12))
    font = _get_carousel_font(font_size)

    # Wrap to fit (leave margin)
    margin = w // 8
    max_text_width = w - 2 * margin
    lines = _wrap_text(draw, text_line.strip(), font, max_text_width)
    if not lines:
        lines = [text_line.strip()[:50]]

    # Line height and total block height
    line_height = int(font_size * 1.35)
    total_height = len(lines) * line_height
    y_start = (h - total_height) // 2

    # Semi-transparent dark bar behind text for readability (like wisdom carousel accounts)
    padding = w // 24
    bar_top = y_start - padding
    bar_bottom = y_start + total_height + padding
    bar_left = margin
    bar_right = w - margin
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rounded_rectangle(
        [bar_left, bar_top, bar_right, bar_bottom],
        radius=12,
        fill=(0, 0, 0, 180),
        outline=(255, 255, 255, 80),
    )
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, overlay)
    img = img.convert("RGB")
    draw = ImageDraw.Draw(img)

    # Draw text (white, centered)
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        tx = (w - tw) // 2
        ty = y_start + i * line_height
        # Slight shadow for readability
        draw.text((tx + 1, ty + 1), line, font=font, fill=(0, 0, 0))
        draw.text((tx, ty), line, font=font, fill=(255, 255, 255))
    out = BytesIO()
    img.save(out, format="JPEG", quality=95, optimize=True)
    out.seek(0)
    return out.getvalue()


def generate_carousel_content():
    """
    Generate background prompts, SLIDE TEXTS (meaningful quotes on each image),
    caption, and hashtags. Style: like projectwuhu, sacredwhisperers, revivalofwisdom
    — they put SHORT, INTERESTING-TO-READ text ON every slide.
    """
    import google.generativeai as genai

    brand_variations = [
        "Astro Boli",
        "AstroBoli AI",
        "Astro AI",
        "AstroBoli",
        "Astro Boli AI",
    ]
    brand_name = random.choice(brand_variations)
    brand_hashtag = brand_name.replace(" ", "")

    prompt = f"""
You create Instagram CAROUSEL posts for Astroboli (brand: {brand_name}, site: astroboli.com).

CRITICAL — Study these accounts: @projectwuhu, @sacredwhisperers, @revivalofwisdom. They put MEANINGFUL, SHORT TEXT DIRECTLY ON EACH SLIDE so users stop and read. Each slide has one wisdom quote or impactful line ON THE IMAGE — not just a caption. Your job is to write that kind of content: interesting, readable, shareable lines that go ON each of the 5 images.

{STYLE_REFERENCE_ACCOUNTS}

Rules for the text ON the images:
- One short wisdom/quote line PER SLIDE (10–15 words max per slide). This text will be overlaid on the image.
- Meaningful: cosmic guidance, astrology insight, reflection, manifestation, or timeless wisdom — Astroboli vibe.
- Tone: contemplative, gentle, memorable. Something users would save or screenshot.
- No hashtags in the slide text. No "Visit astroboli.com" on the image (that goes in caption only).
- Each line should stand alone and feel complete.

Generate a JSON object with these keys:

- "image_prompts": Array of exactly {CAROUSEL_SLIDES} prompts for an AI image generator (BACKGROUND only; text will be added by us).
  * Same art style across all: ethereal cosmic, "by Peter Mohrbacher" or cosmic surrealism, deep purples/golds/teals.
  * Subtle visual story (e.g. dawn to stars). NO text in the image — we overlay text separately.
  * End each with: "masterpiece, 8K, hyperdetailed, square 1:1, no text, no watermarks"

- "slide_texts": Array of exactly {CAROUSEL_SLIDES} SHORT LINES to be OVERLAID ON EACH SLIDE. These are the meaningful quotes/wisdom that appear ON the image (like projectwuhu, sacredwhisperers, revivalofwisdom). Each string 10–15 words max, impactful, interesting to read. Examples of the STYLE: "The stars don't decide your path. You do." / "What you seek is seeking you." / "Your intuition is the universe whispering." — Astroboli/cosmic themed.

- "caption": One Instagram caption (≤300 chars) for the whole carousel. Hook + CTA "✨ Visit astroboli.com for your reading" or "Save this for later." Use 2–3 emojis.

- "hashtags": Array of exactly 5. First: #{brand_hashtag}. Rest: #Astrology #CosmicEnergy #Spirituality #ZodiacSigns #Manifestation (or similar).

Return ONLY valid JSON. No markdown fences.
Example structure:
{{
  "image_prompts": ["Ethereal cosmic dawn...", "..."],
  "slide_texts": [
    "The stars don't decide your path. You do.",
    "What you seek is seeking you.",
    "Your intuition is the universe whispering.",
    "Trust the timing of your life.",
    "The cosmos crowns those who listen."
  ],
  "caption": "Five reminders from the cosmos. ✨ Save for when you need them. Visit astroboli.com for your reading 🌙",
  "hashtags": ["#{brand_hashtag}", "#Astrology", "#CosmicEnergy", "#Spirituality", "#ZodiacSigns"]
}}
"""

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    text = response.text

    data = _extract_json_from_text(text) or {}
    if not data:
        raise ValueError("No JSON found in Gemini output for carousel")

    raw_prompts = data.get("image_prompts") or []
    if isinstance(raw_prompts, str):
        raw_prompts = [p.strip() for p in raw_prompts.split("\n") if p.strip()]
    prompts = [_clean_image_prompt(p) for p in raw_prompts[:CAROUSEL_SLIDES]]
    while len(prompts) < CAROUSEL_SLIDES:
        prompts.append(
            prompts[-1]
            if prompts
            else "Ethereal cosmic scene, 1:1, no text, masterpiece"
        )

    # Slide texts = meaningful lines ON each image (required)
    raw_slides = data.get("slide_texts") or []
    if isinstance(raw_slides, str):
        raw_slides = [s.strip() for s in raw_slides.split("\n") if s.strip()]
    slide_texts = [str(s).strip()[:200] for s in raw_slides[:CAROUSEL_SLIDES]]
    while len(slide_texts) < CAROUSEL_SLIDES:
        slide_texts.append(
            slide_texts[-1] if slide_texts else "The cosmos speaks to those who listen."
        )

    caption_part = (data.get("caption") or data.get("CAPTION") or "").strip()
    hashtags_list = data.get("hashtags") or data.get("HASHTAGS") or []
    if isinstance(hashtags_list, str):
        hashtags_list = [
            h.strip() for h in hashtags_list.replace(",", " ").split() if h.strip()
        ]
    normalized = []
    for h in hashtags_list:
        h = h.strip()
        if not h:
            continue
        if not h.startswith("#"):
            h = f"#{h}"
        normalized.append(h)
    top5 = normalized[:5]
    if "#astroboliai" not in [t.lower() for t in top5]:
        top5 = [f"#{brand_hashtag}"] + [t for t in top5 if t.lower() != "#astroboliai"]
    top5 = top5[:5]
    while len(top5) < 5:
        top5.append("#Astrology")
    hashtags_str = " ".join(top5)
    if "astroboli" not in caption_part.lower():
        caption_part = f"{caption_part.strip()} — Visit astroboli.com"
    full_caption = f"{caption_part}\n\n{hashtags_str}".strip()

    return prompts, slide_texts, full_caption, {"hashtags": top5}


def send_carousel_email(images_data: list, caption: str):
    """Send one email with all carousel images (with text on each) and instructions."""
    msg = MIMEMultipart()
    msg["From"] = YOUR_EMAIL
    msg["To"] = YOUR_EMAIL
    msg["Subject"] = "Astroboli Carousel Ready — Post to Instagram"

    body = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <h2 style="color: #2D3748;">📸 Astroboli Carousel Ready</h2>
    <p>One carousel ({len(images_data)} slides) with <strong>meaningful text on each image</strong> — ready to post to Astroboli Instagram. Order: slide 1 → {len(images_data)}.</p>
    <div style="background: #EDF2F7; padding: 20px; border-radius: 8px; margin: 20px 0;">
        <h3 style="color: #2D3748; margin-top: 0;">Caption & Hashtags</h3>
        <p style="white-space: pre-wrap; color: #4A5568;">{caption}</p>
    </div>
    <div style="background: #E6FFFA; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #38B2AC;">
        <h3 style="color: #234E52; margin-top: 0;">📱 How to Post as Carousel</h3>
        <ol style="color: #285E61;">
            <li>Open Instagram (Astroboli account) → tap <strong>+</strong> → Post</li>
            <li>Select <strong>Multiple</strong> and add the attached images in order (slide 1, 2, 3, 4, 5)</li>
            <li>Tap Next → Next</li>
            <li>Paste the caption above</li>
            <li>Tap <strong>Share</strong></li>
        </ol>
    </div>
    <p style="color: #718096; font-size: 14px;">Attachments: {len(images_data)} images (1080×1080, text on each)</p>
</body>
</html>
"""
    msg.attach(MIMEText(body, "html"))

    for i, img_bytes in enumerate(images_data, start=1):
        part = MIMEImage(img_bytes, name=f"astroboli_carousel_slide_{i}.jpg")
        msg.attach(part)

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(YOUR_EMAIL, EMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()
    print(f"Email sent: Astroboli carousel with {len(images_data)} slides (text on each).")


def main():
    parser = argparse.ArgumentParser(
        description="Astroboli Instagram Carousel Bot — meaningful text on each slide"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only generate content (no images, no email)",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use mock carousel content (no Gemini)",
    )
    args = parser.parse_args()

    if not args.mock and not all([GEMINI_API_KEY, YOUR_EMAIL, EMAIL_PASSWORD]):
        print(
            "ERROR: Missing credentials. Set GEMINI_API_KEY, YOUR_EMAIL, EMAIL_PASSWORD (and POLLINATION_API_KEY for images)."
        )
        exit(1)

    try:
        if args.mock:
            prompts = [
                "Ethereal cosmic dawn, soft gold and purple, 1:1, no text, masterpiece",
            ] * CAROUSEL_SLIDES
            slide_texts = [
                "The stars don't decide your path. You do.",
                "What you seek is seeking you.",
                "Your intuition is the universe whispering.",
                "Trust the timing of your life.",
                "The cosmos crowns those who listen.",
            ]
            caption = (
                "Five reminders from the cosmos. ✨ Visit astroboli.com for your reading.\n\n"
                "#AstroboliAI #Astrology #CosmicEnergy #Spirituality #ZodiacSigns"
            )
            meta = {"hashtags": ["#AstroboliAI", "#Astrology", "#CosmicEnergy", "#Spirituality", "#ZodiacSigns"]}
        else:
            prompts, slide_texts, caption, meta = generate_carousel_content()
        print("Slide texts (on each image):")
        for i, t in enumerate(slide_texts, 1):
            print(f"  {i}. {t}")
        print(f"\nCaption:\n{caption}")

        if args.dry_run:
            print(
                f"Dry-run: would generate {len(prompts)} images, overlay text on each, and send one Astroboli carousel email."
            )
            exit(0)

        images_data = []
        for i, (p, text_line) in enumerate(zip(prompts, slide_texts), start=1):
            print(f"Generating slide {i}/{len(prompts)} (text: \"{text_line[:40]}...\")...")
            raw = generate_image(p)
            processed = process_for_instagram(raw)
            with_text = overlay_text_on_slide(processed, text_line)
            images_data.append(with_text)

        send_carousel_email(images_data, caption)
        print("\n✨ Astroboli carousel done (meaningful text on each slide). Check your email and post to Instagram.")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
