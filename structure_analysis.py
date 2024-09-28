from bar_matches import bar_match_scores
import re


# Function to generate Doherty melodic structures for each part in a passed tune represented as a nested list
# of MIDI notes.
def analyse_tune(tune_notes, tune_name, tune_number, eighth_notes_per_bar, part_labels, SCORING_METHOD, BEAT_STRENGTH_COEFF, full_match_threshold, variant_match_threshold):
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
            full_match_pattern = {}
            partial_match_pattern = {}
            # Reset the best match values to the threshold values.
            best_full_match_score = full_match_threshold
            best_partial_match_score = variant_match_threshold
            best_transposition_amount = float('inf')
            full_match = False
            partial_match = False
            variant_part = None
            variant_bar = None
            for prev_part_num in part_patterns:
                letter_prefix = '' if part_num == prev_part_num else part_labels[prev_part_num]
                # Loop over the bars in the previous parts and compare for commonality.
                for prev_bar_num, prev_bar in part_patterns[prev_part_num].items():
                    full_match_score, partial_match_score, transposition_amount = bar_match_scores(bar, prev_bar['notes'], eighth_notes_per_bar, SCORING_METHOD, BEAT_STRENGTH_COEFF)
                    # Identical or near-identical to previous pattern.
                    if full_match_score >= best_full_match_score:
                        full_match = True
                        best_full_match_score = full_match_score
                        if part_patterns[prev_part_num][prev_bar_num]['prefix'] == "":
                            prefix = letter_prefix
                        else:
                            prefix = part_patterns[prev_part_num][prev_bar_num]['prefix']
                        full_match_pattern = {'notes': bar,
                                              'letter': part_patterns[prev_part_num][prev_bar_num]['letter'],
                                              'suffix': part_patterns[prev_part_num][prev_bar_num]['suffix'],
                                              'delimiter': delimiter,
                                              'prefix': prefix,
                                              'variant_counter': 0}
                    # Variant of a previous pattern.
                    elif (not full_match and ((partial_match_score > best_partial_match_score) or
                          (abs(partial_match_score - best_partial_match_score) < 1E-16
                           and transposition_amount < best_transposition_amount))):
                        # Exclude matches with other variants.
                        if part_patterns[prev_part_num][prev_bar_num]['suffix'] == "":
                            partial_match = True
                            best_partial_match_score = partial_match_score
                            best_transposition_amount = transposition_amount
                            # Determine suffix number with variant counter.
                            variant_part = prev_part_num
                            variant_bar = prev_bar_num
                            partial_match_pattern = {'notes': bar,
                                                     'letter': part_patterns[prev_part_num][prev_bar_num]['letter'],
                                                     'suffix': '',
                                                     'delimiter': delimiter,
                                                     'prefix': letter_prefix,
                                                     'variant_counter': 0}
            if full_match:
                part_patterns[part_num][bar_num] = full_match_pattern
            elif partial_match:
                part_patterns[part_num][bar_num] = partial_match_pattern
                part_patterns[variant_part][variant_bar]['variant_counter'] += 1
                part_patterns[part_num][bar_num]['suffix'] = str(part_patterns[variant_part][variant_bar]['variant_counter'])
            else:
                # New unique pattern.
                part_patterns[part_num][bar_num] = {'notes': bar,
                                                    'letter': curr_letter,
                                                    'suffix': "",
                                                    'delimiter': delimiter,
                                                    'prefix': "",
                                                    'variant_counter': 0}
                curr_letter = chr(ord(curr_letter) + 1)
            bar_num += 1
            # Store current value of current_letter.
            curr_letters[part_labels[part_num]] = curr_letter
        part_num += 1
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
