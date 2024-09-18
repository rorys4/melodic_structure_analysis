from bar_matches import score_thresholds, bar_match_scores
import re

import collections


# Function to generate Doherty melodic structures for each part in a passed tune represented as a nested list
# of MIDI notes.
def analyse_tune(tune_notes, tune_name, tune_number, part_labels, SCORING_METHOD, BEAT_STRENGTH_COEFF):
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
            #if tune_number == '852' and part_num == 2 and bar_num == 0:
            #breakpoint()
            delimiter = delimiter_options[bar_num % 8]
            full_match_pattern = {}
            partial_match_pattern = {}
            best_full_match_score, best_partial_match_score = score_thresholds(SCORING_METHOD)
            best_transposition_amount = float('inf')
            full_match = False
            partial_match = False
            variant_part = None
            variant_bar = None
            #part_repeat = False
            # Loop backwards from current part to the first part.
            for prev_part_num in part_patterns:
                #while True:
                letter_prefix = '' if part_num == prev_part_num else part_labels[prev_part_num]
                # Loop over the bars in the previous parts and compare for commonality.
                for prev_bar_num, prev_bar in part_patterns[prev_part_num].items():
                    full_match_score, partial_match_score, transposition_amount = bar_match_scores(bar, prev_bar['notes'], SCORING_METHOD, BEAT_STRENGTH_COEFF)

                    # Identify fully transposed bars.
                    # diff = [xi - yi for xi, yi in zip(bar, prev_bar['notes'])]
                    # most_common_delta = collections.Counter(diff).most_common(1)[0]
                    # comparison = most_common_delta[1] / max(len(bar), len(prev_bar['notes']))
                    # if comparison >= 1 - 1E-14 and most_common_delta[0] != 0:
                    #     print(tune_number, end=",")
                    #     print(part_labels[prev_part_num] + "," + str(prev_bar_num), end=",")
                    #     print(part_labels[part_num] + "," + str(bar_num), end=",")
                    #     print(str(most_common_delta[0]), end="\n")

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

            # Check if any parts have been revealed to be variant parts.
            #part_labels, part_patterns, part_repeat = part_variant_check(part_patterns, part_patterns, part_num, part_labels)

            # if not part_repeat:
                # break

            # Store current value of current_letter.
            curr_letters[part_labels[part_num]] = curr_letter
        part_num += 1
    # print(part_patterns)
    # print('\n')
    # print(part_labels)
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


# def part_variant_check(part_patterns, part_patterns, part_num, part_labels):
#     # Exclude the first part and parts that are already variant parts.
#     if part_num == 0:
#         return part_labels, False
#
#     # Create a list of the bar prefix values.
#     bar_prefixes = [bar['prefix'] for bar in part_patterns[part_num].values()]
#     # Check if there are at least 4 repeated bars from another non-related part.
#     most_common_prefix = collections.Counter(bar_prefixes).most_common(1)[0]
#
#     # Get the number of the matched part.
#     matched_part =
#
#     if most_common_prefix[1] == 8:
#         part_labels[part_num] = most_common_prefix[0]
#
#         # Rename all subsequent parts to X - 1 of their original letter.
#         for subsequent_part in range(part_num + 1, len(part_patterns[part_num]):
#             # Part is variant of current part.
#             if strip_variant_number(part_labels[subsequent_part]) == strip_variant_number(part_labels[part_num]):
#                 part_letter = chr(ord(strip_variant_number(part_labels[subsequent_part]))) + 1)
#                 part_labels[subsequent_part] =
#             # Part has a higher letter value.
#             elif part_labels[subsequent_part] > part_labels[part_num]:
#                 if not part_labels[subsequent_part]:
#                 part_labels[subsequent_part]
#
#         # Remove this part.
#         del part_labels[part_num]
#         del part_patterns[part_num]
#         part_repeat = False
#
#
#     elif most_common_prefix[1] >= 4 and not is_variant(part_labels[part_num]):
#         # Relabel the current part as a variant of prev_part.
#         variant_counter = ...
#         part_labels[part_num] = most_common_prefix[0] + variant_counter
#
#         # Relabel all parts referring to this part.
#         for subsequent_part in range(part_num + 1, len(part_labels):
#             # Part is variant of current part.
#             if strip_variant_number(part_labels[subsequent_part]) == strip_variant_number(part_labels[part_num]):
#                 part_letter = chr(ord(strip_variant_number(part_labels[subsequent_part]))) + 1)
#                 part_labels[subsequent_part] =
#             # Part has a higher letter value.
#             elif part_labels[subsequent_part] > part_labels[part_num]:
#                 if not part_labels[subsequent_part]:
#                     part_labels[subsequent_part]
#
#         # Re-label all subsequent parts and bars to X - 1 of their original letter.
#
#         part_repeat = True
#
# return part_labels, part_patterns, part_repeat
