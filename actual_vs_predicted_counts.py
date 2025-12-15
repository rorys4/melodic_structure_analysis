import csv
import re
from collections import defaultdict
import argparse
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors


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
        
        if y != s: # Actual full or variant match
            if x == y: # Actual and prediction refer to same bar.
                if a == b == False: # Both non-variants
                    counts[0][0] += 1  # predicted_full_match_actual_full_match
                elif a == True and b == False:
                    counts[0][1] += 1  # predicted_variant_match_actual_full_match
                elif a == False and b == True:
                    counts[1][0] += 1  # predicted_full_match_actual_variant_match
                elif a == b == True:
                    counts[1][1] += 1  # predicted_variant_match_actual_variant_match
            elif x == s: # Predicted no match
                if b == False:
                    counts[0][2] += 1  # predicted_no_match_actual_full_match
                elif b == True:
                    counts[1][2] += 1  # predicted_no_match_actual_variant_match
        else:  # Actual No_match
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
                    
                    # Compute confusion matrix values for current bar.
                    result = compare_arrays(script_array, doherty_array)
                    #if tune1 == '4':
                    #    print(script_array, doherty_array)
                    
                    #n = sum([sum(x) for x in zip(*result)])
                    #if n != 8:
                    #    print(f"{tune1}:{row1['Title']}, {n}, {result}")
                    
                    # Increment the count for this number of common bar patterns
                    confusion_matrix = [[confusion_matrix[i][j] + result[i][j] for j in range(3)] for i in range(3)]
                    break  # break the inner loop since we found a match
    return confusion_matrix


def visualize_confusion_matrix(confusion_matrix, method_name, ax):
    categories = ['Full', 'Variant', 'None']
    num_classes = len(categories)
    
    # Compute totals
    row_totals = np.sum(confusion_matrix, axis=1)
    col_totals = np.sum(confusion_matrix, axis=0)
    overall_total = np.sum(row_totals)
    
    # Create extended matrix with totals
    extended_matrix = np.zeros((num_classes + 1, num_classes + 1), dtype=int)
    extended_matrix[:num_classes, :num_classes] = confusion_matrix
    extended_matrix[:num_classes, -1] = row_totals
    extended_matrix[-1, :num_classes] = col_totals
    extended_matrix[-1, -1] = overall_total
    
    # Update categories to include 'Total'
    categories.append('Total')
    
    # Create a mask for the main confusion matrix
    mask = np.ones_like(extended_matrix, dtype=bool)
    mask[:num_classes, :num_classes] = False  # Set main confusion matrix to False in mask
    
    # Create a masked array for the main confusion matrix
    masked_matrix = np.ma.array(extended_matrix, mask=mask)
    
    # Create a masked array for the totals
    totals_mask = ~mask  # Invert the mask
    totals_matrix = np.ma.array(extended_matrix, mask=totals_mask)
    
    # Plot the main confusion matrix with YlGn colormap
    main_cmap = plt.get_cmap('YlGn')
    truncated_main_cmap = mcolors.LinearSegmentedColormap.from_list("truncated", main_cmap(np.linspace(0, 0.9, 256)))
    im1 = ax.imshow(masked_matrix, cmap=truncated_main_cmap)
    
    # Plot the totals with a Purples colormap
    totals_cmap = plt.get_cmap('Purples')
    im2 = ax.imshow(totals_matrix, cmap=totals_cmap)
    
    # Set y-tick labels on the left side (default)
    ax.set_yticks(np.arange(len(categories)))
    ax.set_yticklabels(categories, fontsize=8)
    
    # Place x-tick labels above the heatmap
    ax.xaxis.tick_top()
    ax.set_xticks(np.arange(len(categories)))
    ax.set_xticklabels(categories, fontsize=8)
    ax.xaxis.set_label_position('top')
    
    # Hide X and Y axes tick marks
    ax.tick_params(which='both', left=False, top=False)
    
    # Find the maximum value in the main confusion matrix for color scaling
    max_main_val = np.max(confusion_matrix)
    
    # Loop over data dimensions and create text annotations
    for i in range(len(categories)):
        for j in range(len(categories)):
            cell_value = extended_matrix[i][j]
            
            # Choose text color based on cell position and value
            if i < num_classes and j < num_classes:
                # Main confusion matrix - darker as value approaches max_main_val
                threshold = max_main_val * 0.5
                text_color = "white" if cell_value > threshold else "black"
            else:
                # Totals section - darker as value approaches overall_total
                threshold = overall_total * 0.5
                text_color = "white" if cell_value > threshold else "black"
            
            ax.text(j, i, cell_value, fontsize=15, ha="center", va="center", color=text_color)
    
    # Draw separator lines for the totals row and column
    ax.axhline(y=num_classes - 0.5, color='black', linewidth=1.5)
    ax.axvline(x=num_classes - 0.5, color='black', linewidth=1.5)
    
    # Place the method name label at the bottom instead
    ax.set_xlabel(f"{method_name}", fontsize=14)
    ax.xaxis.set_label_position('bottom')
    
    return ax


def f1_scores(m):
    """
    Calculate F1 scores for each class in a multi-class confusion matrix.
    
    :param confusion_matrix: 2D numpy array (NxN) representing the confusion matrix
    :return: Dictionary with class indices as keys and F1 scores as values
    """
    confusion_matrix = np.array(m)
    num_classes = confusion_matrix.shape[0]
    f1_scores = []

    support = np.sum(confusion_matrix, axis=1)  # Total instances per class
    total_support = np.sum(support)
    weighted_f1_sum = 0
    
    for i in range(num_classes):
        tp = confusion_matrix[i, i]  # True Positives
        fp = sum(confusion_matrix[:, i]) - tp  # False Positives
        fn = sum(confusion_matrix[i, :]) - tp  # False Negatives
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        f1_scores.append(f1)
        weighted_f1_sum += f1 * support[i]
    weighted_avg = weighted_f1_sum / total_support if total_support > 0 else 0
    f1_scores.append(weighted_avg)
    return f1_scores


def compute_cm_values(file1):
    #file2 = '/home/roro/Documents/RA2/datasets/james/7fefb0fea2a4d00d74f6a3a8eaab81cf-7fb105e18fe0bf0d0c34c53e0ae36e6d53441188/Detail1.csv'
    file2 = 'Detail1.csv'
    file1_data = read_csv_file(file1)
    file2_data = read_csv_file(file2)

    confusion_matrix = compare(file1_data, file2_data)
    
    # Compute F1 scores
    f1 = f1_scores(confusion_matrix)
    print(f1)
    return confusion_matrix, f1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    #parser.add_argument("-i", "--input", help="Input file", default='/home/roro/Documents/RA2/code/melodic_structure_analysis/melodic_structures.csv')
    parser.add_argument("-i", "--input", help="Input file", default='melodic_structures.csv')
    args = parser.parse_args()
    in_path = args.input
    results = compute_cm_values(in_path)
    print(results)

