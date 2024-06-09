
#!/bin/bash

# File to save the merged result
output_file="Xavier-rawdata-20240608.csv"

# Create the output file and add the header from the first file
head -n 1 airbnb_results_2024-07-01_2024-07-04_Kelowna.csv > "$output_file"

# Append the content of each file excluding the header
for file in *2024*.csv; do
    tail -n +2 "$file" >> "$output_file"
done
