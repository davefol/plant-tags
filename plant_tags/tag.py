"""
tag [plant-site].json
"""
from argparse import ArgumentParser
import json
from pathlib import Path

from dearpygui import core, simple


def main():
    """
    run gui
    """
    parser = ArgumentParser("Tag [plant-site].json files")
    parser.add_argument("json", type=Path)
    args = parser.parse_args()
    info_path = args.json.absolute()
    info = json.load(args.json.open("r"))
    base_dir = args.json.parent.absolute()
    plants = list(info["plants"])
    index = 0

    def show_plant(key):
        nonlocal index
        image_path = str((base_dir / info["plants"][key]["image_paths"][0]).absolute())
        core.draw_image("canvas", image_path, [0, 0], pmax=[512, 512])
        core.set_value("plant_name", key)
        if info["plants"][key].get("tags"):
            core.set_value("plant_tags", ", ".join(info["plants"][key]["tags"]))
        else:
            core.set_value("plant_tags", "")
        index = plants.index(key)

    def next_plant():
        nonlocal index
        index = (index + 1) % len(plants)
        show_plant(plants[index])

    def prev_plant():
        nonlocal index
        index = (index - 1)
        if index < 0:
            index = len(plants) - 1
        show_plant(plants[index])

    def edit_tags():
        info["plants"][plants[index]]["tags"] = core.get_value("plant_tags").split(",")
        save_info()

    def save_info():
        json.dump(info, info_path.open("w"), indent=2)


    with simple.window("Tag Plants"):
        core.set_value("plant_name", "")
        core.set_value("plant_tags", "")
        core.add_text("", source="plant_name")
        core.add_spacing(count=5)
        core.add_separator()
        core.add_spacing()
        core.add_drawing("canvas", width=512, height=512)
        core.add_spacing(count=5)
        core.add_separator()
        core.add_spacing()
        core.add_input_text("Tags", source="plant_tags", callback=edit_tags)
        core.add_button("Back", callback=next_plant)
        core.add_button("Next", callback=prev_plant)
        show_plant(plants[index])

    core.start_dearpygui(primary_window="Tag Plants")

if __name__ == "__main__":
    main()
