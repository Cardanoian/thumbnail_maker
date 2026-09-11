"""Create Windows .ico for the packaged app."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    assets = root / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    output = assets / "icon.ico"

    size = 256
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    margin = 16
    draw.rounded_rectangle(
        [margin, margin, size - margin - 1, size - margin - 1],
        radius=48,
        fill=(37, 99, 235, 255),
    )
    try:
        font = ImageFont.truetype("arial.ttf", 110)
    except OSError:
        font = ImageFont.load_default()
    text = "20"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size - text_width) / 2 - bbox[0]
    y = (size - text_height) / 2 - bbox[1]
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
    image.save(output, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (256, 256)])
    print(output)


if __name__ == "__main__":
    main()
