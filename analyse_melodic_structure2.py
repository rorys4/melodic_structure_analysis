import pandas as pd
import collections
import sys
import os
from tqdm import tqdm
import pprint

def load_data(file_path):
    # Load the CSV file into a DataFrame
    data = pd.read_csv(file_path)

    # Create the nested structure
    parts = {}
    for _, note in data.iterrows():
        bar_num = note['bar_num']
        part_num = bar_num // 8

        if part_num not in parts:
            parts[part_num] = {}
        if bar_num not in parts[part_num]:
            parts[part_num][bar_num] = []

        parts[part_num][bar_num].append(note.to_dict())

    return parts

def analyse_tune(in_path, filename, outputfile):
    # Path to the CSV file
    #file_path = '/home/roro/Documents/RA2/code/melodic_struc_analysis/feature_CSVs/duration_weighted/Shandonbells.csv'
    tunename = os.path.splitext(filename)[0]

    # Load the data into the desired structure
    parts = load_data(f"{in_path}/{filename}")

    part_patterns = {}
    tune_patterns = {}

    curr_part_letter = 'A'

    for part_num, bars in parts.items():
        curr_letter = 'a'
        part_label = ""
        if part_num not in part_patterns:
            part_patterns[part_num] = {}

        for bar_num, notes in bars.items():
            v1 = [note['midi_note_num'] for note in notes]

            # Check if there are any previous patterns stored.
            found_match = False
            # Loop backwards from current part to the first part.
            for prev_part_num in reversed(part_patterns):
                # Is this needed?
                if prev_part_num not in part_patterns:
                    continue
                letter_prefix = '' if part_num == prev_part_num else tune_patterns[prev_part_num]['letter']

                # Loop over the bars in the previous part.
                for prev_bar_num, prev_bar in part_patterns[prev_part_num].items():
                    prev_notes = prev_bar['notes']

                    diff = [xi - yi for xi, yi in zip(v1, prev_notes)]
                    comparison = collections.Counter(diff).most_common(1)[0][1]

                    # Compare the current bar with previous bars for commonality.
                    if comparison >= 5:
                        # Identical or near-identical to previous pattern.
                        part_patterns[part_num][bar_num] = {'notes': v1, 'letter': part_patterns[prev_part_num][prev_bar_num]['letter'], 'suffix': "", 'prefix': letter_prefix, 'variant_counter': 0}
                        found_match = True
                        break

                    elif comparison >= 3 and comparison < 5:
                        # Variant of a previous pattern.

                        # Exclude matches with other variants.
                        if part_patterns[prev_part_num][prev_bar_num]['suffix'] != "":
                            continue

                        # Determine suffix number with variant counter.
                        part_patterns[prev_part_num][prev_bar_num]['variant_counter'] += 1
                        suffix = str(part_patterns[prev_part_num][prev_bar_num]['variant_counter'])
                        part_patterns[part_num][bar_num] = {'notes': v1, 'letter': part_patterns[prev_part_num][prev_bar_num]['letter'], 'suffix': suffix, 'prefix': letter_prefix, 'variant_counter': 0}
                        found_match = True
                        break
                if found_match:
                    break
            if not found_match:
                # New unique pattern.
                part_patterns[part_num][bar_num] = {'notes': v1, 'letter': curr_letter, 'suffix': "", 'prefix': "", 'variant_counter': 0}
                curr_letter = chr(ord(curr_letter) + 1)

            part_label += part_patterns[part_num][bar_num]['prefix'] + part_patterns[part_num][bar_num]['letter'] + part_patterns[part_num][bar_num]['suffix']

        tune_patterns[part_num] = {}
        tune_patterns[part_num]['pattern'] = part_label
        tune_patterns[part_num]['variant_counter'] = 0
        # Check if the current part label is the same as any previous ones.
        # Need to remove numbers?

        found_match = False
        # Loop over previous parts in tune.
        for prev_part_num in part_patterns:
            # Skip the current part. Check that this is reference equality.
            if prev_part_num == part_num:
                continue
            # Counter for the number of bars in common between the two parts.
            bar_counter = 0
            # Loop over bars in previous part.
            for prev_part_bar, curr_part_bar in zip(part_patterns[prev_part_num].values(), part_patterns[part_num].values()):
                # Count the number of identical bars.
                if prev_part_bar['letter'] == curr_part_bar['letter']:
                    bar_counter += 1

            #if bar_counter == 8:
            #    tune_patterns[part_num]['letter'] = tune_patterns[prev_part_num]['letter']
            #    # Change to counter.
            #    tune_patterns[part_num]['suffix'] = " "
            #    found_match = True
            #    break
            if bar_counter >= 6:
                tune_patterns[part_num]['letter'] = tune_patterns[prev_part_num]['letter']
                tune_patterns[prev_part_num]['variant_counter'] += 1
                tune_patterns[part_num]['suffix'] = str(tune_patterns[prev_part_num]['variant_counter'])
                found_match = True
                break
        if not found_match:
            tune_patterns[part_num]['letter'] = curr_part_letter
            curr_part_letter = chr(ord(curr_part_letter) + 1)
            tune_patterns[part_num]['suffix'] = " "

    # Return the melodic structure patterns to the calling function.
    output = []
    for part, tune_label in zip(part_patterns.values(), tune_patterns.values()):
        part_label = tune_label['letter'] + tune_label['suffix'] + ": "
        for bar in part.values():
            if tune_label['letter'] == bar['prefix']:
                part_label += bar['letter'] + bar['suffix']
            else:
                part_label += bar['prefix'] + bar['letter'] + bar['suffix']
        output.append(tunename + ", \"" + part_label + "\"\n")

    outputfile.writelines(output)

def analyse_melodic_structure(in_path):
    outputfile = open("melodic_structures.txt", "w")
    filetypes = ('.csv')

    print(in_path)

    if os.path.isdir(in_path):
        filenames = [file for file in os.listdir(in_path) if file.endswith(filetypes)]
        #print(filenames)
        for file in tqdm(filenames, desc='Analysing Melodic Structure.'):
            analyse_tune(in_path, file, outputfile)

if __name__ == "__main__":
    in_path = sys.argv[1]
    analyse_melodic_structure(in_path)
