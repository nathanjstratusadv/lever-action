from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw


def create_reticle_icon(output_path: Path, size: int = 256) -> None:
    margin = size // 16
    corner_radius = size // 3
    img = Image.new("RGBA", (size, size), (255, 200, 150, 255))
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=corner_radius,
        fill=(255, 200, 150, 255),
    )

    center = size // 2
    thickness = max(size // 16, 4)
    inner_length = center // 3

    dark_blue = (30, 50, 120, 255)

    draw.line(
        [center, margin, center, center - inner_length],
        fill=dark_blue,
        width=thickness,
    )
    draw.line(
        [center, center + inner_length, center, size - margin],
        fill=dark_blue,
        width=thickness,
    )
    draw.line(
        [margin, center, center - inner_length, center],
        fill=dark_blue,
        width=thickness,
    )
    draw.line(
        [center + inner_length, center, size - margin, center],
        fill=dark_blue,
        width=thickness,
    )

    draw.ellipse(
        [
            center - inner_length // 2,
            center - inner_length // 2,
            center + inner_length // 2,
            center + inner_length // 2,
        ],
        outline=dark_blue,
        width=max(thickness // 2, 2),
    )

    for s in [256, 128, 64, 48, 32, 16]:
        resized = img.resize((s, s), Image.LANCZOS)
        resized.save(output_path.parent / f"reticle_{s}x{s}.png")

    img.save(
        output_path,
        format="ICO",
        sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)],
    )


if __name__ == "__main__":
    script_dir = Path(__file__).parent.resolve()
    output_file = script_dir / "reticle.ico"

    print(f"Creating reticle icon at {output_file}...")
    create_reticle_icon(output_file)
    print(f"Icon created successfully: {output_file}")
