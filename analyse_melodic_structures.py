from extract_notes import extract_tune_notes
from structure_analysis import analyse_tune
from process_abc import extract_abc_info, clean_abc, read_abc_file
from music21 import converter
from tqdm import tqdm
import pprint
import argparse
import concurrent.futures


def process_tune(abc_content, SCORING_METHOD):
    # Remove errors and contents that music21 cannot parse.
    abc_content = clean_abc(abc_content)
    # Parse the ABC content
    abc_score = converter.parse(abc_content, format='abc')
    # Expand repeats
    expanded_score = abc_score.expandRepeats()
    tune_name, tune_number = extract_abc_info(abc_content)
    # Generate a list of lists containing the notes in each bar.
    tune_notes, part_labels = extract_tune_notes(expanded_score)
    #print(tune_number + ": " + tune_name)
    #pprint.pprint([[[note['beatStrength'] for note in bar] for bar in part] for part in tune_notes])
    #if tune_number == '9':
    #    breakpoint()
    # Generate Doherty structure pattern strings.
    return analyse_tune(tune_notes, tune_name, tune_number, part_labels, SCORING_METHOD)


# Function to extract a list of tunes from the input file, initialise the output file, and run a loop to analyse the
# corpus of tunes.
def main(in_file, out_file, SCORING_METHOD):
    # Open input file & read contents
    corpus = read_abc_file(in_file)
    outputfile = open(out_file, "w")
    outputfile.writelines("Tune,Title,Part,Structure" + "\n")
    outputfile.close()

    # Use ProcessPoolExecutor to parallelize the tune processing
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Submit tasks to the executor for parallel processing, storing the index with the future
        futures = {executor.submit(process_tune, tune, SCORING_METHOD): i for i, tune in enumerate(corpus)}

        # Collect results in the correct order using the indices
        results = [None] * len(corpus)
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(corpus), desc='Analysing Melodic Structures.'):
            index = futures[future]
            results[index] = future.result()

    # Write results to output file in the correct order
    with open(out_file, "a") as outputfile:
        for result in results:
            outputfile.write("".join(result)) # Join list elements into a single string


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
