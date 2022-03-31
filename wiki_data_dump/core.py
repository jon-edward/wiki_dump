
import copy
import re
import threading
import urllib.parse
import tempfile
from typing import Union, List, Tuple, overload, Dict

import json
import tqdm as tqdm
from requests import Session

from wiki_data_dump.mirrors import Mirror, _name_to_mirror
import wiki_data_dump.cache
import wiki_data_dump.api_response
import wiki_data_dump.download


def _get_index_contents(mirror: Mirror, sess: Session) -> str:
    """Returns index.json contents from mirror."""

    res = sess.get(mirror.index_location, stream=True, timeout=5.0)
    total = int(res.headers['content-length'])

    p_bar = tqdm.tqdm(
        desc="Downloading index file",
        total=total,
        unit="B",
        unit_scale=True,
        unit_divisor=1024
    )

    t_file = tempfile.TemporaryFile()

    res.raise_for_status()

    chunk_size = 1024

    with p_bar, t_file:
        for b in res.iter_content(chunk_size):
            p_bar.update(t_file.write(b))
        t_file.seek(0)
        content = t_file.read().decode()

    return content


class WikiDump:
    """Primary class of wiki_data_dump, holds logic for getting items from the index of the mirror's site and provides
    utilities for downloading linked files."""

    mirror: Mirror
    session: Session
    response_json: dict
    _cached_wikis: Dict[str, wiki_data_dump.api_response.Wiki]

    def __init__(self,
                 mirror: Union[str, Mirror] = "wikimedia",
                 session: Session = None,
                 clear_expired_caches: bool = True):

        if isinstance(mirror, str):
            mirror = _name_to_mirror[mirror]
        self._mirror = mirror

        if session is None:
            session = Session()
        self.session = session

        self._update_response()

        if clear_expired_caches:
            wiki_data_dump.cache.clear_expired_caches()

    def _update_response(self) -> None:
        """Used internally for getting cached json response contents, and caching new index files as needed."""
        self._cached_wikis = {}
        _cache = wiki_data_dump.cache.get_cache(self.mirror)

        if _cache.content:
            content = _cache.content
        else:
            content = _get_index_contents(self.mirror, self.session)
            with open(_cache.path, 'w') as f_buffer:
                f_buffer.write(content)

        self._raw_response_json: dict = json.loads(content)

    @property
    def mirror(self) -> Mirror:
        """Returns the mirror instance the WikiDump is currently using."""
        return self._mirror

    @mirror.setter
    def mirror(self, val: Mirror):
        """Sets the mirror instance, and handles getting the appropriate index response."""
        self._mirror = val
        self._update_response()

    @property
    def response_json(self) -> dict:
        """Contains the raw response from the index.json file on the mirror."""
        return copy.deepcopy(self._raw_response_json)  # Internally, _raw_response_json should be used so copying
        # isn't required

    @overload
    def __getitem__(self, item: str) -> wiki_data_dump.api_response.Wiki: ...
    @overload
    def __getitem__(self, item: Tuple[str]) -> wiki_data_dump.api_response.Wiki: ...
    @overload
    def __getitem__(self, item: Tuple[str, str]) -> wiki_data_dump.api_response.Job: ...
    @overload
    def __getitem__(self, item: Tuple[str, str, Union[str, re.Pattern]]) -> wiki_data_dump.api_response.File: ...

    def __getitem__(self, item: Union[tuple, str]):
        """Convenience method for get_wiki, get_job, and get_file. Caches on every call."""

        if isinstance(item, str):
            return self.get_wiki(item)
        elif len(item) == 1:
            return self.get_wiki(item[0])
        elif len(item) == 2:
            return self.get_job(*item)
        elif len(item) == 3:
            return self.get_file(*item)
        raise TypeError("Argument must be a string, or a tuple containing <= 3 strings.")

    def get_wiki(self, wiki_name: str, cache: bool = True) -> wiki_data_dump.api_response.Wiki:
        """Get Wiki instance associated with wiki_name. Optionally caches result."""
        try:
            return self._cached_wikis[wiki_name]
        except KeyError:
            result = wiki_data_dump.api_response.Wiki(**self._raw_response_json['wikis'][wiki_name])
            if not cache:
                return result
            self._cached_wikis[wiki_name] = result
        return self._cached_wikis[wiki_name]

    def get_job(self, wiki_name: str,
                job_name: str, cache: bool = True) -> wiki_data_dump.api_response.Job:
        """Get Job instance associated with wiki_name and job_name. Optionally caches result."""
        wiki = self.get_wiki(wiki_name, cache=cache)
        return wiki.jobs[job_name]

    def get_file(self, wiki_name,
                 job_name, file_identifier: Union[str, re.Pattern],
                 cache: bool = True) -> wiki_data_dump.api_response.File:
        """Get File instance associated with wiki_name, job_name, and file_identifier. Optionally caches result."""
        job = self.get_job(wiki_name, job_name, cache=cache)
        return job.get_file(file_identifier)

    @property
    def wikis(self):
        """Get wiki names for every non-empty wiki in the raw response tree."""
        return [k for k in self._raw_response_json['wikis'].keys() if self._raw_response_json['wikis'][k]]

    def download(self,
                 file: wiki_data_dump.api_response.File,
                 destination: str = None,
                 decompress: bool = True) -> threading.Thread:
        """Downloads a File with an optional supplied destination - if no destination is supplied then it will be
         assigned based on the end component of the originating url. Also includes decompression based on file suffix,
         which can be turned off with decompress.

         Returns the Thread instance that the download is running on."""

        return wiki_data_dump.download.base_download(
            from_location=urllib.parse.urljoin(self.mirror.index_location, file.url),
            to_location=destination,
            sha1=file.sha1,
            size=file.size,
            decompress=decompress,
            session=self.session
        )

    def iter_files(self) -> Tuple[str, str, str]:
        """Returns an iterator that contains the file path components (wiki_name, job_name, file_name) for every file
        in the raw json response. Does not cache accessed wikis."""

        for wiki_name in self.wikis:
            for job_name, job in self.get_wiki(wiki_name, cache=False).jobs.items():
                job: wiki_data_dump.api_response.Job
                if not job.files:
                    continue
                for file in job.files.keys():
                    yield wiki_name, job_name, file


def all_mirrors() -> List[Mirror]:
    """Returns a list of all available mirrors."""
    return [c for c in _name_to_mirror.values()]
