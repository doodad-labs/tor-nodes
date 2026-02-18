#!/usr/bin/env python3
"""
Generate churn rate analytics for Tor nodes.
Tracks node appearance, disappearance, and average node lifetime.
"""

import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

# Configuration
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
HISTORY_DIR = PROJECT_ROOT / "history"
OUTPUT_FILE = PROJECT_ROOT / "stats" / "churn-rate.png"

# Color scheme from network chart
COLOURS = {
    "relay": (189/255, 97/255, 87/255, 1),  # red
    "exit": (86/255, 189/255, 164/255, 1),   # green
    "guard": (87/255, 148/255, 189/255, 1),  # blue
    "churn": (87/255, 148/255, 189/255, 1),  # blue for churn rate
}

def collect_churn_data():
    """Collect node appearance/disappearance data and calculate lifespans."""
    
    node_first_seen = {}
    node_last_seen = {}
    date_nodes = {}
    
    # Find all date directories
    date_dirs = sorted(HISTORY_DIR.glob("*/*/????-??-??"))
    
    for date_dir in date_dirs:
        date_str = date_dir.name
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            continue
        
        date_nodes[date_obj] = {"relay": set(), "exit": set(), "guard": set()}
        
        # Read relay nodes
        relay_file = date_dir / "relay-nodes.txt"
        if relay_file.exists():
            with open(relay_file) as f:
                for line in f:
                    ip = line.strip()
                    if ip:
                        date_nodes[date_obj]["relay"].add(ip)
                        if ip not in node_first_seen:
                            node_first_seen[ip] = date_obj
                        node_last_seen[ip] = date_obj
        
        # Read exit nodes
        exit_file = date_dir / "exit-nodes.txt"
        if exit_file.exists():
            with open(exit_file) as f:
                for line in f:
                    ip = line.strip()
                    if ip:
                        date_nodes[date_obj]["exit"].add(ip)
                        if ip not in node_first_seen:
                            node_first_seen[ip] = date_obj
                        node_last_seen[ip] = date_obj
        
        # Read guard nodes
        guard_file = date_dir / "guard-nodes.txt"
        if guard_file.exists():
            with open(guard_file) as f:
                for line in f:
                    ip = line.strip()
                    if ip:
                        date_nodes[date_obj]["guard"].add(ip)
                        if ip not in node_first_seen:
                            node_first_seen[ip] = date_obj
                        node_last_seen[ip] = date_obj
    
    # Calculate lifespans
    lifespans = []
    for ip, first_date in node_first_seen.items():
        last_date = node_last_seen[ip]
        lifespan_days = (last_date - first_date).days
        lifespans.append(lifespan_days)
    
    avg_lifetime = sum(lifespans) / len(lifespans) if lifespans else 0
    
    print(f"Total unique nodes: {len(node_first_seen)}")
    print(f"Average node lifetime: {avg_lifetime:.1f} days")
    print(f"Min lifetime: {min(lifespans)} days")
    print(f"Max lifetime: {max(lifespans)} days")
    
    # Calculate daily churn
    sorted_dates = sorted(date_nodes.keys())
    new_nodes_per_day = []
    departed_nodes_per_day = []
    churn_rate_per_day = []
    
    for i, date in enumerate(sorted_dates):
        current_nodes = set()
        for node_type in date_nodes[date].values():
            current_nodes.update(node_type)
        
        if i == 0:
            new_nodes = len(current_nodes)
            departed_nodes = 0
            churn_rate = 0
        else:
            prev_date = sorted_dates[i-1]
            prev_nodes = set()
            for node_type in date_nodes[prev_date].values():
                prev_nodes.update(node_type)
            
            new_nodes = len(current_nodes - prev_nodes)
            departed_nodes = len(prev_nodes - current_nodes)
            # Churn rate as percentage of previous day's nodes
            churn_rate = (departed_nodes / len(prev_nodes) * 100) if len(prev_nodes) > 0 else 0
        
        new_nodes_per_day.append(new_nodes)
        departed_nodes_per_day.append(departed_nodes)
        churn_rate_per_day.append(churn_rate)
    
    print(f"\nDaily churn statistics:")
    print(f"  Average new nodes/day: {sum(new_nodes_per_day) / len(new_nodes_per_day):.1f}")
    print(f"  Average departed nodes/day: {sum(departed_nodes_per_day) / len(departed_nodes_per_day):.1f}")
    print(f"  Average churn rate: {sum(churn_rate_per_day) / len(churn_rate_per_day):.2f}%")
    
    return {
        "dates": sorted_dates,
        "new_nodes": new_nodes_per_day,
        "departed_nodes": departed_nodes_per_day,
        "churn_rate": churn_rate_per_day,
        "avg_lifetime": avg_lifetime,
        "total_nodes": len(node_first_seen),
        "lifespans": lifespans
    }

