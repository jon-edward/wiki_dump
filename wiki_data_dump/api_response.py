"""Holds data classes that represent varying levels of the data dump hierarchy."""

from typing import Optional, Union, List
import copy
from dataclasses import dataclass
import re


@dataclass
class File:
    """
    Holds file size, sha1 sum, and url for downloading.
    Also contains md5, though this is unused.
    """

    size: int
    url: str
    md5: str = None
    sha1: str = None


@dataclass
class Job:
    """Holds job status, update time,
    and file mapping from name to File."""

    status: str
    updated: str
    files: Optional[dict] = None

    def __post_init__(self):
        if not self.files:
            return

        to_delete = set()

        for name, file in self.files.items():
            if file:
                self.files[name] = File(**copy.deepcopy(file))
            else:
                to_delete.add(name)

        for delete_member in to_delete:
            del self.files[delete_member]

    def get_file(self, key: Union[str, re.Pattern]) -> File:
        """Query file names by the first name that contains a match
        for a regex Pattern or get the exact matching file name."""

        if isinstance(key, str):
            return self.files[key]
        try:
            name = next(_k for _k in self.files.keys() if key.search(_k))
            return self.files[name]
        except StopIteration:
            # pylint: disable=W0707
            raise KeyError(f"{key}")
            # pylint: enable=W0707

    def get_files(self, re_key: re.Pattern) -> List[File]:
        """Queries file names to find all files that contain a match for the supplied re_key."""

        return [self.files[_k] for _k in self.files.keys() if re_key.search(_k)]


@dataclass
class Wiki:
    """Contains a mapping from job name to Job, and a version string."""

    jobs: dict
    version: str

    def __post_init__(self):
        for name, job in self.jobs.items():
            if not isinstance(job, Job):
                self.jobs[name] = Job(**copy.deepcopy(job))
