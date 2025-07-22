import os
from baml_client import b
from typing import List, Tuple
from pdf2image import convert_from_path
from PIL import Image, ImageChops, ImageDraw
from PIL.Image import Image as PILImage
import numpy as np
import cv2
from baml_py import Image as BamlImage


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def pil_to_cv(image: PILImage) -> np.ndarray:
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


def classify_and_draw_layout_regions(
    reference: PILImage,
    mask: PILImage,
    min_area: int = 5000,
    label: bool = True
) -> PILImage:
    mask_np = np.array(mask.convert("L"))
    h, w = mask_np.shape

    # Clean up the mask a bit
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    cleaned = cv2.morphologyEx(mask_np, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    img = reference.copy()
    draw = ImageDraw.Draw(img)

    for cnt in contours:
        x, y, rw, rh = cv2.boundingRect(cnt)
        area = rw * rh
        # print(f"area: {area}")
        if area < min_area:
            continue

        cx, cy = x + rw // 2, y + rh // 2

        # Classify region based on position
        if cy < h * 0.25:
            region = "header"
        elif cy > h * 0.75:
            region = "footer"
        elif cx < w * 0.15:
            region = "left_margin"
        elif cx > w * 0.85:
            region = "right_margin"
        else:
            region = "body"

        # print(f"region: {region}, x: {x}, y: {y}, rw: {rw}, rh: {rh}")
        # print(f"cx: {cx}, cy: {cy}")
        # print(f"{cnt}")
        draw.rectangle([x, y, x + rw, y + rh], outline="green", width=2)
        if label:
            draw.text((x, y - 10), region, fill="green")


    print("--------------------------------")
    return img

def find_horizontal_bands(mask: PILImage, min_height: int = 15, min_ratio: float = 0.95):
    mask_np = np.array(mask.convert("L"))
    h, w = mask_np.shape

    row_sums = np.sum(mask_np == 255, axis=1) / w  # white = same
    same_rows = row_sums >= min_ratio

    bands = []
    start = None
    for i, val in enumerate(same_rows):
        if val and start is None:
            start = i
        elif not val and start is not None:
            if i - start >= min_height:
                bands.append((start, i))
            start = None
    if start is not None and h - start >= min_height:
        bands.append((start, h))

    return bands

def draw_horizontal_bands(img: PILImage, bands: List[Tuple[int, int]]) -> PILImage:
    out = img.copy()
    draw = ImageDraw.Draw(out)
    w, h = img.size
    for y1, y2 in bands:
        print(f"y1: {y1}, y2: {y2}")
        draw.rectangle([0, y1, w, y2], fill="black")
        draw.text((50, y1), f"same {y1}-{y2}", fill="white")
    return out



def compare_pages(
    reference_img: PILImage,
    compare_img: PILImage,
    index_ref: int,
    index_cmp: int,
    out_dir: str
) -> None:
    reference = reference_img.convert("RGB")
    compare = compare_img.convert("RGB")

    if reference.size != compare.size:
        print(f"[warn] Resizing page {index_cmp} to match reference size")
        compare = compare.resize(reference.size)

    # Step 1: Compute difference and invert so white = same
    diff = ImageChops.difference(reference, compare)
    sameness_mask = ImageChops.invert(diff.convert("L"))

    # Step 2: Threshold the mask (keep high-sameness pixels)
    binary_mask = sameness_mask.point(lambda p: 255 if p > 30 else 0).convert("1")

    # Step 3: Composite: show only same parts on white background
    white_bg = Image.new("RGB", reference.size, (255, 255, 255))
    result = Image.composite(reference, white_bg, binary_mask)

    # Step 4: Detect and draw horizontal sameness bands
    bands = find_horizontal_bands(sameness_mask)
    boxed_img = draw_horizontal_bands(reference, bands)
    print("--------------------------------")

    # Step 5: Save all outputs
    result.save(os.path.join(out_dir, f"exact_same_{index_ref}_{index_cmp}.png"))
    binary_mask.save(os.path.join(out_dir, f"mask_same_{index_ref}_{index_cmp}.png"))
    boxed_img.save(os.path.join(out_dir, f"boxed_common_{index_ref}_{index_cmp}.png"))

def main() -> None:
    images: List[PILImage] = convert_from_path("./example.pdf")
    ensure_dir("./data")
    ensure_dir("./data/same")

    for i, img in enumerate(images):
        img.save(f"./data/page_{i}.png")

    reference_index: int = 1
    reference_img: PILImage = images[reference_index]

    for i in range(reference_index + 1, len(images)):
        compare_pages(reference_img, images[i], reference_index, i, "./data/same")


if __name__ == "__main__":
    main()


def take_page(img: BamlImage):
    res = b.HasTransactions(page=img)
    if not (res.page_type == "transactions" and res.number_of_transactions > 0):
        return None
    # now get data
    return res.number_of_transactions