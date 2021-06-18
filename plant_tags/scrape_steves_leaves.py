"""
Scrape stevesleaves.com
"""
import json
from pathlib import Path
import re
import shutil
from argparse import ArgumentParser

import requests
import lxml.html
from tqdm import tqdm


def load_info(base_dir):
    """
    Load info json
    """
    info_path = base_dir / Path("stevesleaves.json")
    try:
        info = json.load(info_path.open("r"))
    except FileNotFoundError:
        info = dict()
    return info


def save_info(info, base_dir):
    """
    Save info json
    """
    info_path = base_dir / Path("stevesleaves.json")
    json.dump(info, info_path.open("w"), indent=2)


def discover_links(info):
    """
    Discover plant links
    """
    discover_url = "https://stevesleaves.com/collections/all"
    n_pages = 52
    plant_links = list()
    for page_number in tqdm(range(1, n_pages + 1), desc="discovering links"):
        url = discover_url + f"?page={page_number}"
        html = requests.get(url)
        doc = lxml.html.fromstring(html.content)
        links = doc.xpath("//a/@href")
        links = [
            "https://stevesleaves.com" + link
            for link in links
            if re.match(r"\/collections\/all\/products\/[\w-]+", link)
        ]
        plant_links.extend(links)

    if info.get("plant_links"):
        info["plant_links"].extend(plant_links)
        info["plant_links"] = list(set(info["plant-links"]))
    else:
        info["plant_links"] = list(set(plant_links))
    return info


def visit_link(link, base_dir):
    """
    Visit link and extract plant info
    """
    html = requests.get(link)
    doc = lxml.html.fromstring(html.content)
    description = doc.xpath(
        "//div[contains(concat(' ', normalize-space(@class), ' '), 'product__description')]"
    )[0].text_content()
    description = description.replace("\n", " ")
    image_links = doc.xpath(
        "//div[contains(concat(' ', normalize-space(@class), ' '), 'product__media')]/a/@href"
    )
    image_links = ["https:" + link for link in image_links]
    plant_name = link.split("/")[-1]
    image_paths = []
    for i, image_link in enumerate(image_links):
        image_path = save_image(image_link, plant_name, base_dir, i)
        image_paths.append(image_path)
    return plant_name, dict(description=description, image_paths=image_paths)


def save_image(url, plant_name, base_dir, index):
    """
    Save an image
    """
    response = requests.get(url, stream=True)
    response.raw.decode_content = True
    image_path = base_dir / Path("images/steves_leaves") / (plant_name + f"_{index}.jpg")
    image_path.parent.mkdir(parents=True, exist_ok=True)
    with open(image_path, "wb") as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response
    return str(image_path.relative_to(base_dir))


def main():
    """
    Scrape stevesleaves.com
    """
    parser = ArgumentParser(description="Scrape Steve's Leaves")
    parser.add_argument("base-dir", type=Path)
    parser.add_argument("--force-discover", action="store_true")
    args = parser.parse_args()
    args.base_dir = getattr(args, "base-dir")
    args.base_dir.mkdir(parents=True, exist_ok=True)
    info = load_info(args.base_dir)
    if args.force_discover or not info.get("plant_links"):
        info = discover_links(info)
        save_info(info, args.base_dir)
    if not info.get("plants"):
        info["plants"] = dict()
    for link in tqdm(info["plant_links"], desc="scraping pages"):
        if link.split("/")[-1] not in info["plants"]:
            plant_name, plant_info = visit_link(link, args.base_dir)
            info["plants"][plant_name] = plant_info
            save_info(info, args.base_dir)


if __name__ == "__main__":
    main()
