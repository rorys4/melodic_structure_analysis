import collections

# Switches
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
        best_full_match_score = 5 / 6
        best_partial_match_score = 3 / 6
    if SCORING_METHOD == BEAT_STRENGTH_SUM_2o0_1o5:
        best_full_match_score = 2.0
        best_partial_match_score = 1.5
    if SCORING_METHOD == BEAT_STRENGTH_SUM_1o75_1o25:
        best_full_match_score = 1.75
        best_partial_match_score = 1.25
    if SCORING_METHOD == BEAT_STRENGTH_SUM_1o75_1o5:
        best_full_match_score = 1.75
        best_partial_match_score = 1.5
    if SCORING_METHOD == BEAT_STRENGTH_SUM_1o5_1o25:
        best_full_match_score = 1.5
        best_partial_match_score = 1.25
    if SCORING_METHOD == BEAT_STRENGTH_SUM_2o25_1o5:
        best_full_match_score = 2.25
        best_partial_match_score = 1.5
    if SCORING_METHOD == LCP:
        best_full_match_score = 5 / 6
        best_partial_match_score = 3 / 6
    if SCORING_METHOD == CONTIGUOUS_NOTES:
        best_full_match_score = 5 / 6
        best_partial_match_score = 3 / 6
    return best_full_match_score, best_partial_match_score


# Compute the match scores of a pair of bars.
def bar_match_scores(bar, prev_notes, beat_strengths, SCORING_METHOD):
    if SCORING_METHOD == BASIC:
        return score_basic(bar, prev_notes, beat_strengths)
    if SCORING_METHOD == REQUIRE_1st_NOTE:
        return score_require_first_note(bar, prev_notes, beat_strengths)
    if SCORING_METHOD == REQUIRE_1st_AND_4th_NOTES:
        return score_require_first_and_fourth_notes(bar, prev_notes, beat_strengths)
    if SCORING_METHOD == BEAT_STRENGTH_SUM_2o0_1o25:
        return score_beat_strength_sum(bar, prev_notes, beat_strengths)
    if SCORING_METHOD == BEAT_STRENGTH_SUM_2o0_1o5:
        return score_beat_strength_sum(bar, prev_notes, beat_strengths)
    if SCORING_METHOD == BEAT_STRENGTH_SUM_1o75_1o25:
        return score_beat_strength_sum(bar, prev_notes, beat_strengths)
    if SCORING_METHOD == BEAT_STRENGTH_SUM_1o75_1o5:
        return score_beat_strength_sum(bar, prev_notes, beat_strengths)
    if SCORING_METHOD == BEAT_STRENGTH_SUM_1o5_1o25:
        return score_beat_strength_sum(bar, prev_notes, beat_strengths)
    if SCORING_METHOD == BEAT_STRENGTH_SUM_2o25_1o5:
        return score_beat_strength_sum(bar, prev_notes, beat_strengths)
    if SCORING_METHOD == LCP:
        return score_basic(bar, prev_notes, beat_strengths)
    if SCORING_METHOD == CONTIGUOUS_NOTES:
        return score_basic(bar, prev_notes, beat_strengths)


def score_basic(bar, prev_notes, beat_strengths):
    diff = [xi - yi for xi, yi in zip(bar, prev_notes)]
    # For full match (without transposition)
    num_common = diff.count(0) / max(len(bar), len(prev_notes))
    # For partial match (transposition allowed)
    most_common_delta = collections.Counter(diff).most_common(1)[0]
    comparison = most_common_delta[1] / max(len(bar), len(prev_notes))
    full_match_score = num_common
    partial_match_score = comparison / (abs(most_common_delta[0]) + 1)
    return full_match_score, partial_match_score

def score_require_first_note(bar, prev_notes, beat_strengths):
    diff = [xi - yi for xi, yi in zip(bar, prev_notes)]
    # For full match (without transposition)
    num_common = diff.count(0) / max(len(bar), len(prev_notes))
    # For partial match (transposition allowed)
    most_common_delta = collections.Counter(diff).most_common(1)[0]
    comparison = most_common_delta[1] / max(len(bar), len(prev_notes))
    # Require that the first note be a match.
    if diff[0] != most_common_delta[0]:
        return 0, 0
    full_match_score = num_common
    partial_match_score = comparison / (abs(most_common_delta[0]) + 1)
    return full_match_score, partial_match_score


def score_require_first_and_fourth_notes(bar, prev_notes, beat_strengths):
    diff = [xi - yi for xi, yi in zip(bar, prev_notes)]
    # For full match (without transposition)
    num_common = diff.count(0) / max(len(bar), len(prev_notes))
    # For partial match (transposition allowed)
    most_common_delta = collections.Counter(diff).most_common(1)[0]
    comparison = most_common_delta[1] / max(len(bar), len(prev_notes))
    # Require that the first note be a match.
    if len(diff) > 3:
        if diff[0] != most_common_delta[0] or diff[3] != most_common_delta[0]:
            return 0, 0
    else:
        if diff[0] != most_common_delta[0]:
            return 0, 0
    full_match_score = num_common
    partial_match_score = comparison / (abs(most_common_delta[0]) + 1)
    return full_match_score, partial_match_score


def score_beat_strength_sum(bar, prev_notes, beat_strengths):
    diff = [xi - yi for xi, yi in zip(bar, prev_notes)]
    matched_notes = [1 if x == 0 else 0 for x in diff]

    most_common_delta = collections.Counter(diff).most_common(1)[0]
    transposed_matched_notes = [1 if x == most_common_delta[1] else 0 for x in diff]

    full_match_score = sum([x * y for x, y in zip(beat_strengths, matched_notes)])
    partial_match_score = sum([x * y for x, y in zip(beat_strengths, transposed_matched_notes)])
    return full_match_score, partial_match_score
