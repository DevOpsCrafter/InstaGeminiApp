"""
Instagram Carousel Post Bot — Multiple Insta IDs

Generates a multi-slide carousel (5 images + 1 caption) for a given Instagram account.
Designed to run from GitHub Actions with INSTA_ID (e.g. projectwuhu, sacredwhisperers, revivalofwisdom).
Reuses daily_bot's image generation and email stack.
"""

import os
import json
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

# Optional theme hints per Insta ID for variety
INSTA_ID_THEMES = {
    "projectwuhu": "creative projects, inspiration, minimal wisdom, modern spirituality",
    "sacredwhisperers": "sacred wisdom, ancient knowledge, meditation, soulful guidance",
    "revivalofwisdom": "revival of classic wisdom, philosophy, timeless insights, contemplation",
}


def generate_carousel_content(insta_id: str):
    """
    Generate one caption and CAROUSEL_SLIDES image prompts for a cohesive carousel via Gemini.
    Returns (list of image prompts, full caption string, meta dict with hashtags).
    """
    import google.generativeai as genai

    theme_hint = INSTA_ID_THEMES.get(insta_id.lower(), "wisdom, inspiration, and reflection")
    handle = f"@{insta_id}"

    prompt = f"""
You are creating an Instagram CAROUSEL post for the account {handle}.
Theme tone: {theme_hint}.

Generate a JSON object with these keys:

- "image_prompts": An array of exactly {CAROUSEL_SLIDES} prompts for an AI image generator.
  * Each prompt ~300-500 chars: vivid scene, same art style across all slides (e.g. "ethereal", "by Peter Mohrbacher", "cosmic surrealism").
  * Tell a subtle visual story across the slides (e.g. journey from dawn to stars, or one concept in five variations).
  * Colors: cohesive palette (e.g. cosmic purples, golds, teals).
  * End each with: "masterpiece, 8K, hyperdetailed, square 1:1, no text, no watermarks"

- "caption": One Instagram caption (≤300 chars) for the whole carousel.
  * Hook in the first line. Weave in the account's vibe ({theme_hint}).
  * End with a soft CTA (e.g. "Save this for later" or "Which slide speaks to you?")
  * Use 2-3 emojis.

- "hashtags": Array of exactly 5 hashtags relevant to the theme.

Return ONLY valid JSON. No markdown fences.
Example structure:
{{
  "image_prompts": ["First slide prompt...", "Second...", "Third...", "Fourth...", "Fifth..."],
  "caption": "Your opening line. Deeper message. ✨ Save for later.",
  "hashtags": ["#Wisdom", "#Spirituality", "#Mindfulness", "#Inspiration", "#Reflection"]
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
        prompts.append(prompts[-1] if prompts else "Ethereal cosmic scene, 1:1, no text, masterpiece")

    caption_part = (data.get("caption") or data.get("CAPTION") or "").strip()
    hashtags_list = data.get("hashtags") or data.get("HASHTAGS") or []
    if isinstance(hashtags_list, str):
        hashtags_list = [h.strip() for h in hashtags_list.replace(",", " ").split() if h.strip()]
    normalized = []
    for h in hashtags_list:
        h = h.strip()
        if not h:
            continue
        if not h.startswith("#"):
            h = f"#{h}"
        normalized.append(h)
    top5 = normalized[:5]
    while len(top5) < 5:
        top5.append("#Wisdom")
    hashtags_str = " ".join(top5)
    full_caption = f"{caption_part}\n\n{hashtags_str}".strip()

    return prompts, full_caption, {"hashtags": top5}


def send_carousel_email(images_data: list, caption: str, insta_id: str):
    """Send one email with all carousel images attached and posting instructions."""
    msg = MIMEMultipart()
    msg["From"] = YOUR_EMAIL
    msg["To"] = YOUR_EMAIL
    handle = f"@{insta_id}"
    msg["Subject"] = f"Instagram Carousel Ready for {handle} — {len(images_data)} slides"

    body = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <h2 style="color: #2D3748;">📸 Carousel Post Ready — {handle}</h2>
    <p>Your {len(images_data)}-slide carousel has been generated. Post in order (slide 1 → {len(images_data)}).</p>
    <div style="background: #EDF2F7; padding: 20px; border-radius: 8px; margin: 20px 0;">
        <h3 style="color: #2D3748; margin-top: 0;">Caption & Hashtags</h3>
        <p style="white-space: pre-wrap; color: #4A5568;">{caption}</p>
    </div>
    <div style="background: #E6FFFA; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #38B2AC;">
        <h3 style="color: #234E52; margin-top: 0;">📱 How to Post as Carousel</h3>
        <ol style="color: #285E61;">
            <li>Open Instagram → tap <strong>+</strong> → Post</li>
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
        part = MIMEImage(img_bytes, name=f"carousel_slide_{i}.jpg")
        msg.attach(part)

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(YOUR_EMAIL, EMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()
    print(f"Email sent for {handle} with {len(images_data)} slides.")


def main():
    parser = argparse.ArgumentParser(description="Instagram Carousel Bot — multiple Insta IDs")
    parser.add_argument("--dry-run", action="store_true", help="Only generate content (no images, no email)")
    parser.add_argument("--mock", action="store_true", help="Use mock carousel content (no Gemini)")
    args = parser.parse_args()

    insta_id = os.environ.get("INSTA_ID", "").strip()
    if not insta_id:
        print("ERROR: INSTA_ID environment variable is required (e.g. projectwuhu, sacredwhisperers, revivalofwisdom)")
        exit(1)

    if not args.mock and not all([GEMINI_API_KEY, YOUR_EMAIL, EMAIL_PASSWORD]):
        print("ERROR: Missing credentials. Set GEMINI_API_KEY, YOUR_EMAIL, EMAIL_PASSWORD (and POLLINATION_API_KEY for images).")
        exit(1)

    try:
        if args.mock:
            prompts = [
                "Ethereal cosmic dawn, soft gold and purple, 1:1, no text, masterpiece",
            ] * CAROUSEL_SLIDES
            caption = "Wisdom in five frames. ✨ Save for later.\n\n#Wisdom #Spirituality #Mindfulness #Inspiration #Reflection"
            meta = {"hashtags": ["#Wisdom", "#Spirituality", "#Mindfulness", "#Inspiration", "#Reflection"]}
        else:
            prompts, caption, meta = generate_carousel_content(insta_id)
        print(f"Caption:\n{caption}")

        if args.dry_run:
            print(f"Dry-run: would generate {len(prompts)} images and send email for @{insta_id}")
            exit(0)

        images_data = []
        for i, p in enumerate(prompts, start=1):
            print(f"Generating slide {i}/{len(prompts)}...")
            raw = generate_image(p)
            processed = process_for_instagram(raw)
            images_data.append(processed)

        send_carousel_email(images_data, caption, insta_id)
        print(f"\n✨ Carousel for @{insta_id} done. Check your email.")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
