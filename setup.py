"""
setup script
"""
from setuptools import setup, find_packages

setup(
    name="plant-tags",
    version="0.1",
    description="Catalog visual features of house-plants",
    author="Dave Fol",
    author_email="dof5@cornell.edu",
    packages=find_packages(),
    install_requires=[
        "lxml==4.6.3",
        "requests==2.25.1",
        "tqdm==4.61.1",
        "dearpygui==0.6.415",
    ],
    entry_points={
        "console_scripts": [
            "plant-tags-scrape-steve = plant_tags.scrape_steves_leaves:main",
            "plant-tags-tag = plant_tags.tag:main"
        ]
    }
)
