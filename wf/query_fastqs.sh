#!/bin/bash

# Usage: ./query_fastqs.sh PRJEB24645

PROJECT_ID=$1

if [ -z "$PROJECT_ID" ]; then
  echo "Usage: $0 <ENA_project_id>"
  exit 1
fi

# Fetch and process the TSV
curl -s "https://www.ebi.ac.uk/ena/portal/api/filereport?accession=${PROJECT_ID}&result=read_run&fields=run_accession,fastq_ftp&format=tsv" \
  | tail -n +2 \
  | awk -F '\t' '{
      split($2, files, ";")
      forward = (length(files) >= 1 ? files[1] : "")
      reverse = (length(files) >= 2 ? files[2] : "")
      print $1 "\t" forward "\t" reverse
  }' > fastqs.tsv

ROW_COUNT=$(wc -l < fastqs.tsv)

if [ "$ROW_COUNT" -eq 0 ]; then
  echo "Error: No FASTQ entries found for project ${PROJECT_ID}."
  exit 1
fi

echo "Generated fastqs.tsv with ${ROW_COUNT} entries for project ${PROJECT_ID}"
