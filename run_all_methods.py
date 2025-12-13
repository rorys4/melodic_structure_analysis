import subprocess
import matplotlib.pyplot as plt
import pandas as pd
import math
import os
import json
import argparse
import numpy as np
import csv
from actual_vs_predicted_counts import compute_cm_values, visualize_confusion_matrix

method_mapping = {
    0: "Basic Method",
    1: "Initial Note Constraint Method",
    2: "Initial and Central Note Constraint Method",
    3: "Longest Common Prefix Method",
    4: "Contiguous Notes Method",
    5: "Transposition-Adjusted Method",
    6: "Custom Beat Strength Weighting Method",
    7: "Linear Beat Strength Weighting Method",
    8: "Exponential Beat Strength Weighting Method",
    9: "Doherty Ruleset Method"
}

def round_up_to_nearest_10(number):
    return math.ceil(number / 10) * 10

def run_analysis():
    results = []

    for x in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
        output_filename = f"comparison_Feb2025/output{x}.csv"
        
        subprocess.run(["python3", "analyse_melodic_structures.py", "-m", str(x), "-o", output_filename])
        
        result = subprocess.run(["python3", "compare_with_doherty.py", "-i", output_filename], 
                                capture_output=True, text=True)
        
        try:
            agreement = float(result.stdout.strip())
            results.append((method_mapping[x], agreement))
        except ValueError:
            print(f"Could not extract agreement percentage for method {x}. Output: {result.stdout}")
    
    return results, output_filename


def confusion_matrices():
    f1_data = [['Method', "Full Match", "Variant Match", "No Match", "Weighted Average"]]
    fig, axes = plt.subplots(4, 3, figsize=(15, 20))  # Create a 4x3 grid for better A4 fit
    axes = axes.flatten()  # Flatten the 2D array for easy indexing
    
    for x in range(10):  # Loop over the 10 plots
        output_filename = f"comparison_Feb2025/output{x}.csv"
        cm_values, f1 = compute_cm_values(output_filename)
        visualize_confusion_matrix(cm_values, str(method_mapping[x]).removesuffix(' Method'), axes[x])
        
        f1_data.append([method_mapping[x]] + f1)
    
    # Hide unused subplot
    for i in range(10, 12):  # Hide the last two empty subplots
        fig.delaxes(axes[i])
    
    plt.tight_layout()
    plt.savefig("comparison_Feb2025/confusion_matrices_grid.png", dpi=300)
    print("Confusion matrix grid has been saved as 'comparison_Feb2025/confusion_matrices_grid.png'")
    
    save_results(f1_data, 'CSV', 'comparison_Feb2025/f1_scores.csv')


def save_results(results, filetype, filename='comparison_Feb2025/analysis_results.json'):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        if filetype == 'JSON':
            json.dump(results, f)
        else:
            write = csv.writer(f)
            write.writerows(results)
    print(f"Results saved to {filename}")

def load_results(filename='comparison_Feb2025/analysis_results.json'):
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
    max_value = df['Agreement (%)'].max()
    plt.xlim(0, round_up_to_nearest_10(max_value))

    plt.box(False)
    plt.yticks(ticks=plt.gca().get_yticks(), labels=df['Method'])
    plt.gca().tick_params(axis='both', which='both', length=0)
    plt.grid(axis='x', linestyle='--', alpha=0.7, color='lightgray')
    
    # Add the No Information Rate line
    no_info_rate = 58.99388341031082
    plt.axvline(x=no_info_rate, color='black', linestyle='--', linewidth=1)
    
    # Add the No Information Rate text
    plt.text(no_info_rate, 1.02, 'No Information Rate', 
             transform=plt.gca().get_xaxis_transform(),
             ha='center', va='bottom', color='black', fontsize=10)

    plt.tight_layout()
    os.makedirs('comparison_Feb2025', exist_ok=True)
    plt.savefig('comparison_Feb2025/method_comparison_bar_chart.png', dpi=300, bbox_inches='tight')
    print("Chart has been saved as 'comparison_Feb2025/method_comparison_bar_chart.png'")


def main():
    parser = argparse.ArgumentParser(description="Analyze melodic structures and create comparison chart.")
    parser.add_argument("-l", "--load", help="Load results from a JSON file instead of running analysis")
    args = parser.parse_args()

    if args.load:
        print(f"Loading results from {args.load}")
        results = load_results(args.load)
    else:
        print("Running analysis...")
        results, output_filename = run_analysis()
        save_results(results, 'JSON')

    if results:
        create_chart(results)
        confusion_matrices()
        
    else:
        print("Error: No results to create chart.")

if __name__ == "__main__":
    main()
