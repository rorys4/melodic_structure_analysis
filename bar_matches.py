import collections
import math
from collections import defaultdict


# Handy class to allow dot notation access to dict keys.
class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

#BEAT_STRENGTH_COEFF = 5

EXCLUDE_SHORT_NOTES = False

# Method Switches
BASIC = 0
REQUIRE_1st_NOTE = 1
REQUIRE_1st_AND_4th_NOTES = 2
BEAT_STRENGTH_SUM_2o0_1o25 = 3
BEAT_STRENGTH_SUM_2o0_1o5 = 4
BEAT_STRENGTH_SUM_1o75_1o25 = 5
BEAT_STRENGTH_SUM_1o75_1o5 = 6
BEAT_STRENGTH_SUM_1o5_1o25 = 7
BEAT_STRENGTH_SUM_2o25_1o5 = 8
LCP = 9
CONTIGUOUS_NOTES = 10
DIV_BY_TRSPS_AMT = 11
VARIANT_THRESH_4 = 12
CUSTOM_BEAT_STRENGTH = 13
HARD_CODED_BEAT_STRENGTH_LINEAR = 14
HARD_CODED_BEAT_STRENGTH_GEOMETRIC = 15
NEW_RULES = 16


# Select the score thresholds for the given bar similarity scoring method.
def score_thresholds(SCORING_METHOD):
    if SCORING_METHOD == BASIC:
        best_full_match_score = 5 / 6
        best_partial_match_score = 3 / 6
    if SCORING_METHOD == REQUIRE_1st_NOTE:
        best_full_match_score = 5 / 6
        best_partial_match_score = 3 / 6
    if SCORING_METHOD == REQUIRE_1st_AND_4th_NOTES:
        best_full_match_score = 5 / 6
        best_partial_match_score = 3 / 6
    if SCORING_METHOD == BEAT_STRENGTH_SUM_2o0_1o25:
        best_full_match_score = 2.0 / 6
        best_partial_match_score = 1.25 / 6
    if SCORING_METHOD == BEAT_STRENGTH_SUM_2o0_1o5:
        best_full_match_score = 2.0 / 6
        best_partial_match_score = 1.5 / 6
    if SCORING_METHOD == BEAT_STRENGTH_SUM_1o75_1o25:
        best_full_match_score = 1.75 / 6
        best_partial_match_score = 1.25 / 6
    if SCORING_METHOD == BEAT_STRENGTH_SUM_1o75_1o5:
        best_full_match_score = 1.75 / 6
        best_partial_match_score = 1.5 / 6
    if SCORING_METHOD == BEAT_STRENGTH_SUM_1o5_1o25:
        best_full_match_score = 1.5 / 6
        best_partial_match_score = 1.25 / 6
    if SCORING_METHOD == BEAT_STRENGTH_SUM_2o25_1o5:
        best_full_match_score = 2.25 / 6
        best_partial_match_score = 1.5 / 6
    if SCORING_METHOD == LCP:
        best_full_match_score = 5 / 6
        best_partial_match_score = 3 / 6
    if SCORING_METHOD == CONTIGUOUS_NOTES:
        best_full_match_score = 5 / 6
        best_partial_match_score = 3 / 6
    if SCORING_METHOD == DIV_BY_TRSPS_AMT:
        best_full_match_score = 5 / 6
        best_partial_match_score = 3 / 6
    if SCORING_METHOD == VARIANT_THRESH_4:
        best_full_match_score = 5 / 6
        best_partial_match_score = 4 / 6
    if SCORING_METHOD == CUSTOM_BEAT_STRENGTH:
        best_full_match_score = 5 / 6
        best_partial_match_score = 3 / 6
    if SCORING_METHOD == HARD_CODED_BEAT_STRENGTH_LINEAR:
        best_full_match_score = 5 / 6
        best_partial_match_score = 3 / 6
    if SCORING_METHOD == HARD_CODED_BEAT_STRENGTH_GEOMETRIC:
        best_full_match_score = 5 / 6
        best_partial_match_score = 3 / 6
    if SCORING_METHOD == NEW_RULES:
        best_full_match_score = 0.5
        best_partial_match_score = 0.5
    return best_full_match_score, best_partial_match_score


