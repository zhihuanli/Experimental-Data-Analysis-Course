#!/usr/bin/env bash
set -u
if [ "$#" -ne 5 ]; then
    echo "Usage: bash run_batch.sh first last input_dir output_dir program" >&2
    exit 1
fi
first=$1; last=$2; input_dir=$3; output_dir=$4; program=$5
if ! [[ $first =~ ^[0-9]+$ && $last =~ ^[0-9]+$ ]] || (( first > last )); then
    echo "Invalid run range" >&2
    exit 1
fi
mkdir -p "$output_dir"
failed=0
for ((run=first; run<=last; run++)); do
    printf -v input_file '%s/f8ppac%03d.root' "$input_dir" "$run"
    printf -v output_file '%s/out%03d.root' "$output_dir" "$run"
    if [ ! -f "$input_file" ] || [ -e "$output_file" ]; then
        echo "Skip run $run: missing input or existing output" >&2
        failed=1
        continue
    fi
    if "$program" "$run" "$input_dir" "$output_dir" >"$output_dir/run$run.log" 2>&1; then
        echo "Run $run completed"
    else
        echo "Run $run failed; see $output_dir/run$run.log" >&2
        failed=1
    fi
done
exit "$failed"
