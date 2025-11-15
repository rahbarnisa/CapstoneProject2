from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


DATA = [
    (
        "step1_upload",
        "Step 1 · Upload Voice & Choose Models",
        "Audio file: sunrise_idea.m4a\n"
        "Transcriber: gpt-4o-mini-transcribe\n"
        "Prompt model: gpt-4o-mini\n"
        "Image model: gpt-image-1 (1024x1024)",
    ),
    (
        "step2_prompt",
        "Step 2 · Transcript & Prompt",
        "Transcript: \"Paint a calm sunrise over alpine mountains with mist.\"\n"
        "Generated prompt highlights mood, lighting, environment, and style.",
    ),
    (
        "step3_result",
        "Step 3 · Generated Artwork",
        "Final image rendered via gpt-image-1.\n"
        "UI also lists models used and makes the PNG downloadable.",
    ),
]


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()


def create_screenshots():
    base_dir = Path("docs/screenshots")
    base_dir.mkdir(parents=True, exist_ok=True)

    title_font = _load_font(48)
    body_font = _load_font(32)

    for slug, title, body in DATA:
        img = Image.new("RGB", (1400, 900), "white")
        draw = ImageDraw.Draw(img)

        draw.rectangle([(0, 0), (1400, 120)], fill="#f0f2f6")
        draw.text((40, 35), title, fill="#303952", font=title_font)

        text_y = 180
        for line in body.split("\n"):
            draw.text((40, text_y), line, fill="#1e272e", font=body_font)
            text_y += 60

        img.save(base_dir / f"{slug}.png")
        print(f"Saved {slug}.png")


if __name__ == "__main__":
    create_screenshots()

