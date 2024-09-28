import csv
import re
from collections import defaultdict
import argparse

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



def compare(file1_data, file2_data):
    total = 0
    bar_level_count = 0
    
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

                        # Compare bar patterns
                        common_count = sum(1 for sp, dp in zip(script_array, doherty_array) if sp == dp)

                        # Increment the count for this number of common bar patterns
                        bar_level_count += common_count
                        total += 8
                        break  # break the inner loop since we found a match
    return bar_level_count, total


def main(file1):
    file2 = '/home/roro/Documents/RA2/datasets/james/7fefb0fea2a4d00d74f6a3a8eaab81cf-7fb105e18fe0bf0d0c34c53e0ae36e6d53441188/Detail1.csv'
    file1_data = read_csv_file(file1)
    file2_data = read_csv_file(file2)

    same, total = compare(file1_data, file2_data)

    print(same/total*100)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Input file", default='/home/roro/Documents/RA2/code/melodic_structure_analysis/melodic_structures.csv')
    args = parser.parse_args()
    in_path = args.input
    main(in_path)

