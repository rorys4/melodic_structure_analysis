import math
from collections import defaultdict


# Handy class to allow dot notation access to dict keys.
class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


EXCLUDE_SHORT_NOTES = False

# Method Switches
BASIC = 0
REQUIRE_1st_NOTE = 1
REQUIRE_1st_AND_4th_NOTES = 2
LCP = 3
CONTIGUOUS_NOTES = 4
DIV_BY_TRSPS_AMT = 5
CUSTOM_BEAT_STRENGTH = 6
HARD_CODED_BEAT_STRENGTH_LINEAR = 7
HARD_CODED_BEAT_STRENGTH_GEOMETRIC = 8
NEW_RULES = 9


# Compute the match scores of a pair of bars.
def bar_match_scores(bar, prev_notes, eighth_notes_per_bar, SCORING_METHOD, beat_strength_coeff):
    if SCORING_METHOD == BASIC:
        return score_basic(bar, prev_notes)
    if SCORING_METHOD == REQUIRE_1st_NOTE:
        return score_require_first_note(bar, prev_notes)
    if SCORING_METHOD == REQUIRE_1st_AND_4th_NOTES:
        return score_require_first_and_fourth_notes(bar, prev_notes)
    if SCORING_METHOD == LCP:
        return score_longest_common_prefix(bar, prev_notes)
    if SCORING_METHOD == CONTIGUOUS_NOTES:
        return score_longest_contiguous_match(bar, prev_notes)
    if SCORING_METHOD == DIV_BY_TRSPS_AMT:
        return score_div_by_transposition_amount(bar, prev_notes)
    if SCORING_METHOD == CUSTOM_BEAT_STRENGTH:
        return score_beat_strength_sum2(bar, prev_notes, beat_strength_coeff)
    if SCORING_METHOD == HARD_CODED_BEAT_STRENGTH_LINEAR:
        return score_beat_strength_sum3(bar, prev_notes, eighth_notes_per_bar)
    if SCORING_METHOD == HARD_CODED_BEAT_STRENGTH_GEOMETRIC:
        return score_beat_strength_sum4(bar, prev_notes, eighth_notes_per_bar, beat_strength_coeff)
    if SCORING_METHOD == NEW_RULES:
        return score_new_rules(bar, prev_notes)


def score_basic(bar, prev_notes):
    bar_duration = max(sum([n.duration for n in bar]), sum([n.duration for n in prev_notes]))
    i, j = 0, 0
    pairs = []
    # Iterate over both lists in single loop. (Offsets are ordered.)
    while i < len(bar) and j < len(prev_notes):
        if bar[i].offset == prev_notes[j].offset:
            # If the offset values match, subtract note values and store in the result
            note_diff = bar[i].noteValue - prev_notes[j].noteValue
            if not EXCLUDE_SHORT_NOTES or (bar[i].duration >= 1 and prev_notes[j].duration >= 1):
                pairs.append(dotdict({'diff': note_diff, 'duration': min(bar[i].duration, prev_notes[j].duration)}))
            i += 1
            j += 1
        elif bar[i]['offset'] < prev_notes[j]['offset']:
            # Increment i if bar has a smaller offset
            i += 1
        else:
            # Increment j if prev_notes has a smaller offset
            j += 1
    proportion_in_common = sum([n.duration for n in pairs if n.diff == 0])/bar_duration
    full_match_score = proportion_in_common
    # For partial match (transposition allowed)
    diff_durations = defaultdict(float)
    # Find aggregate duration for each diff value.
    if len(pairs) > 0:
        for i in pairs:
            diff_durations[i['diff']] += i['duration']
        most_prevalent_delta = max(diff_durations.items(), key=lambda x: (x[1], -x[0]))
        partial_match_score = most_prevalent_delta[1] / bar_duration
        transposition_amount = abs(most_prevalent_delta[0])
    else:
        partial_match_score = 0
        transposition_amount = 0
    return full_match_score, partial_match_score, transposition_amount


