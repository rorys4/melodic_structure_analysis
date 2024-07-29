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
    beatStrengths = []

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
                    beatStrengths.append(n.beatStrength)
                if rem > 10E-9:
                    midi_numbers.append(n.pitch.midi)
                    beatStrengths.append(n.beatStrength)
            else:
                if eighths + rem >= 1:
                    num_eighths = round((eighths + rem - 1) // 1)
                    rem = (eighths + rem - 1) % 1
                    for i in range(num_eighths):
                        midi_numbers.append(n.pitch.midi)
                        beatStrengths.append(n.beatStrength)
                    if rem > 10E-9:
                        midi_numbers.append(n.pitch.midi)
                        beatStrengths.append(n.beatStrength)
                else:
                    rem += eighths
    return midi_numbers, beatStrengths


# Function to extract and display MIDI numbers of notes in each bar
def extract_tune_notes(score):
    measures = score.parts[0].getElementsByClass(stream.Measure)
    num, den = score.recurse().getElementsByClass(meter.TimeSignature)[0].ratioString.split('/')
    eighth_notes_per_bar = float(num) * 8 / float(den)
    notes = []
    beat_strengths = []
    measure_nums = []
    bar_count = 0
    skip_next = False
    for i in range(len(measures)):
        # If pickup bar has been already concatenated onto the previous bar, skip it.
        if skip_next:
            skip_next = False
            continue
        measure = measures[i]
        midi_numbers,beatStrengths = get_bar_notes(measure)
        # Remove loose pick-up bar if present.
        if len(midi_numbers) < 0.5*eighth_notes_per_bar:
            continue
        # Check if this bar is missing a note.
        if len(midi_numbers) < eighth_notes_per_bar and i > 0 and i + 1 < len(measures):
            #combining with next bar in case it's a pick-up bar.
            next_midi_numbers, next_beatStrengths = get_bar_notes(measures[i + 1])
            combined_midi_numbers = midi_numbers + next_midi_numbers
            # Check if new bar length is smaller or equal to a full bar length, and revert to two separate bars if not.
            if len(combined_midi_numbers) <= eighth_notes_per_bar:
                bar_notes = combined_midi_numbers
                beatStrengths = beatStrengths + next_beatStrengths
                skip_next = True
            else:
                bar_notes = midi_numbers
        # Extend final note of tune if the bar is short.
        elif len(midi_numbers) == eighth_notes_per_bar - 1 and i == len(measures) - 1:
            midi_numbers.append(midi_numbers[len(midi_numbers) - 2])
            bar_notes = midi_numbers
            # Is this wrong?
            beatStrengths.append(beatStrengths[len(beatStrengths) - 2])
        else:
            bar_notes = midi_numbers
        part_count = bar_count // 8
        if bar_count % 8 == 0:
            notes.append([])
            beat_strengths.append([])
            measure_nums.append([])
        notes[part_count].append(bar_notes)
        beat_strengths[part_count].append(beatStrengths)
        measure_nums[part_count].append(measure.number)
        bar_count += 1

    # Part labelling
    curr_letter = 'A'
    non_variant_part = []
    variant_counter = []
    part_labels = []
    removal_list = []
    for part_num in range(len(measure_nums)):
        part_labels.append('')
        non_variant_part.append(False)
        variant_counter.append(1)
        score = 0
        match_found = False
        for prev_part_num in range(part_num):
            diff = [xi - yi for xi, yi in zip(measure_nums[part_num], measure_nums[prev_part_num])]
            num_common = diff.count(0)
            # Full match.
            if num_common == 8:
                part_labels[part_num] = part_labels[prev_part_num]
                match_found = True
                removal_list.append(part_num)
                break
            # Partial match.
            elif num_common >= 4:
                if num_common > score and non_variant_part[prev_part_num]:
                    part_labels[part_num] = part_labels[prev_part_num] + str(variant_counter[prev_part_num])
                    variant_counter[prev_part_num] += 1
                    score = num_common
                    match_found = True
        # New part letter.
        if not match_found:
            part_labels[part_num] = curr_letter
            curr_letter = chr(ord(curr_letter) + 1)
            non_variant_part[part_num] = True
    # Remove duplicate parts.
    for i in reversed(removal_list):
        notes.pop(i)
        part_labels.pop(i)
    return notes, part_labels, beat_strengths


# Function to generate Doherty melodic structures for each part in a passed tune represented as a nested list
# of MIDI notes.
def analyse_tune(tune_notes, tune_name, tune_number, part_labels, beat_strengths):
    delimiter_options = {0: "",
                         1: ", ",
                         2: "",
                         3: "; ",
                         4: "",
                         5: ", ",
                         6: "",
                         7: "."}
    part_patterns = {}
    part_num = 0
    curr_letters = {}
    for part in tune_notes:
        if is_variant(part_labels[part_num]):
            curr_letter = curr_letters.get(strip_variant_number(part_labels[part_num]))
        else:
            curr_letter = 'a'
        if part_num not in part_patterns:
            part_patterns[part_num] = {}
        bar_num = 0
        for bar in part:
            delimiter = delimiter_options[bar_num % 8]
            temp_bar_pattern = {}
            best_full_match_score = 5/6
            best_partial_match_score = 3/6
            full_match = False
            partial_match = False
            # Loop backwards from current part to the first part.
            for prev_part_num in part_patterns:
                letter_prefix = '' if part_num == prev_part_num else part_labels[prev_part_num]
                # Loop over the bars in the previous parts and compare for commonality.
                for prev_bar_num, prev_bar in part_patterns[prev_part_num].items():
                    prev_notes = prev_bar['notes']
                    diff = [xi - yi for xi, yi in zip(bar, prev_notes)]
                    # For full match (without transposition)
                    num_common = diff.count(0)/max(len(bar), len(prev_notes))
                    # For partial match (transposition allowed)
                    most_common_delta = collections.Counter(diff).most_common(1)[0]
                    comparison = most_common_delta[1]/max(len(bar), len(prev_notes))

                    full_match_score = num_common
                    partial_match_score = comparison / (abs(most_common_delta[0]) + 1)

                    # Identical or near-identical to previous pattern.
                    if full_match_score > best_full_match_score:
                        full_match = True
                        best_full_match_score = full_match_score
                        temp_bar_pattern = {'notes': bar,
                                            'letter': part_patterns[prev_part_num][prev_bar_num]['letter'],
                                            'suffix': part_patterns[prev_part_num][prev_bar_num]['suffix'],
                                            'delimiter': delimiter,
                                            'prefix': letter_prefix,
                                            'variant_counter': 0}
                    # Variant of a previous pattern.
                    elif not full_match and partial_match_score > best_partial_match_score:
                        # Exclude matches with other variants.
                        if part_patterns[prev_part_num][prev_bar_num]['suffix'] == "":
                            partial_match = True
                            best_partial_match_score = partial_match_score
                            # Determine suffix number with variant counter.
                            part_patterns[prev_part_num][prev_bar_num]['variant_counter'] += 1
                            temp_bar_pattern = {'notes': bar,
                                                'letter': part_patterns[prev_part_num][prev_bar_num]['letter'],
                                                'suffix': str(part_patterns[prev_part_num][prev_bar_num]['variant_counter']),
                                                'delimiter': delimiter,
                                                'prefix': letter_prefix,
                                                'variant_counter': 0}
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
            bar_num += 1
            # Check if any parts have been revealed to be variant parts.
            # part_variant_check(part_patterns, part_labels)

            # Store current value of current_letter.
            curr_letters[part_labels[part_num]] = curr_letter
        part_num += 1
    # Output the melodic structure patterns to the output file.
    output = []
    for part, tune_label in zip(part_patterns.values(), part_labels):
        structure = ""
        for bar in part.values():
            if tune_label[0] == bar['prefix']:
                structure += bar['letter'] + bar['suffix'] + bar['delimiter']
            else:
                structure += bar['prefix'] + bar['letter'] + bar['suffix'] + bar['delimiter']
        output.append(tune_number + "," + tune_name + "," + tune_label + ",\"" + structure + "\"\n")
    return output


# Return true if the passed part or bar pattern is a variant.
def is_variant(pattern):
    return any(char.isdigit() for char in pattern)


# Function to return a pattern without a variant number.
def strip_variant_number(pattern):
    return "".join(re.findall("[a-zA-Z]+", pattern))


# Function to extract the tune number and title from its ABC representation.
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
    tune_notes, part_labels, beat_strengths = extract_tune_notes(expanded_score)
    #print(tune_number + " " + tune_name + "\n")
    # if tune_number == '6':
    #    pprint.pp(tune_notes)
    # Generate Doherty structure pattern strings.
    return analyse_tune(tune_notes, tune_name, tune_number, part_labels, beat_strengths)


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
    #print("Tune,Part1,Bar1,Part2,Bar2,Delta")
    # Loop over each tune.
    for tune in tqdm(corpus, desc='Analysing Melodic Structures.'):
    #for tune in corpus:
        outputfile.writelines(process_tune(tune))


if __name__ == "__main__":
    #in_path = sys.argv[1]
    in_path = '/home/roro/Documents/RA2/datasets/ABC/song_names_single_line/ONeills1001.abc'
    main(in_path)
