from music21 import converter, stream, note, meter
import collections
from tqdm import tqdm
import re
import pprint
import sys


# Function: generate a list of notes rin MIDI number format
# in which each eighth-note block is represented by the first note
# value present in the block. Possibly change later to represent each
# block by the predominant note value.
def get_bar_notes(measure):
    notes_in_measure = measure.notes
    midi_numbers = []

    rem = 0
    for n in notes_in_measure:
        if isinstance(n, note.Note):
            # Determine how many eighth notes fit in the current note's duration
            eighths = n.duration.quarterLength * 2
            if rem < 10E-9:
                num_eighths = round(eighths // 1)
                rem = eighths % 1
                for i in range(num_eighths):
                    midi_numbers.append(n.pitch.midi)
                if rem > 10E-9:
                    midi_numbers.append(n.pitch.midi)
            else:
                if eighths + rem >= 1:
                    num_eighths = round((eighths + rem - 1) // 1)
                    rem = (eighths + rem - 1) % 1
                    for i in range(num_eighths):
                        midi_numbers.append(n.pitch.midi)
                    if rem > 10E-9:
                        midi_numbers.append(n.pitch.midi)
                else:
                    rem += eighths
    return midi_numbers


# Function to extract and display MIDI numbers of notes in each bar
def extract_tune_notes(score):
    measures = score.parts[0].getElementsByClass(stream.Measure)
    num, den = score.recurse().getElementsByClass(meter.TimeSignature)[0].ratioString.split('/')
    eighth_notes_per_bar = float(num) * 8 / float(den)

    notes = []
    bar_count = 0
    skip_next = False
    for i in range(len(measures)):
        # If pickup bar has been already concatenated onto the previous bar, skip it.
        if skip_next:
            skip_next = False
            continue
        measure = measures[i]
        midi_numbers = get_bar_notes(measure)

        # Remove initial anacrusis bar if present.
        if len(midi_numbers) < 0.5*eighth_notes_per_bar and i == 0:
            continue

        # Check if current measure is a pick-up measure
        if len(midi_numbers) < eighth_notes_per_bar and i > 0 and i + 1 < len(measures):
            next_midi_numbers = get_bar_notes(measures[i + 1])
            combined_midi_numbers = midi_numbers + next_midi_numbers
            # Check if new bar length is smaller or equal to a full bar length, and revert to two separate bars if not.
            if len(combined_midi_numbers) <= eighth_notes_per_bar:
                bar_notes = combined_midi_numbers
                skip_next = True
            else:
                bar_notes = midi_numbers
        else:
            bar_notes = midi_numbers

        part_count = bar_count // 8
        if bar_count % 8 == 0:
            notes.append([])
        notes[part_count].append(bar_notes)
        bar_count += 1
    return notes


def analyse_tune(tune_notes, tune_name, tune_number):
    delimiter_options = {0: "",
                         1: ", ",
                         2: "",
                         3: "; ",
                         4: "",
                         5: ", ",
                         6: "",
                         7: "."}

    part_patterns = {}
    tune_patterns = {}

    curr_part_letter = 'A'

    part_num = 0
    for part in tune_notes:
        curr_letter = 'a'
        part_label = ""
        if part_num not in part_patterns:
            part_patterns[part_num] = {}

        bar_num = 0
        for bar in part:
            delimiter = delimiter_options[bar_num % 8]
            temp_bar_pattern = {}
            full_match = False
            partial_match = False
            # Check if there are any previous patterns stored.
            # Loop backwards from current part to the first part.
            for prev_part_num in reversed(part_patterns):
                letter_prefix = '' if part_num == prev_part_num else tune_patterns[prev_part_num]['letter']

                # Loop over the bars in the previous part.
                for prev_bar_num, prev_bar in part_patterns[prev_part_num].items():
                    prev_notes = prev_bar['notes']

                    diff = [xi - yi for xi, yi in zip(bar, prev_notes)]
                    comparison = collections.Counter(diff).most_common(1)[0][1]/max(len(bar), len(prev_notes))

                    # Compare the current bar with previous bars for commonality.
                    if comparison >= 5/6:
                        # Identical or near-identical to previous pattern.
                        temp_bar_pattern = {'notes': bar,
                                            'letter': part_patterns[prev_part_num][prev_bar_num]['letter'],
                                            'suffix': part_patterns[prev_part_num][prev_bar_num]['suffix'],
                                            'delimiter': delimiter, 'prefix': letter_prefix,
                                            'variant_counter': 0}
                        full_match = True
                        break

                    elif 3/6 <= comparison < 5/6:
                        # Variant of a previous pattern.

                        # Exclude matches with other variants.
                        if part_patterns[prev_part_num][prev_bar_num]['suffix'] != "":
                            continue

                        # Determine suffix number with variant counter.
                        part_patterns[prev_part_num][prev_bar_num]['variant_counter'] += 1
                        suffix = str(part_patterns[prev_part_num][prev_bar_num]['variant_counter'])
                        temp_bar_pattern = {'notes': bar,
                                            'letter': part_patterns[prev_part_num][prev_bar_num]['letter'],
                                            'suffix': suffix, 'delimiter': delimiter,
                                            'prefix': letter_prefix,
                                            'variant_counter': 0}
                        partial_match = True
                if full_match:
                    break
            if not full_match and not partial_match:
                # New unique pattern.
                part_patterns[part_num][bar_num] = {'notes': bar,
                                                    'letter': curr_letter,
                                                    'suffix': "",
                                                    'delimiter': delimiter,
                                                    'prefix': "",
                                                    'variant_counter': 0}
                curr_letter = chr(ord(curr_letter) + 1)
            else:
                part_patterns[part_num][bar_num] = temp_bar_pattern

            part_label += (part_patterns[part_num][bar_num]['prefix'] + part_patterns[part_num][bar_num]['letter'] +
                           part_patterns[part_num][bar_num]['suffix'])
            bar_num += 1

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
            for prev_part_bar, curr_part_bar in zip(part_patterns[prev_part_num].values(),
                                                    part_patterns[part_num].values()):
                # Count the number of identical bars.
                if prev_part_bar['letter'] == curr_part_bar['letter']:
                    bar_counter += 1

            if bar_counter >= 6:
                tune_patterns[part_num]['letter'] = tune_patterns[prev_part_num]['letter']
                tune_patterns[prev_part_num]['variant_counter'] += 1
                tune_patterns[part_num]['suffix'] = str(tune_patterns[prev_part_num]['variant_counter'])
                found_match = True
                break
        if not found_match:
            tune_patterns[part_num]['letter'] = curr_part_letter
            curr_part_letter = chr(ord(curr_part_letter) + 1)
            tune_patterns[part_num]['suffix'] = ""

        part_num += 1

    # Output the melodic structure patterns to the output file.
    output = []
    for part, tune_label in zip(part_patterns.values(), tune_patterns.values()):
        part_label = tune_label['letter'] + tune_label['suffix']
        structure = ""
        for bar in part.values():
            if tune_label['letter'] == bar['prefix']:
                structure += bar['letter'] + bar['suffix'] + bar['delimiter']
            else:
                structure += bar['prefix'] + bar['letter'] + bar['suffix'] + bar['delimiter']
        output.append(tune_number + "," + tune_name + "," + part_label + ",\"" + structure + "\"\n")

    return output


def extract_abc_info(abc_string):
    lines = abc_string.split('\n')
    title = None
    number = None

    for line in lines:
        if line.startswith('X:'):
            number = line[2:].strip()
        elif line.startswith('T:'):
            title = line[2:].strip()

    return title, number


def remove_macros(abc_string):
    # Split the input into lines
    lines = abc_string.split('\n')

    # To store the uppercase letters to be removed and the processed lines
    letters_to_remove = set()

    # Find macro flags to remove.
    for line in lines:
        if line.startswith('m:'):
            # Find the uppercase letter immediately after 'm:'
            match = re.search(r'm:\s*([A-Z])', line)
            if match:
                letter = match.group(1)
                letters_to_remove.add(letter)

    # Remove all instances of the letters to be removed from the processed string
    processed_lines = []
    for line in lines:
        if not re.search("^[A-Z]:", line):
            for letter in letters_to_remove:
                line = line.replace(letter, '')
            processed_lines.append(line)
        else:
            processed_lines.append(line)
    processed_string = '\n'.join(processed_lines)

    lines = processed_string.split('\n')
    processed_lines = []
    for line in lines:
        if not line.startswith('m:'):
            processed_lines.append(line)
    processed_string = '\n'.join(processed_lines)

    return processed_string


def clean_abc(abc_content):
    lines = abc_content.split('\n')
    # Remove all instances of W
    processed_lines = []
    for line in lines:
        if not re.search("^[A-Z]:", line):
            line = line.replace('W', '')
            line = line.replace('\"   ~\"', '')
            processed_lines.append(line)
        else:
            processed_lines.append(line)
    processed_string = '\n'.join(processed_lines)

    return processed_string


def process_tune(abc_content):
    # Remove ABC macros
    abc_content = remove_macros(abc_content)
    # Substitute repeat shorthand.
    abc_content = abc_content.replace("::", ":||:")
    abc_content = clean_abc(abc_content)

    # Parse the ABC content
    abc_score = converter.parse(abc_content, format='abc')
    # Expand repeats
    expanded_score = abc_score.expandRepeats()

    tune_name, tune_number = extract_abc_info(abc_content)
    # Generate a list of lists containing the notes in each bar as MIDI numbers.
    tune_notes = extract_tune_notes(expanded_score)

    # if tune_number == '6':
    #    pprint.pp(tune_notes)

    # Generate Doherty structure pattern strings.
    return analyse_tune(tune_notes, tune_name, tune_number)


# Function to read the contents of an abc file, strip any header material that does not form part of a description of a
# tune, and return a list containing a string for each tune in the abc file.
def read_abc_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Split the content into lines
    lines = content.split('\n')

    # List of common metadata fields in .abc files
    metadata_fields = {'X:', 'T:', 'M:', 'K:', 'L:', 'Q:', 'C:', 'R:', 'N:', 'P:'}

    # Identify the end of the header section
    header_end_index = 0
    for i, line in enumerate(lines):
        if line.strip()[:2] in metadata_fields:
            header_end_index = i
            break

    # The tunes start at the header end index
    tunes_content = '\n'.join(lines[header_end_index:])

    # Split the remaining content into tunes based on double newlines (indicating a blank line)
    tunes = tunes_content.strip().split('\n\n')

    # Clean up any extra newlines or leading/trailing spaces in each tune
    tunes = [tune.strip() for tune in tunes if tune.strip()]

    return tunes


# Function to extract a list of tunes from the input file, initialise the output file, and run a loop to analyse the
# corpus of tunes.
def main(in_path):
    # open input file & read contents.
    corpus = read_abc_file(in_path)

    outputfile = open("melodic_structures.csv", "w")
    outputfile.writelines("Tune,Title,Part,Structure" + "\n")
    outputfile.close()
    outputfile = open("melodic_structures.csv", "a")
    # Loop over each tune.
    for tune in tqdm(corpus, desc='Analysing Melodic Structures.'):
        outputfile.writelines(process_tune(tune))


if __name__ == "__main__":
    in_path = sys.argv[1]
    main(in_path)