def generate_churn_chart(data):
    """Generate churn rate visualization."""
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Skip first day to avoid startup spike
    dates = data["dates"][1:]
    new_nodes = data["new_nodes"][1:]
    departed_nodes = data["departed_nodes"][1:]
    churn_rate = data["churn_rate"][1:]
    
    # Top chart: New vs Departed nodes
    ax1.bar(dates, new_nodes, label="New Nodes", alpha=1, color=COLOURS["exit"])
    ax1.bar(dates, [-x for x in departed_nodes], label="Departed Nodes", alpha=1, color=COLOURS["relay"])
    ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
    ax1.set_ylabel("Node Count")
    ax1.set_title("Daily Node Appearance and Disappearance")
    ax1.legend(loc="best")
    ax1.grid(True, alpha=0.3)
    
    # Format x-axis
    ax1.xaxis.set_major_locator(mdates.MonthLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax1.xaxis.set_minor_locator(mdates.WeekdayLocator())
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Remove spines
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    
    # Bottom chart: Churn rate
    ax2.plot(dates, churn_rate, color=COLOURS["guard"], linewidth=2.5, marker='o', markersize=4)
    ax2.fill_between(dates, churn_rate, alpha=0.7, color=COLOURS["guard"])
    ax2.set_ylabel("Churn Rate (%)")
    ax2.set_xlabel("Date")
    ax2.set_title("Daily Node Churn Rate (Departed / Total)")
    ax2.grid(True, alpha=0.3)
    
    # Format x-axis
    ax2.xaxis.set_major_locator(mdates.MonthLocator())
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax2.xaxis.set_minor_locator(mdates.WeekdayLocator())
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Remove spines
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['bottom'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    
    # Add statistics text (excluding first day from averages)
    avg_new = sum(new_nodes) / len(new_nodes) if new_nodes else 0
    avg_departed = sum(departed_nodes) / len(departed_nodes) if departed_nodes else 0
    avg_churn = sum(churn_rate) / len(churn_rate) if churn_rate else 0
    
    stats_text = (
        f"Total unique nodes: {data['total_nodes']}\n"
        f"Avg lifetime: {data['avg_lifetime']:.1f} days\n"
        f"Avg new/day: {avg_new:.0f}  |  Avg departed/day: {avg_departed:.0f}\n"
        f"Avg churn rate: {avg_churn:.2f}%"
    )
    fig.text(0.12, 0.02, stats_text, fontsize=10, family='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # Add generated date text in bottom right
    generated_text = f"generated: {datetime.now().strftime('%Y-%m-%d')}"
    fig.text(0.99, 0.01, generated_text, fontsize=9, ha='right', va='bottom',
             color='gray', alpha=0.7)
    
    plt.tight_layout(rect=[0, 0.06, 1, 1])
    plt.savefig(OUTPUT_FILE, dpi=150, bbox_inches="tight")
    print(f"\n✓ Churn rate chart saved: {OUTPUT_FILE}")
    plt.close()

if __name__ == "__main__":
    print("Analyzing Tor node churn rate...\n")
    data = collect_churn_data()
    
    print("\nGenerating churn rate chart...")
    generate_churn_chart(data)