# Compute the match scores of a pair of bars.
def bar_match_scores(bar, prev_notes, eighth_notes_per_bar, SCORING_METHOD, BEAT_STRENGTH_COEFF):
    if SCORING_METHOD == BASIC:
        return score_basic(bar, prev_notes)
    if SCORING_METHOD == REQUIRE_1st_NOTE:
        return score_require_first_note(bar, prev_notes)
    if SCORING_METHOD == REQUIRE_1st_AND_4th_NOTES:
        return score_require_first_and_fourth_notes(bar, prev_notes)
    if SCORING_METHOD == BEAT_STRENGTH_SUM_2o0_1o25:
        return score_beat_strength_sum(bar, prev_notes)
    if SCORING_METHOD == BEAT_STRENGTH_SUM_2o0_1o5:
        return score_beat_strength_sum(bar, prev_notes)
    if SCORING_METHOD == BEAT_STRENGTH_SUM_1o75_1o25:
        return score_beat_strength_sum(bar, prev_notes)
    if SCORING_METHOD == BEAT_STRENGTH_SUM_1o75_1o5:
        return score_beat_strength_sum(bar, prev_notes)
    if SCORING_METHOD == BEAT_STRENGTH_SUM_1o5_1o25:
        return score_beat_strength_sum(bar, prev_notes)
    if SCORING_METHOD == BEAT_STRENGTH_SUM_2o25_1o5:
        return score_beat_strength_sum(bar, prev_notes)
    if SCORING_METHOD == LCP:
        return score_longest_common_prefix(bar, prev_notes)
    if SCORING_METHOD == CONTIGUOUS_NOTES:
        return score_longest_contiguous_match(bar, prev_notes)
    if SCORING_METHOD == DIV_BY_TRSPS_AMT:
        return score_div_by_transposition_amount(bar, prev_notes)
    if SCORING_METHOD == VARIANT_THRESH_4:
        return score_basic(bar, prev_notes)
    if SCORING_METHOD == CUSTOM_BEAT_STRENGTH:
        return score_beat_strength_sum2(bar, prev_notes, BEAT_STRENGTH_COEFF)
    if SCORING_METHOD == HARD_CODED_BEAT_STRENGTH_LINEAR:
        return score_beat_strength_sum3(bar, prev_notes, eighth_notes_per_bar)
    if SCORING_METHOD == HARD_CODED_BEAT_STRENGTH_GEOMETRIC:
        return score_beat_strength_sum4(bar, prev_notes, eighth_notes_per_bar, BEAT_STRENGTH_COEFF)
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
        diff_durations[i['diff']] += i['duration']
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
        diff_durations[i['diff']] += i['duration']
    most_prevalent_delta = max(diff_durations.items(), key=lambda x: (x[1], -x[0]))

    if pairs[0].diff != most_prevalent_delta[0] or pairs[0].offset != 0 or middle_diff != most_prevalent_delta[0]:
        partial_match_score = 0
        transposition_amount = 0
    else:
        partial_match_score = most_prevalent_delta[1] / bar_duration
        transposition_amount = abs(most_prevalent_delta[0])

    return full_match_score, partial_match_score, transposition_amount


def score_beat_strength_sum(bar, prev_notes):
    bar_duration = max(sum([n.duration for n in bar]), sum([n.duration for n in prev_notes]))
    i, j = 0, 0
    pairs = []
    # Iterate over both lists in single loop. (Offsets are ordered.)
    while i < len(bar) and j < len(prev_notes):
        if bar[i].offset == prev_notes[j].offset:
            # If the offset values match, subtract note values and store in the result
            note_diff = bar[i].noteValue - prev_notes[j].noteValue
            pairs.append(dotdict({'diff': note_diff, 'duration': min(bar[i].duration, prev_notes[j].duration), 'beatStrength': bar[i].beatStrength}))
            i += 1
            j += 1
        elif bar[i]['offset'] < prev_notes[j]['offset']:
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
        diff_durations[i['diff']] += i['duration']
    most_prevalent_delta = max(diff_durations.items(), key=lambda x: (x[1], -x[0]))
    partial_match_score = sum([n.duration*n.beatStrength for n in pairs if n.diff == most_prevalent_delta[0]])/bar_duration
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
        elif bar[i]['offset'] < prev_notes[j]['offset']:
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


