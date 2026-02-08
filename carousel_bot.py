"""
Instagram Carousel Post Bot — Astroboli only

Generates one 5-slide carousel (images + caption) for Astroboli's Instagram.
Content style is inspired by wisdom/quote carousel accounts: @projectwuhu,
@sacredwhisperers, @revivalofwisdom — minimal, contemplative, shareable —
but themed for Astroboli (cosmic, astrology, mystical, astroboli.com).
One run = one carousel ready to post directly as an Instagram carousel.
"""

import os
import random
import argparse
from dotenv import load_dotenv

load_dotenv()

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

# Reference accounts: content style to emulate (wisdom, sacred, revival — not for posting to them)
STYLE_REFERENCE_ACCOUNTS = (
    "@projectwuhu — creative projects, minimal wisdom, modern spirituality, clean visuals\n"
    "@sacredwhisperers — sacred wisdom, ancient knowledge, meditation, soulful guidance, contemplative\n"
    "@revivalofwisdom — revival of classic wisdom, philosophy, timeless insights, quote-style"
)


def generate_carousel_content():
    """
    Generate one caption and CAROUSEL_SLIDES image prompts for an Astroboli carousel.
    Style: like projectwuhu, sacredwhisperers, revivalofwisdom (wisdom carousels, minimal, shareable).
    Theme: Astroboli — cosmic, astrology, mystical, astroboli.com.
    Returns (list of image prompts, full caption string, meta dict with hashtags).
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
Content must be in the STYLE of these wisdom/quote carousel accounts — study their vibe and copy that approach:

{STYLE_REFERENCE_ACCOUNTS}

What they do well: short wisdom, one idea per slide, contemplative, shareable, "save for later", minimal text feel, cohesive visual story. You are NOT posting to those accounts; you are writing for Astroboli in that same style.

Theme for this carousel: Astroboli — cosmic, astrology, zodiac, mystical, celestial guidance. Blend: wisdom-carousel style (like the references) + Astroboli's cosmic/astrology theme.

Generate a JSON object with these keys:

- "image_prompts": An array of exactly {CAROUSEL_SLIDES} prompts for an AI image generator.
  * Each prompt ~300-500 chars: vivid cosmic/astrology scene, SAME art style across all slides (e.g. "ethereal", "by Peter Mohrbacher", "cosmic surrealism").
  * Tell a subtle visual story across the slides (e.g. dawn to stars, or one cosmic concept in five variations).
  * Colors: cohesive Astroboli palette — cosmic purples, celestial golds, ethereal teals.
  * End each with: "masterpiece, 8K, hyperdetailed, square 1:1, no text, no watermarks"

- "caption": One Instagram caption (≤300 chars) for the whole carousel.
  * Hook in the first line. Wisdom/contemplative tone like the reference accounts, but Astroboli/cosmic.
  * End with CTA: "✨ Visit astroboli.com for your reading" or "Save this for later" or "Which slide speaks to you?"
  * Use 2-3 emojis (e.g. 🌙 ✨ 🔮).

- "hashtags": Array of exactly 5 hashtags. First: #{brand_hashtag}. Rest: #Astrology #CosmicEnergy #Spirituality #ZodiacSigns #Manifestation (or similar).

Return ONLY valid JSON. No markdown fences.
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

    return prompts, full_caption, {"hashtags": top5}


def send_carousel_email(images_data: list, caption: str):
    """Send one email with all carousel images and instructions to post to Astroboli's Instagram."""
    msg = MIMEMultipart()
    msg["From"] = YOUR_EMAIL
    msg["To"] = YOUR_EMAIL
    msg["Subject"] = "Astroboli Carousel Ready — Post to Instagram"

    body = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <h2 style="color: #2D3748;">📸 Astroboli Carousel Ready</h2>
    <p>One carousel ({len(images_data)} slides) for <strong>Astroboli</strong>. Post in order (slide 1 → {len(images_data)}) to your Astroboli Instagram.</p>
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
    <p style="color: #718096; font-size: 14px;">Attachments: {len(images_data)} images (1080×1080 each)</p>
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
    print(f"Email sent: Astroboli carousel with {len(images_data)} slides.")


def main():
    parser = argparse.ArgumentParser(
        description="Astroboli Instagram Carousel Bot — single post for Astroboli"
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
            caption = (
                "Wisdom in five frames. ✨ Visit astroboli.com for your reading.\n\n"
                "#AstroboliAI #Astrology #CosmicEnergy #Spirituality #ZodiacSigns"
            )
            meta = {
                "hashtags": [
                    "#AstroboliAI",
                    "#Astrology",
                    "#CosmicEnergy",
                    "#Spirituality",
                    "#ZodiacSigns",
                ]
            }
        else:
            prompts, caption, meta = generate_carousel_content()
        print(f"Caption:\n{caption}")

        if args.dry_run:
            print(
                f"Dry-run: would generate {len(prompts)} images and send one Astroboli carousel email."
            )
            exit(0)

        images_data = []
        for i, p in enumerate(prompts, start=1):
            print(f"Generating slide {i}/{len(prompts)}...")
            raw = generate_image(p)
            processed = process_for_instagram(raw)
            images_data.append(processed)

        send_carousel_email(images_data, caption)
        print("\n✨ Astroboli carousel done. Check your email and post to Instagram.")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