def score_require_first_note(bar, prev_notes):
    bar_duration = max(sum([n.duration for n in bar]), sum([n.duration for n in prev_notes]))
    i, j = 0, 0
    pairs = []
    # Iterate over both lists in single loop. (Offsets are ordered.)
    while i < len(bar) and j < len(prev_notes):
        if bar[i].offset == prev_notes[j].offset:
            # If the offset values match, subtract note values and store in the result
            note_diff = bar[i].noteValue - prev_notes[j].noteValue
            pairs.append(dotdict({'diff': note_diff, 'offset': bar[i].offset, 'duration': min(bar[i].duration, prev_notes[j].duration)}))
            i += 1
            j += 1
        elif bar[i]['offset'] < prev_notes[j]['offset']:
            # Increment i if bar has a smaller offset
            i += 1
        else:
            # Increment j if prev_notes has a smaller offset
            j += 1
    proportion_in_common = sum([n.duration for n in pairs if n.diff == 0])/bar_duration

    if bar[0] != prev_notes[0] or pairs[0].offset != 0:
        full_match_score = 0
    else:
        full_match_score = proportion_in_common

    # For partial match (transposition allowed)
    diff_durations = defaultdict(float)
    # Find aggregate duration for each diff value.
    for i in pairs:
        diff_durations[i.diff] += i.duration
    most_prevalent_delta = max(diff_durations.items(), key=lambda x: (x[1], -x[0]))

    if pairs[0].diff != most_prevalent_delta[0] or pairs[0].offset != 0:
        partial_match_score = 0
        transposition_amount = 0
    else:
        partial_match_score = most_prevalent_delta[1] / bar_duration
        transposition_amount = abs(most_prevalent_delta[0])
    return full_match_score, partial_match_score, transposition_amount


def score_require_first_and_fourth_notes(bar, prev_notes):
    bar_duration = max(sum([n.duration for n in bar]), sum([n.duration for n in prev_notes]))
    i, j = 0, 0
    pairs = []
    # Iterate over both lists in single loop. (Offsets are ordered.)
    while i < len(bar) and j < len(prev_notes):
        if bar[i].offset == prev_notes[j].offset:
            # If the offset values match, subtract note values and store in the result
            note_diff = bar[i].noteValue - prev_notes[j].noteValue
            pairs.append(dotdict({'diff': note_diff, 'offset': bar[i].offset, 'duration': min(bar[i].duration, prev_notes[j].duration)}))
            i += 1
            j += 1
        elif bar[i]['offset'] < prev_notes[j]['offset']:
            # Increment i if bar has a smaller offset
            i += 1
        else:
            # Increment j if prev_notes has a smaller offset
            j += 1
    proportion_in_common = sum([n.duration for n in pairs if n.diff == 0])/bar_duration

    middle_note_offset = int(bar_duration/2)
    # Find the middle note.
    middle_diff = next((pair.diff for pair in pairs if pair.offset == middle_note_offset), None)

    if pairs[0].diff != 0 or pairs[0].offset != 0 or middle_diff != 0:
        full_match_score = 0
    else:
        full_match_score = proportion_in_common

    # For partial match (transposition allowed)
    diff_durations = defaultdict(float)
    # Find aggregate duration for each diff value.
    for i in pairs:
        diff_durations[i.diff] += i.duration
    most_prevalent_delta = max(diff_durations.items(), key=lambda x: (x[1], -x[0]))

    if pairs[0].diff != most_prevalent_delta[0] or pairs[0].offset != 0 or middle_diff != most_prevalent_delta[0]:
        partial_match_score = 0
        transposition_amount = 0
    else:
        partial_match_score = most_prevalent_delta[1] / bar_duration
        transposition_amount = abs(most_prevalent_delta[0])
    return full_match_score, partial_match_score, transposition_amount


