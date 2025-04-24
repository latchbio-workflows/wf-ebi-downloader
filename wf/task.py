import csv
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List

from latch.resources.tasks import small_task
from latch.types.directory import LatchOutputDir
from latch.types.file import LatchFile

sys.stdout.reconfigure(line_buffering=True)


@dataclass
class Sample:
    """Represents a sample with associated data and processing parameters."""

    identifier: str
    forward_read: str
    reverse_read: str
    outdir: LatchOutputDir


@small_task
def preprocess_task(
    id: str,
    output_directory: LatchOutputDir,
) -> List[Sample]:
    try:
        result = subprocess.run(
            ["/root/wf/query_fastqs.sh", id], check=True, text=True, capture_output=True
        )
        print("Script output:\n", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error occurred:\n", e.stderr)

    """Preprocesses input data and creates a list of Sample objects."""
    sample_sets = []

    with open("fastqs.tsv", "r") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            sample_id, fwd_url, rev_url = row
            if fwd_url and rev_url:
                sample_sets.append(
                    Sample(
                        identifier=sample_id,
                        forward_read=fwd_url,
                        reverse_read=rev_url,
                        outdir=output_directory.remote_path,
                    )
                )

    print(sample_sets)

    return sample_sets


@small_task
def download_task(sample: Sample) -> LatchOutputDir:
    output_path = Path("/root/fastqs/")
    Path(output_path).mkdir(parents=True, exist_ok=True)

    try:
        print(f"Downloading forward read for {sample.identifier}...")
        subprocess.run(
            ["wget", "-nc", "-P", output_path, sample.forward_read], check=True
        )

        print(f"Downloading reverse read for {sample.identifier}...")
        subprocess.run(
            ["wget", "-nc", "-P", output_path, sample.reverse_read], check=True
        )

        print(f"Finished downloading {sample.identifier}")
    except subprocess.CalledProcessError as e:
        print(f"Download failed for {sample.identifier}: {e}")

    return LatchOutputDir(str(output_path), f"{sample.outdir.remote_path}/")
