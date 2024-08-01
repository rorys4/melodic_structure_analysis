from music21 import stream, note, meter

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
                    # Changed to diatonic pitch classes.
                    #midi_numbers.append(n.pitch.midi)
                    midi_numbers.append(n.pitch.diatonicNoteNum)
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
