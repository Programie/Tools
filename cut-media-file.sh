#! /bin/bash

input_file="$1"
output_file="$2"
start_time="$3"
end_time="$4"

if [[ -z ${start_time} ]] || [[ -z ${end_time} ]]; then
    echo "Usage: $0 <input file> <output file> <start time> <end time>"
    exit 1
fi

ffmpeg -nostdin -i "${input_file}" -ss "${start_time}" -to "${end_time}" -c copy "${output_file}"