def score_longest_common_prefix(bar, prev_notes):
    bar_duration = max(sum([n.duration for n in bar]), sum([n.duration for n in prev_notes]))
    i, j = 0, 0
    pairs = []
    index_b = 0
    index_p = 0
    # Iterate over both lists in single loop. (Offsets are ordered.)
    while i < len(bar) and j < len(prev_notes):
        if bar[i].offset == prev_notes[j].offset:
            if bar[i].noteIndex == index_b and prev_notes[j].noteIndex == index_p:
                # If the offset values match, subtract note values and store in the result
                note_diff = bar[i].noteValue - prev_notes[j].noteValue
                pairs.append(dotdict({'diff': note_diff, 'duration': min(bar[i].duration, prev_notes[j].duration), 'beatStrength': bar[i].beatStrength, 'index': index_b}))
                i += 1
                j += 1
                index_b += 1
                index_p += 1
            else:
                break
        elif bar[i].offset < prev_notes[j].offset:
            # Increment i if bar has a smaller offset
            i += 1
        else:
            # Increment j if prev_notes has a smaller offset
            j += 1

    duration_sum = 0
    index = 0
    for p in pairs:
        if p.diff == 0 and p.index == index:
            duration_sum += p.duration
            index += 1
        else:
            break
    full_match_score = duration_sum / bar_duration

    first_diff = None
    duration_sum = 0
    index = 0
    for p in pairs:
        if p.index == 0:
            first_diff = p.diff
            index += 1
        if p.diff == first_diff and p.index == index:
            duration_sum += p.duration
            index += 1
        else:
            break
    if len(pairs) > 0:
        partial_match_score = duration_sum / bar_duration
        transposition_amount = abs(pairs[0].diff)
    else:
        partial_match_score = 0
        transposition_amount = 0
    return full_match_score, partial_match_score, transposition_amount


# Function to find the duration of the longest set of contiguous notes with the same diff value.
# Concern: Because the index attribute is based on the current bar, this type of bar matching is not necessarily
# commutative.
def largest_consecutive_duration_sum(pairs):
    if not pairs:
        return 0, float('inf')
    max_sum = 0
    max_diff = None
    current_sum = pairs[0].duration
    current_diff = pairs[0].diff
    for i in range(1, len(pairs)):
        if pairs[i].diff == current_diff and pairs[i].index == pairs[i - 1].index + 1:
            current_sum += pairs[i].duration
            if current_sum > max_sum:
                max_sum = current_sum
                max_diff = current_diff
        else:
            current_sum = pairs[i].duration
            current_diff = pairs[i].diff
    # Check if the last sequence is the largest
    if current_sum > max_sum:
        max_sum = current_sum
        max_diff = current_diff
    return max_sum, max_diff


# Find the duration of the longest sequence of notes with a zero diff value.
def largest_zero_diff_consecutive_duration_sum(pairs):
    if not pairs:
        return 0
    max_sum = 0
    current_sum = 0
    last_index = None
    for pair in pairs:
        if pair.diff == 0:
            if last_index is None or pair.index == last_index + 1:
                current_sum += pair.duration
                max_sum = max(max_sum, current_sum)
            else:
                current_sum = pair.duration
            last_index = pair.index
        else:
            current_sum = 0
            last_index = None
    return max_sum


def score_longest_contiguous_match(bar, prev_notes):
    bar_duration = max(sum([n.duration for n in bar]), sum([n.duration for n in prev_notes]))
    i, j = 0, 0
    pairs = []
    index_b = 0
    index_p = 0
    # Iterate over both lists in single loop. (Offsets are ordered.)
    while i < len(bar) and j < len(prev_notes):
        if bar[i].offset == prev_notes[j].offset:
            if bar[i].noteIndex == index_b and prev_notes[j].noteIndex == index_p:
                # If the offset values match, subtract note values and store in the result
                note_diff = bar[i].noteValue - prev_notes[j].noteValue
                pairs.append(dotdict({'diff': note_diff, 'duration': min(bar[i].duration, prev_notes[j].duration), 'beatStrength': bar[i].beatStrength, 'index': index_b}))
                i += 1
                j += 1
                index_b += 1
                index_p += 1
            else:
                break
        elif bar[i].offset < prev_notes[j].offset:
            # Increment i if bar has a smaller offset
            i += 1
        else:
            # Increment j if prev_notes has a smaller offset
            j += 1

    full_match_score = largest_zero_diff_consecutive_duration_sum(pairs) / bar_duration
    transposed_match_duration, diff_value = largest_consecutive_duration_sum(pairs)

    partial_match_score = transposed_match_duration / bar_duration
    transposition_amount = abs(diff_value)
    return full_match_score, partial_match_score, transposition_amount


