from typing import List

from latch import map_task
from latch.resources.workflow import workflow
from latch.types.directory import LatchOutputDir
from latch.types.file import LatchFile
from latch.types.metadata import LatchAuthor, LatchMetadata, LatchParameter

from wf.task import download_task, preprocess_task

metadata = LatchMetadata(
    display_name="EBI FASTQ Downloader",
    author=LatchAuthor(
        name="Zhen",
    ),
    parameters={
        "id": LatchParameter(
            display_name="EBI BioProject ID",
            batch_table_column=True,
        ),
        "output_directory": LatchParameter(
            display_name="Output Directory",
            batch_table_column=True,
        ),
    },
)


@workflow(metadata)
def ebi_download_workflow(
    id: str, output_directory: LatchOutputDir
) -> List[LatchOutputDir]:
    # Step 1: Generate list of EBI FTP link to download given EBI BioProject ID
    samples = preprocess_task(
        id=id,
        output_directory=output_directory,
    )

    # Step 2: Quantify samples in parallel
    return map_task(download_task)(sample=samples)
