import subprocess
import matplotlib.pyplot as plt
import pandas as pd
import math
import os
import json
import argparse
import numpy as np
from actual_vs_predicted_counts import compute_cm_values, visualize_confusion_matrix

def round_up_to_nearest_10(number):
    return math.ceil(number / 10) * 10

def run_analysis():
    results = []
    method_mapping = {
        0: "Basic Method",
        1: "Require 1st Note",
        2: "Require 1st and 4th notes",
        3: "Longest Common Prefix",
        4: "Contiguous Notes",
        5: "Division by Transposition Amount",
        6: "Custom Beat Strength, r = sqrt(10)",
        7: "Hard-coded Beat Strength Values - Linear",
        8: "Hard-coded Beat Strength Values - Geometric",
        9: "New Rules"
    }
    
    #for x in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 13, 14, 15]:
    for x in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
        output_filename = f"comparison/output{x}.csv"
        
        subprocess.run(["python3", "analyse_melodic_structures.py", "-m", str(x), "-o", output_filename])
        
        result = subprocess.run(["python3", "compare_with_doherty.py", "-i", output_filename], 
                                capture_output=True, text=True)
        
        try:
            agreement = float(result.stdout.strip())
            results.append((method_mapping[x], agreement))
        except ValueError:
            print(f"Could not extract agreement percentage for method {x}. Output: {result.stdout}")

        cm_values = compute_cm_values(output_filename)
        visualize_confusion_matrix(cm_values, str(method_mapping[x]))
    
    return results

def save_results(results, filename='comparison/analysis_results.json'):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        json.dump(results, f)
    print(f"Results saved to {filename}")

def load_results(filename='comparison/analysis_results.json'):
    with open(filename, 'r') as f:
        return json.load(f)

def create_chart(data):
    df = pd.DataFrame(data, columns=["Method", "Agreement (%)"])
    df = df.sort_values('Agreement (%)', ascending=True)

    plt.figure(figsize=(12, 8))
    color = (0.5, # redness
         0.5, # greenness
         0.95, # blueness
         0.9 # transparency
         )
    bars = plt.barh(df['Method'], df['Agreement (%)'], color=color)

    plt.title("Method Comparison\n A Parts", fontsize=16, pad=30)  # Increase padding for the title
    plt.xlabel("Agreement (%)", fontsize=12)
    # Remove y-axis label
    # plt.ylabel("Method", fontsize=12)

    max_value = df['Agreement (%)'].max()
    plt.xlim(0, round_up_to_nearest_10(max_value))

    plt.box(False)
    plt.yticks(ticks=plt.gca().get_yticks(), labels=df['Method'])
    plt.gca().tick_params(axis='both', which='both', length=0)

    #for i, method in enumerate(df['Method']):
    #    if method == "Hard-coded Beat Strength Values - Linear" or method == "Hard-coded Beat Strength Values - Geometric":
    #        bars[i].set_color('red')

    #bars[5].set_color('red')
    #bars[7].set_color('red')

    plt.grid(axis='x', linestyle='--', alpha=0.7, color='lightgray')
    
    # Add the No Information Rate line
    no_info_rate = 58.99388341031082
    plt.axvline(x=no_info_rate, color='black', linestyle='--', linewidth=1)
    
    # Add the No Information Rate text
    plt.text(no_info_rate, 1.02, 'No Information Rate', 
             transform=plt.gca().get_xaxis_transform(),
             ha='center', va='bottom', color='black', fontsize=10)

    plt.tight_layout()
    
    os.makedirs('comparison', exist_ok=True)
    
    plt.savefig('comparison/method_comparison_bar_chart.png', dpi=300, bbox_inches='tight')
    print("Chart has been saved as 'comparison/method_comparison_bar_chart.png'")


def main():
    parser = argparse.ArgumentParser(description="Analyze melodic structures and create comparison chart.")
    parser.add_argument("-l", "--load", help="Load results from a JSON file instead of running analysis")
    args = parser.parse_args()

    if args.load:
        print(f"Loading results from {args.load}")
        results = load_results(args.load)
    else:
        print("Running analysis...")
        results = run_analysis()
        save_results(results)

    if results:
        create_chart(results)
    else:
        print("Error: No results to create chart.")

if __name__ == "__main__":
    main()
