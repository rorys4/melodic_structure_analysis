import subprocess
import matplotlib.pyplot as plt
import pandas as pd
import math

def round_up_to_nearest_10(number):
    return math.ceil(number / 10) * 10

def run_analysis():
    results = []
    method_mapping = {
        0: "Basic Method",
        1: "Require 1st Note",
        2: "Require 1st and 4th notes",
        3: "Music21 Beat Strength Sum 2.0,1.25",
        4: "Music21 Beat Strength Sum 2.0,1.5",
        5: "Music21 Beat Strength Sum 1.75,1.25",
        6: "Music21 Beat Strength Sum 1.75,1.5",
        7: "Music21 Beat Strength Sum 1.5,1.25",
        8: "Music21 Beat Strength Sum 2.25,1.5",
        9: "Longest Common Prefix",
        12: "Variant Score Threshold = 4",
        14: "Hard-coded Beat Strength Values"
    }
    
    for x in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 14]:
        output_filename = f"comparison/output{x}.csv"
        
        # Run the first Python program
        subprocess.run(["python3", "analyse_melodic_structures.py", "-m", str(x), "-o", output_filename])
        
        # Run the second Python program and capture its output
        result = subprocess.run(["python3", "../compare_results/compare_with_doherty.py", "-i", output_filename], 
                                capture_output=True, text=True)
        
        # Extract the agreement percentage from the output
        try:
            agreement = float(result.stdout.strip())
            results.append((method_mapping[x], agreement))
        except ValueError:
            print(f"Could not extract agreement percentage for method {x}. Output: {result.stdout}")
    
    return results

def create_chart(data):
    df = pd.DataFrame(data, columns=["Method", "Agreement (%)"])
    df = df.sort_values('Agreement (%)', ascending=True)

    plt.figure(figsize=(12, 8))
    bars = plt.barh(df['Method'], df['Agreement (%)'])

    plt.title("Method Comparison", fontsize=16)
    plt.xlabel("Agreement (%)", fontsize=12)
    plt.ylabel("Method", fontsize=12)

    max_value = df['Agreement (%)'].max()
    plt.xlim(0, round_up_to_nearest_10(max_value))

    plt.box(False)
    plt.yticks(ticks=plt.gca().get_yticks(), labels=df['Method'])
    plt.gca().tick_params(axis='both', which='both', length=0)

    # Highlight specific bars
    for i, method in enumerate(df['Method']):
        if method == "Hard-coded Beat Strength Values" or method == "Hard-coded Beat Strength Values":
            bars[i].set_color('red')

    plt.grid(axis='x', linestyle='--', alpha=0.7, color='lightgray')
    plt.tight_layout()
    plt.savefig('comparison/method_comparison_bar_chart.png', dpi=300, bbox_inches='tight')
    print("Chart has been saved as 'comparison/method_comparison_bar_chart.png'")

def main():
    results = run_analysis()
    if results:
        create_chart(results)
    else:
        print("Error: No results to create chart.")

if __name__ == "__main__":
    main()
