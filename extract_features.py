# import required classes from local FoNN module
from feature_sequence_extraction_tools import Corpus

# local path to MTC-ANN corpus
corpus_path = '/home/roro/Documents/RA2/datasets/MIDI'



# Step 2. Process entire corpus
# initialize corpus object
corpus = Corpus(corpus_path)
# Corpus.setup_corpus_iteratively() populates corpus tune titles, extracts primary feature sequence data and root for all music score files in input dir.
corpus.setup_corpus_iteratively()
corpus.strip_anacrusis()
# Print sample output:
print(f"Title: {corpus.tunes[0].title}")
print("Note-level feature sequence output")
print(corpus.tunes[0].feat_seq.head())
print(f"Corpus contains {len(corpus.tunes)} tunes.")


# Step 3. Extract secondary feature sequence data
# Note: calls below can be commented-out if a full set of input features is not necessary/desired.

# Add relative chromatic & diatonic pitch:
corpus.extract_relative_chromatic_pitch_seqs()
corpus.extract_relative_diatonic_pitch_seqs()
# Add chromatic & diatonic scale degrees:
corpus.extract_chromatic_scale_degree_seqs()
corpus.extract_diatonic_scale_degree_seqs()
# Add chromatic & diatonic intervals:
corpus.extract_chromatic_intervals()
corpus.extract_diatonic_intervals()
print(corpus.tunes[0].title)
# Print sample output:
print(f"Title: {corpus.tunes[0].title}")
print("Note-level feature sequence output")
print(corpus.tunes[0].feat_seq.head())
print(f"Corpus contains {len(corpus.tunes)} tunes.")





# Step 4. Filter sequences to create 'accent-level' representation
# This step is not applied to the MTC-ANN corpus as it was conceived specifically for the study of Irish dance tune melodies.
# The shorter song melodies in MTC-ANN are not suited to analysis at this higher level of granularity.

 # To apply accent-level filtering, please call Corpus.filter_feat_seq() method as instructed below:
 # For corpora originating in ABC Notation format: Corpus.filter_feat_seq_accents(thresh=80, by='velocity')
 # For all other corpora: Corpus.filter_feat_seq(self, thresh=0.5, by='beat_strength')



# Step 5. Add Parsons code sequence data
# Note: If accent-level sequence filtering is applied, Parsons code must be calculated after filtration to ensure accuracy of the accent-level output sequences.

# Add Parsons code (simple contour)
corpus.extract_parsons_codes()
print(corpus.tunes[0].title)
# Print sample output:
print(f"Title: {corpus.tunes[0].title}")
print("Note-level feature sequence output")
print(corpus.tunes[0].feat_seq.head())
print(f"Corpus contains {len(corpus.tunes)} tunes.")


# Step 6: Apply duration-weighting to feature sequence data
# Step 1: select features for inclusion

# select all available features for input into duration-weighting process
features = [col for col in corpus.tunes[0].feat_seq.columns]
# the 'duration' feature is no longer of use after duration-weighting and can be removed
features.remove('duration')
# print names of all remaining features for inclusion in duration-weighting process
print("Input features for duration weighting:")
for feat in features:
    print(feat)

# Note: to apply duration-weighting to a custom subset of features, please select from the list of feature names printe



# Step 7. Write output data to file
# Run duration-weighting
corpus.extract_duration_weighted_feat_seqs(features=features)
# Print sample output:
print(f"Title: {corpus.tunes[0].title}")
print("Note-level feature sequence output")
print(corpus.tunes[0].feat_seq.head())
print(f"Duration-weighted corpus contains {len(corpus.tunes)} tunes.")


# Step 8. Output
# set outpath
corpus.out_path = "/home/roro/Documents/RA2/code/melodic_struc_analysis/feature_CSVs/"
# write output to csv
corpus.save_feat_seq_data_to_csv()
