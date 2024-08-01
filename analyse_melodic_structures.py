from extract_notes import extract_tune_notes
from structure_analysis import analyse_tune
from process_abc import extract_abc_info, clean_abc, read_abc_file
from music21 import converter
from tqdm import tqdm
import pprint
import argparse


def process_tune(abc_content, SCORING_METHOD):
    # Remove errors and contents that music21 cannot parse.
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
    return analyse_tune(tune_notes, tune_name, tune_number, part_labels, beat_strengths, SCORING_METHOD)


# Function to extract a list of tunes from the input file, initialise the output file, and run a loop to analyse the
# corpus of tunes.
def main(in_file, out_file, SCORING_METHOD):
    # open input file & read contents.
    corpus = read_abc_file(in_file)
    outputfile = open(out_file, "w")
    outputfile.writelines("Tune,Title,Part,Structure" + "\n")
    outputfile.close()
    outputfile = open(out_file, "a")
    # Loop over each tune.
    for tune in tqdm(corpus, desc='Analysing Melodic Structures.'):
    #for tune in corpus:
        outputfile.writelines(process_tune(tune, SCORING_METHOD))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Input file", default='/home/roro/Documents/RA2/datasets/ABC/song_names_single_line/ONeills1001.abc')
    parser.add_argument("-o", "--output", help="Output file", default='melodic_structures.csv')
    parser.add_argument("-m", "--method", help="Method", type=int, default=0)
    args = parser.parse_args()
    in_file = args.input
    out_file = args.output
    SCORING_METHOD = args.method
    main(in_file, out_file, SCORING_METHOD)
