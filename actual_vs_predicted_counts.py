import csv
import re
from collections import defaultdict
import argparse
import matplotlib.pyplot as plt
import numpy as np

def read_csv_file(filename):
    data = []
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return data

def extract_bar_patterns(structure_string):
    # Use regex to split by ',', ';', and '.'
    #bar_patterns = re.split(r'[,\.;]\s*', structure_string)
    bar_patterns = re.findall(r'[A-Z]?[a-z][0-9]?', structure_string)
    # Remove any empty strings that may result from splitting
    bar_patterns = [pattern for pattern in bar_patterns if pattern]
    return bar_patterns


def strip_number(bar_string):
    return re.sub(r'\d+', '', bar_string)


def create_array(pattern):
    array = [] * len(pattern)
    for i in range(0, len(pattern)):
        full_match = False
        variant_match = False
        full_match_element = []
        variant_match_element = []
        for j in range(0, i):
            if pattern[i] == pattern[j] and not full_match:
                full_match_element = [j, False]
                full_match = True
            elif strip_number(pattern[i]) == pattern[j]:
                variant_match_element = [j , True]
                variant_match = True
        if full_match:
            array.append(full_match_element)
        elif variant_match:
            array.append(variant_match_element)
        else:
            array.append([i, False])
    return array

def compare_arrays(script_array, doherty_array):
    counts = [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0]
    ]

    for s, (S, D) in enumerate(zip(script_array, doherty_array)):
        x, a = S
        y, b = D
        d = s

        if y != d:
            if x == y:
                if a == b == False:
                    counts[0][0] += 1  # predicted_full_match_actual_full_match
                elif a == True and b == False:
                    counts[0][1] += 1  # predicted_variant_match_actual_full_match
                elif a == False and b == True:
                    counts[1][0] += 1  # predicted_full_match_actual_variant_match
                elif a == b == True:
                    counts[1][1] += 1  # predicted_variant_match_actual_variant_match
            elif x == s:
                if b == False:
                    counts[0][2] += 1  # predicted_no_match_actual_full_match
                elif b == True:
                    counts[1][2] += 1  # predicted_no_match_actual_variant_match
        else:  # y == d
            if x != y:
                if a == False:
                    counts[2][0] += 1  # predicted_full_match_actual_no_match
                elif a == True:
                    counts[2][1] += 1  # predicted_variant_match_actual_no_match
            elif x == s:
                counts[2][2] += 1  # predicted_no_match_actual_no_match

    return counts


def compare(file1_data, file2_data):
    confusion_matrix = [[0, 0, 0],
                        [0, 0, 0],
                        [0, 0, 0]]
    
    for row1 in file1_data:
        tune1 = row1['Tune']
        part1 = row1['Part']
        script_structure = row1['Structure']
        
        for row2 in file2_data:
            tune2 = row2['Tune']
            part2 = row2['Part']
            doherty_structure = row2['Structure']

            # A parts only
            if part1 =="A" and part2 == "A":
                    if tune1 == tune2 and part1 == part2:
                        # Extract bar patterns
                        script_patterns = extract_bar_patterns(script_structure)
                        doherty_patterns = extract_bar_patterns(doherty_structure)

                        script_array = create_array(script_patterns)
                        doherty_array = create_array(doherty_patterns)

                        # Commpute confusion matrix values for current bar.
                        result = compare_arrays(script_array, doherty_array)

                        # Increment the count for this number of common bar patterns
                        confusion_matrix = [[confusion_matrix[i][j] + result[i][j] for j in range(3)] for i in range(3)]
                        break  # break the inner loop since we found a match
    return confusion_matrix


# Now, let's create a function to visualize the confusion matrix
def visualize_confusion_matrix(confusion_matrix, method_name):
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(confusion_matrix, cmap='YlOrRd')

    # Set labels
    categories = ['Full Match', 'Variant Match', 'No Match']
    ax.set_xticks(np.arange(len(categories)))
    ax.set_yticks(np.arange(len(categories)))
    ax.set_xticklabels(categories)
    ax.set_yticklabels(categories)

    # Hide X and Y axes tick marks
    plt.tick_params(
        which='both',      # both major and minor ticks are affected
        left=False,      # ticks along the bottom edge are off
        bottom=False) # labels along the bottom edge are off

    # Loop over data dimensions and create text annotations
    for i in range(len(categories)):
        for j in range(len(categories)):
            text = ax.text(j, i, confusion_matrix[i][j],
                           ha="center", va="center", color="black")

    #ax.set_title(, fontsize = 15)
    plt.title(f"Confusion Matrix: {method_name}", fontsize = 20, x=0.5, y=1.05)
    ax.set_xlabel('Predicted', fontsize = 15)
    ax.set_ylabel('Actual', rotation=0, ha='right', va='center', fontsize = 15)
    # Add some padding to prevent overlap with axis labels
    ax.xaxis.set_label_coords(0.5, -0.1)
    ax.yaxis.set_label_coords(-0.2, 0.5)


    fig.tight_layout()
    #plt.colorbar(im)
    #plt.show()
    plt.savefig(f'comparison/confusion_matrix_{method_name}.png', dpi=300, bbox_inches='tight')
    print(f"Chart has been saved as 'comparison/confusion_matrix_{method_name}.png'")



def compute_cm_values(file1):
    file2 = '/home/roro/Documents/RA2/datasets/james/7fefb0fea2a4d00d74f6a3a8eaab81cf-7fb105e18fe0bf0d0c34c53e0ae36e6d53441188/Detail1.csv'
    file1_data = read_csv_file(file1)
    file2_data = read_csv_file(file2)

    confusion_matrix = compare(file1_data, file2_data)
    visualize_confusion_matrix(confusion_matrix, "test")
    return confusion_matrix

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Input file", default='/home/roro/Documents/RA2/code/melodic_structure_analysis/melodic_structures.csv')
    args = parser.parse_args()
    in_path = args.input
    results = compute_cm_values(in_path)
    print(results)