def score_div_by_transposition_amount(bar, prev_notes):
    bar_duration = max(sum([n.duration for n in bar]), sum([n.duration for n in prev_notes]))
    i, j = 0, 0
    pairs = []
    # Iterate over both lists in single loop. (Offsets are ordered.)
    while i < len(bar) and j < len(prev_notes):
        if bar[i].offset == prev_notes[j].offset:
            # If the offset values match, subtract note values and store in the result
            note_diff = bar[i].noteValue - prev_notes[j].noteValue
            if not EXCLUDE_SHORT_NOTES or (bar[i].duration >= 1 and prev_notes[j].duration >= 1):
                pairs.append(dotdict({'diff': note_diff, 'duration': min(bar[i].duration, prev_notes[j].duration)}))
            i += 1
            j += 1
        elif bar[i]['offset'] < prev_notes[j]['offset']:
            # Increment i if bar has a smaller offset
            i += 1
        else:
            # Increment j if prev_notes has a smaller offset
            j += 1
    proportion_in_common = sum([n.duration for n in pairs if n.diff == 0])/bar_duration
    full_match_score = proportion_in_common
    # For partial match (transposition allowed)
    diff_durations = defaultdict(float)
    # Find aggregate duration for each diff value.
    if len(pairs) > 0:
        for i in pairs:
            diff_durations[i['diff']] += i['duration']
        most_prevalent_delta = max(diff_durations.items(), key=lambda x: (x[1], -x[0]))
        transposition_amount = abs(most_prevalent_delta[0])
        partial_match_score = most_prevalent_delta[1] / (bar_duration * transposition_amount + 1)
    else:
        partial_match_score = 0
        transposition_amount = 0
    return full_match_score, partial_match_score, transposition_amount


def score_beat_strength_sum2(bar, prev_notes, beat_strength_coeff):
    # Compute the total bar duration.
    bar_duration = max(sum([n.duration for n in bar]), sum([n.duration for n in prev_notes]))
    i, j = 0, 0
    pairs = []
    # Find note pairs with the same offsets.
    # Iterate over both lists in single loop. (Offsets are ordered.)
    while i < len(bar) and j < len(prev_notes):
        # If the offset values match.
        if bar[i].offset == prev_notes[j].offset:
            # Subtract note values and store in the result.
            note_diff = bar[i].noteValue - prev_notes[j].noteValue
            # Compute the beat strength normalising constant.
            bs_sum = sum([pow(beat_strength_coeff, math.log2(n.beatStrength))*n.duration for n in bar])/bar_duration
            # Compute the beat strength value for the current note.
            custom_beat_strength = pow(beat_strength_coeff, math.log2(bar[i].beatStrength)) / bs_sum
            # Store the result.
            pairs.append(dotdict({'diff': note_diff, 'duration': min(bar[i].duration, prev_notes[j].duration), 'beatStrength': custom_beat_strength}))
            i += 1
            j += 1
        elif bar[i].offset < prev_notes[j].offset:
            # Increment i if bar has a smaller offset
            i += 1
        else:
            # Increment j if prev_notes has a smaller offset
            j += 1
    full_match_score = sum([n.duration*n.beatStrength for n in pairs if n.diff == 0])/bar_duration
    # For partial match (transposition allowed)
    diff_durations = defaultdict(float)
    # Find aggregate duration for each note difference value.
    for i in pairs:
        diff_durations[i.diff] += i.duration
    # Sort the diff_durations dict to find the most prevalent note difference value.
    most_prevalent_delta = max(diff_durations.items(), key=lambda x: (x[1], -x[0]))
    partial_match_score = sum([n.duration*n.beatStrength for n in pairs if n.diff == most_prevalent_delta[0]])/bar_duration
    transposition_amount = abs(most_prevalent_delta[0])
    return full_match_score, partial_match_score, transposition_amount


