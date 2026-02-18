#!/usr/bin/env python3
"""
Generate a world map with Tor node geolocation scatter plot.
Shows node density by country with varying bubble sizes and colors.
"""

import json
import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd

# Load geolocation data
with open("active/geo-location.json", "r") as f:
    geo_data = json.load(f)

# Convert to DataFrame
df = pd.DataFrame(geo_data)

# Get world map from Natural Earth dataset
try:
    # Try to load from cache first
    import os
    cache_dir = os.path.expanduser("~/.cache/geopandas")
    zip_path = os.path.join(cache_dir, "naturalearth_lowres.zip")
    
    if os.path.exists(zip_path):
        worldmap = gpd.read_file(f"zip://{zip_path}!ne_110m_admin_0_countries.shp")
    else:
        # Fallback: download on demand
        import urllib.request
        os.makedirs(cache_dir, exist_ok=True)
        print("Downloading Natural Earth data...")
        url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
        urllib.request.urlretrieve(url, zip_path)
        worldmap = gpd.read_file(f"zip://{zip_path}!ne_110m_admin_0_countries.shp")
except Exception as e:
    print(f"Warning: Could not load Natural Earth data: {e}")
    print("Continuing with map outline only...")
    worldmap = None

# Create figure
fig, ax = plt.subplots(figsize=(16, 10))

# Plot world map
if worldmap is not None:
    worldmap.plot(color="lightgrey", ax=ax, edgecolor="white", linewidth=0.5)
else:
    ax.set_facecolor("#e6f2ff")

# Count nodes by location (aggregate nearby points)
node_counts = df.groupby(['latitude', 'longitude']).size().reset_index(name='node_count')

# Plot scatter points
x = node_counts['longitude']
y = node_counts['latitude']
z = node_counts['node_count']

scatter = plt.scatter(
    x, y,
    s=0.1 * z,          # Size proportional to number of nodes
    c=z,                # Color by node count
    alpha=0.6,
    cmap='autumn',
    edgecolors='black',
    linewidth=0.3
)

# Add colorbar
cbar = plt.colorbar(scatter, label='Number of Nodes', ax=ax)

# Set axis limits and labels
plt.xlim([-180, 180])
plt.ylim([-90, 90])
plt.xlabel("Longitude", fontsize=12)
plt.ylabel("Latitude", fontsize=12)
plt.title("Tor Network Node Geolocation Distribution\nNode size and color indicate local concentration", fontsize=14, fontweight='bold')

# Add grid
ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)

# Tight layout
plt.tight_layout()

# Save figure
plt.savefig("stats/geolocation-map.png", dpi=150, bbox_inches='tight')
print("✓ Geolocation map saved to stats/geolocation-map.png")

plt.close()