def score_longest_contiguous_match(bar, prev_notes):
    diff = [xi - yi for xi, yi in zip(bar, prev_notes)]
    full_match_score = longest_zero_sequence(diff) / max(len(bar), len(prev_notes))
    match_length, match_digit = longest_contiguous_same_elements(diff)
    partial_match_score = match_length / max(len(bar), len(prev_notes))
    transposition_amount = abs(match_digit)
    return full_match_score, partial_match_score, transposition_amount


def score_div_by_transposition_amount(bar, prev_notes):
    diff = [xi - yi for xi, yi in zip(bar, prev_notes)]
    # For full match (without transposition)
    proportion_in_common = diff.count(0) / max(len(bar), len(prev_notes))
    full_match_score = proportion_in_common
    # For partial match (transposition allowed)
    most_common_delta = collections.Counter(diff).most_common(1)[0]
    partial_match_comparison = most_common_delta[1] / max(len(bar), len(prev_notes))
    partial_match_score = partial_match_comparison / (abs(most_common_delta[0]) + 1)
    transposition_amount = abs(most_common_delta[0])
    return full_match_score, partial_match_score, transposition_amount


def score_beat_strength_sum2(bar, prev_notes, BEAT_STRENGTH_COEFF):
    bar_duration = max(sum([n.duration for n in bar]), sum([n.duration for n in prev_notes]))
    i, j = 0, 0
    pairs = []
    # Iterate over both lists in single loop. (Offsets are ordered.)
    while i < len(bar) and j < len(prev_notes):
        if bar[i].offset == prev_notes[j].offset:
            # If the offset values match, subtract note values and store in the result
            note_diff = bar[i].noteValue - prev_notes[j].noteValue
            bs_sum = sum([pow(BEAT_STRENGTH_COEFF, math.log2(n.beatStrength))*n.duration for n in bar])/bar_duration
            custom_beat_strength = pow(BEAT_STRENGTH_COEFF, math.log2(bar[i].beatStrength)) / bs_sum
            pairs.append(dotdict({'diff': note_diff, 'duration': min(bar[i].duration, prev_notes[j].duration), 'beatStrength': custom_beat_strength}))
            i += 1
            j += 1
        elif bar[i]['offset'] < prev_notes[j]['offset']:
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
        diff_durations[i['diff']] += i['duration']
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
    if beat_weightings == None:
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
        diff_durations[i['diff']] += i['duration']
    most_prevalent_delta = max(diff_durations.items(), key=lambda x: (x[1], -x[0]))
    partial_match_score = sum([n.duration*n.beatStrength for n in pairs if n.diff == most_prevalent_delta[0]])/bar_duration
    transposition_amount = abs(most_prevalent_delta[0])
    return full_match_score, partial_match_score, transposition_amount


def score_beat_strength_sum4(bar, prev_notes, eighth_notes_per_bar, BEAT_STRENGTH_COEFF):
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
    bs_sum = sum([pow(BEAT_STRENGTH_COEFF, beat_weightings[math.floor(n.offset)]) * n.duration for n in bar]) / bar_duration
    i, j = 0, 0
    pairs = []
    # Iterate over both lists in single loop. (Offsets are ordered.)
    while i < len(bar) and j < len(prev_notes):
        if bar[i].offset == prev_notes[j].offset:
            # If the offset values match, subtract note values and store in the result
            note_diff = bar[i].noteValue - prev_notes[j].noteValue
            custom_beat_strength = pow(BEAT_STRENGTH_COEFF, beat_weightings[math.floor(bar[i].offset)]) / bs_sum
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
        diff_durations[i['diff']] += i['duration']
    most_prevalent_delta = max(diff_durations.items(), key=lambda x: (x[1], -x[0]))
    partial_match_score = sum([n.duration*n.beatStrength for n in pairs if n.diff == most_prevalent_delta[0]])/bar_duration
    transposition_amount = abs(most_prevalent_delta[0])
    return full_match_score, partial_match_score, transposition_amount


def score_new_rules(bar, prev_notes):
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