def score_beat_strength_sum3(bar, prev_notes, eighth_notes_per_bar):
    weightings_dict = {
        1: [1],
        2: [3, 1],
        3: [3, 1, 1],
        4: [4, 1, 2, 1],
        5: [5, 1, 1, 1, 1],  # I made this one up.
        6: [6, 1, 2, 4, 1, 2],
        7: [6, 1, 1, 1, 1, 1, 1], # I made this one up.
        8: [6, 1, 2, 1, 4, 1, 2, 1],
        9: [6, 1, 2, 4, 1, 2, 4, 1, 2]
    }
    bar_len = eighth_notes_per_bar
    beat_weightings = weightings_dict.get(bar_len)
    if beat_weightings is None:
        beat_weightings = [6] + [1]*(bar_len - 1)
    bar_duration = max(sum([n.duration for n in bar]), sum([n.duration for n in prev_notes]))
    bs_sum = sum([beat_weightings[math.floor(n.offset)] * n.duration for n in bar]) / bar_duration
    i, j = 0, 0
    pairs = []
    # Iterate over both lists in single loop. (Offsets are ordered.)
    while i < len(bar) and j < len(prev_notes):
        if bar[i].offset == prev_notes[j].offset:
            # If the offset values match, subtract note values and store in the result
            note_diff = bar[i].noteValue - prev_notes[j].noteValue
            custom_beat_strength = beat_weightings[math.floor(bar[i].offset)] / bs_sum
            pairs.append(dotdict({'diff': note_diff, 'duration': min(bar[i].duration, prev_notes[j].duration), 'beatStrength': custom_beat_strength}))
            i += 1
            j += 1
        elif bar[i].offset < prev_notes[j].offset:
            # Increment i if bar has a smaller offset
            i += 1
        else:
            # Increment j if prev_notes has a smaller offset
            j += 1
    full_match_score = sum([n.duration*n.beatStrength for n in pairs if n.diff == 0])/bar_duration
    # For partial match (transposition allowed)
    diff_durations = defaultdict(float)
    # Find aggregate duration for each diff value.
    for i in pairs:
        diff_durations[i.diff] += i.duration
    most_prevalent_delta = max(diff_durations.items(), key=lambda x: (x[1], -x[0]))
    partial_match_score = sum([n.duration*n.beatStrength for n in pairs if n.diff == most_prevalent_delta[0]])/bar_duration
    transposition_amount = abs(most_prevalent_delta[0])
    return full_match_score, partial_match_score, transposition_amount


