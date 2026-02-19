#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
from utils.constants import COLOURS
from utils.utils import count_nodes_in_file

YEAR = datetime.now().year
MONTH = datetime.now().month
DAY = datetime.now().day

# Configuration
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
ACTIVE_DIR = PROJECT_ROOT / "active"
OUTPUT_FILE = PROJECT_ROOT / "stats" / "node-distribution-pie.png"
HISTORY_DIR = PROJECT_ROOT / "history"
HISTORY_OUTPUT_FILE = HISTORY_DIR / f"{YEAR}" / f"{MONTH:02d}" / f"{YEAR}-{MONTH:02d}-{DAY:02d}" / "node-distribution-pie.png"

def generate_pie_chart():
    """Generate and save the pie chart."""
    # Count nodes for each type
    relay_file = ACTIVE_DIR / "relay-nodes.txt"
    exit_file = ACTIVE_DIR / "exit-nodes.txt"
    guard_file = ACTIVE_DIR / "guard-nodes.txt"
    
    relay_count = count_nodes_in_file(relay_file)
    exit_count = count_nodes_in_file(exit_file)
    guard_count = count_nodes_in_file(guard_file)
    
    print(f"Node counts:")
    print(f"  Relay: {relay_count}")
    print(f"  Exit:  {exit_count}")
    print(f"  Guard: {guard_count}")
    print(f"  Total: {relay_count + exit_count + guard_count}\n")
    
    # Prepare data
    sizes = [relay_count, exit_count, guard_count]
    labels = ["Relay", "Exit", "Guard"]
    colors_list = [COLOURS["relay"], COLOURS["exit"], COLOURS["guard"]]
    
    # Create figure and axis
    plt.figure(figsize=(10, 8))
    
    # Create pie chart
    wedges, texts, autotexts = plt.pie(
        sizes,
        labels=labels,
        colors=colors_list,
        autopct="%1.1f%%",
        startangle=90,
    )
    
    # Enhance autotext (percentage labels)
    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_fontsize(11)
        autotext.set_fontweight("bold")
    
    # Add title
    plt.title("Tor Network Node Distribution", pad=20)
    
    # Add legend with counts
    legend_labels = [
        f"Relay: {relay_count:,}",
        f"Exit: {exit_count:,}",
        f"Guard: {guard_count:,}"
    ]
    plt.legend(legend_labels, loc="upper left", bbox_to_anchor=(0.85, 1))
    
    # Equal aspect ratio ensures that pie is drawn as a circle
    plt.axis("equal")
    
    # Tight layout to prevent label cutoff
    plt.tight_layout()
    
    # Add generated date text in bottom right
    fig = plt.gcf()
    generated_text = f"generated: {datetime.now().strftime('%Y-%m-%d')}"
    fig.text(0.99, 0.01, generated_text, fontsize=9, ha='right', va='bottom',
            color='gray', alpha=0.7)
    
    # Save chart
    plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches="tight")
    plt.savefig(HISTORY_OUTPUT_FILE, dpi=300, bbox_inches="tight")
    print(f"✓ Pie chart saved: {OUTPUT_FILE}")
    plt.close()

if __name__ == "__main__":
    print("Generating Tor network node distribution pie chart...\n")
    generate_pie_chart()
