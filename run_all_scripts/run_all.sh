#!/bin/bash

# Make a directory to store the results in if it doesn't already exist.
mkdir -p comparison
# Declare an array to store the results
declare -a results

# Iterate through values of x from 0 to 10
#for x in {0..12}
for x in 0 1 2 3 4 5 6 7 8 9 12 14
do
    # Construct the output filename
    output_filename="output${x}.csv"
    
    # Run the Python program with the current value of x and the constructed output filename
    python3 analyse_melodic_structures.py -m $x -o comparison/$output_filename
    
    # Capture the output of the second Python program
    result=$(python3 ../compare_results/compare_with_doherty.py -i comparison/$output_filename)
    
    # Store the value pair in the results array
    results+=("$x $result")
done

# Print the table header
printf "%-10s %-10s\n" "x" "Result"

# Print each value pair
for entry in "${results[@]}"
do
    printf "%-10s %-10s\n" $entry
done

