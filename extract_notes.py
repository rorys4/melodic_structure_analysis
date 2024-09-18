from music21 import stream, note, meter

NOTE_DURATION_CUTOFF = 0.0 # Exclude grace notes.
# NOTE_DURATION_CUTOFF = 1.0 # Exclude notes shorter than an eighth note.

# Handy class to allow dot notation access to dict keys.
class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


# Function: generate a list containing each note in a bar represented
# as tuples of diatonic note pitches, offsets, beat strengths and durations.
def get_bar_notes(measure):
    notes_in_measure = measure.notes
    notes = []
    for n in notes_in_measure:
        if isinstance(n, note.Note):
            offset = n._activeSiteStoredOffset * 2 # Familiar with working in eighth notes.
            duration = n.duration.quarterLength * 2 # Familiar with working in eighth notes.
            noteValue = n.pitch.diatonicNoteNum
            beatStrength = n.beatStrength
            if duration > NOTE_DURATION_CUTOFF:
                notes.append(dotdict({'offset': offset, 'noteValue': noteValue, 'beatStrength': beatStrength, 'duration': duration}))
    return notes


# Function to extract and display MIDI numbers of notes in each bar
def extract_tune_notes(score):
    measures = score.parts[0].getElementsByClass(stream.Measure)
    num, den = score.recurse().getElementsByClass(meter.TimeSignature)[0].ratioString.split('/')
    eighth_notes_per_bar = float(num) * 8 / float(den)
    notes = []
    measure_nums = []
    bar_count = 0
    skip_next = False
    for i in range(len(measures)):
        # If pickup bar has been already concatenated onto the previous bar, skip it.
        if skip_next:
            skip_next = False
            continue
        measure = measures[i]
        bar_notes = get_bar_notes(measure)
        bar_duration = sum([n.duration for n in bar_notes])
        # Remove loose pick-up bar if present.
        if bar_duration < 0.5*eighth_notes_per_bar:
            continue
        # Check if this bar is missing a note.
        if bar_duration < eighth_notes_per_bar and i > 0 and i + 1 < len(measures):
            # Get the next bar's notes.
            next_bar_notes = get_bar_notes(measures[i + 1])
            # Adjust pickup bar offset values.
            for n in next_bar_notes:
                n.offset = n.offset + bar_duration
            # Combine with next bar in case it's a pick-up bar.
            combined_bar_notes = bar_notes + next_bar_notes
            # Check if new bar length is smaller or equal to a full bar length, and revert to two separate bars if not.
            if sum([n.duration for n in combined_bar_notes]) <= eighth_notes_per_bar:
                full_bar_notes = combined_bar_notes
                skip_next = True
            else:
                full_bar_notes = bar_notes
        # Extend final note of tune if the bar is short.
        elif bar_duration == eighth_notes_per_bar - 1 and i == len(measures) - 1:
            bar_notes[len(bar_notes)-1].duration = bar_notes[len(bar_notes)-1].duration + 1
            full_bar_notes = bar_notes
        else:
            full_bar_notes = bar_notes
        part_count = bar_count // 8
        if bar_count % 8 == 0:
            notes.append([])
            measure_nums.append([])
        notes[part_count].append(full_bar_notes)
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
    return notes, part_labels