def score_beat_strength_sum4(bar, prev_notes, eighth_notes_per_bar, beat_strength_coeff):
    weightings_dict = {
        1: [1],
        2: [0, -2],
        3: [0, -2, -2],
        4: [0, -3, -2, -3],
        5: [0, -4, -4, -4, -4],  # I made this one up.
        6: [0, -5, -4, -2, -5, -4],
        7: [0, -5, -5, -5, -5, -5, -5], # I made this one up.
        8: [0, -5, -4, -5, -2, -5, -4, -5],
        9: [0, -5, -4, -2, -5, -4, -2, -5, -4]
    }
    bar_len = eighth_notes_per_bar
    beat_weightings = weightings_dict.get(bar_len)
    if beat_weightings == None:
        beat_weightings = [6] + [1]*(bar_len - 1)
    bar_duration = max(sum([n.duration for n in bar]), sum([n.duration for n in prev_notes]))
    bs_sum = sum([pow(beat_strength_coeff, beat_weightings[math.floor(n.offset)]) * n.duration for n in bar]) / bar_duration
    i, j = 0, 0
    pairs = []
    # Iterate over both lists in single loop. (Offsets are ordered.)
    while i < len(bar) and j < len(prev_notes):
        if bar[i].offset == prev_notes[j].offset:
            # If the offset values match, subtract note values and store in the result
            note_diff = bar[i].noteValue - prev_notes[j].noteValue
            custom_beat_strength = pow(beat_strength_coeff, beat_weightings[math.floor(bar[i].offset)]) / bs_sum
            pairs.append(dotdict({'diff': note_diff, 'duration': min(bar[i].duration, prev_notes[j].duration), 'beatStrength': custom_beat_strength}))
            i += 1
            j += 1
        elif bar[i].offset < prev_notes[j].offset:
            # Increment i if bar has a smaller offset
            i += 1
        else:
            # Increment j if prev_notes has a smaller offset
            j += 1
    full_match_score = sum([n.duration*n.beatStrength for n in pairs if n.diff == 0])/bar_duration
    # For partial match (transposition allowed)
    diff_durations = defaultdict(float)
    # Find aggregate duration for each diff value.
    for i in pairs:
        diff_durations[i.diff] += i.duration
    most_prevalent_delta = max(diff_durations.items(), key=lambda x: (x[1], -x[0]))
    partial_match_score = sum([n.duration*n.beatStrength for n in pairs if n.diff == most_prevalent_delta[0]])/bar_duration
    transposition_amount = abs(most_prevalent_delta[0])
    return full_match_score, partial_match_score, transposition_amount


def score_new_rules(bar, prev_notes):
    bar_duration = max(sum([n.duration for n in bar]), sum([n.duration for n in prev_notes]))
    i, j = 0, 0
    pairs = []
    index_b = 0
    index_p = 0
    # Iterate over both lists in single loop. (Offsets are ordered.)
    while i < len(bar) and j < len(prev_notes):
        if bar[i].offset == prev_notes[j].offset:
            if bar[i].noteIndex == index_b and prev_notes[j].noteIndex == index_p:
                # If the offset values match, subtract note values and store in the result
                note_diff = bar[i].noteValue - prev_notes[j].noteValue
                pairs.append(dotdict({'diff': note_diff, 'duration': min(bar[i].duration, prev_notes[j].duration),
                                      'beatStrength': bar[i].beatStrength, 'index': index_b}))
                i += 1
                j += 1
                index_b += 1
                index_p += 1
            else:
                break
        elif bar[i].offset < prev_notes[j].offset:
            # Increment i if bar has a smaller offset
            i += 1
        else:
            # Increment j if prev_notes has a smaller offset
            j += 1
    variant_match_type_scores = []
    non_t_contig_score = largest_zero_diff_consecutive_duration_sum(pairs) / bar_duration
    if non_t_contig_score > 0.5:
        full_match_score = non_t_contig_score
        non_t_contig_variant_score = 0.0
    elif math.isclose(non_t_contig_score, 0.5):
        full_match_score = 0.0
        non_t_contig_variant_score = non_t_contig_score
    else:
        full_match_score = 0.0
        non_t_contig_variant_score = 0.0
    variant_match_type_scores.append(non_t_contig_variant_score)

    non_t_non_contig_score = sum([n.duration for n in pairs if n.diff == 0])/bar_duration
    if non_t_non_contig_score > 0.5:
        non_t_non_contig_variant_score = non_t_non_contig_score
    else:
        non_t_non_contig_variant_score = 0.0
    variant_match_type_scores.append(non_t_non_contig_variant_score)

    transposed_match_duration, diff_value = largest_consecutive_duration_sum(pairs)
    t_contig_score = transposed_match_duration / bar_duration

    if t_contig_score > 0.5:
        non_t_contig_variant_score = t_contig_score
        transposition_amount = abs(diff_value)
    else:
        non_t_contig_variant_score = 0.0
        transposition_amount = float('inf')
    variant_match_type_scores.append(non_t_contig_variant_score)

    # Choose the best variant match score type.
    partial_match_score = max(enumerate(variant_match_type_scores), key=lambda x: (x[1], -x[0]))[1]
    return full_match_score, partial_match_score, transposition_amount
