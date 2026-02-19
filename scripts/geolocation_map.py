#!/usr/bin/env python3
"""
Generate a world map with Tor node geolocation scatter plot.
Shows node density by country with bubble sizes representing node count.
Aggregates nodes by country and places them at country centroids.
"""

import json
from pathlib import Path
import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
import urllib.request
from datetime import datetime

YEAR = datetime.now().year
MONTH = datetime.now().month
DAY = datetime.now().day

# Configuration
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
WORLD_FILE = PROJECT_ROOT / "ne_110m_admin_0_countries.zip"
ACTIVE_DIR = PROJECT_ROOT / "active"
HISTORY_DIR = PROJECT_ROOT / "history"
OUTPUT_FILE = PROJECT_ROOT / "stats" / "geolocation-map.png"
HISTORY_OUTPUT_FILE = HISTORY_DIR / f"{YEAR}" / f"{MONTH:02d}" / f"{YEAR}-{MONTH:02d}-{DAY:02d}" / "geolocation-map.png"
WORLD_MAP = None

def download_natural_earth_data() -> Path:
    """Download Natural Earth data if not already cached. Returns path to zip."""
    if not WORLD_FILE.exists():
        print("Downloading Natural Earth data...")
        url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
        urllib.request.urlretrieve(url, WORLD_FILE)
    return WORLD_FILE


def load_world_map() -> gpd.GeoDataFrame:
    """
    Load Natural Earth countries from the zip.
    Fiona/GDAL understands zip:// URIs.
    """
    zip_path = download_natural_earth_data()

    # Often geopandas can infer the layer directly from the zip:
    try:
        return gpd.read_file(f"zip://{zip_path}")
    except Exception:
        # If inference fails, explicitly point to the .shp inside the zip:
        # (This filename matches the Natural Earth download you’re using.)
        shp_in_zip = "ne_110m_admin_0_countries.shp"
        return gpd.read_file(f"zip://{zip_path}!{shp_in_zip}")

def generate_map(world_map: gpd.GeoDataFrame | None):
    # Load geolocation data
    with open(ACTIVE_DIR / "geo-location.json", "r") as f:
        geo_data = json.load(f)

    df = pd.DataFrame(geo_data)

    # Filter out Antarctica / extreme south
    if world_map is not None and not world_map.empty:
        world_map = world_map[~world_map["NAME"].str.contains("Antarctica", case=False, na=False)]
        # bounds is a DataFrame with columns: minx, miny, maxx, maxy
        world_map = world_map[world_map.bounds["miny"] > -85]

    fig, ax = plt.subplots(figsize=(16, 10))

    if world_map is not None and not world_map.empty:
        world_map.plot(color="lightgrey", ax=ax, edgecolor="white", linewidth=0.5)
    else:
        ax.set_facecolor("#e6f2ff")

    node_counts = df.groupby(["latitude", "longitude"]).size().reset_index(name="node_count")

    print(f"Found {len(node_counts)} unique lat/lon locations with Tor nodes")
    print(f"Total nodes: {int(node_counts['node_count'].sum())}")

    if not node_counts.empty:
        x = node_counts["longitude"].values
        y = node_counts["latitude"].values
        z = node_counts["node_count"].values

        bubble_sizes = (z * 0.5).clip(min=10, max=50)

        ax.scatter(
            x, y,
            s=bubble_sizes,
            c=z,
            alpha=0.6,
            cmap="autumn",
            edgecolors="darkred",
            linewidth=0.5,
            vmin=0,
            vmax=z.max()
        )
    else:
        print("No location data to plot")

    ax.set_xlim([-180, 180])
    ax.set_ylim([-60, 85])  # Exclude Antarctica

    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    generated_text = f"generated: {datetime.now().strftime('%Y-%m-%d')}"
    fig.text(0.98, 0.02, generated_text, fontsize=9, ha="right", va="bottom",
            color="gray", alpha=0.7)

    plt.tight_layout()

    # Ensure output directories exist
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    plt.savefig(OUTPUT_FILE, dpi=150, bbox_inches="tight")
    plt.savefig(HISTORY_OUTPUT_FILE, dpi=150, bbox_inches="tight")
    print(f"✓ Geolocation map saved to {OUTPUT_FILE}, {HISTORY_OUTPUT_FILE}")

    plt.close(fig)

if __name__ == "__main__":
    print(WORLD_FILE)

    try:
        WORLD_MAP = load_world_map()
    except Exception as e:
        print(f"Error loading world map data: {e}")
        WORLD_MAP = None

    print("Generating geolocation map...")
    generate_map(WORLD_MAP)