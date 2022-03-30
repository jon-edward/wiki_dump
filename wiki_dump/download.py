import bz2
import functools
import gzip
import hashlib
import io
import os.path
import re
from tempfile import NamedTemporaryFile
import threading
from typing import Optional

import requests
import tqdm


def _file_process_p_bar(message: str, total: int):
    """Creates a tqdm progress bar for working on system memory with standard unit scaling."""

    p_bar = tqdm.tqdm(
        desc=message,
        total=total,
        unit="B",
        unit_scale=True,
        unit_divisor=1024
    )
    return p_bar


class _FileWrapper(io.IOBase):
    """Wraps a file for tracking how much of the file has been accessed. Used for tracking decompression."""

    def __init__(self, source: io.IOBase):
        self.source: io.IOBase = source
        self.progress = 0

    def read(self, n: int = None):
        if n:
            _content = self.source.read(n)
        else:
            _content = self.source.read()
        self.progress += len(_content)
        return _content


def _decompress(
        from_file_wrapper: _FileWrapper,
        to_file_path: str,
        compression_type: str,
        size: int):
    """Decompresses file contained in a _FileWrapper."""

    assert compression_type in ('bz2', 'gz', None)

    p_bar = _file_process_p_bar(f"{'Decompressing' if compression_type is not None else 'Writing'} to "
                                f"{os.path.relpath(to_file_path)}", size)

    transfer_chunk_size = 1024*10

    transfer_wrapper: io.IOBase = {
        "bz2": lambda: bz2.BZ2File(from_file_wrapper),
        "gz": lambda: gzip.GzipFile(fileobj=from_file_wrapper),
        None: lambda: from_file_wrapper
    }[compression_type]()

    previous = 0

    with transfer_wrapper, open(to_file_path, "wb") as to_file_obj, p_bar:
        while content := transfer_wrapper.read(transfer_chunk_size):
            delta = from_file_wrapper.progress - previous
            p_bar.update(delta)
            to_file_obj.write(content)
            previous = from_file_wrapper.progress


def _download_and_decompress(from_location: str,
                             to_location: str,
                             size: int,
                             session: requests.Session,
                             sha1: str,
                             compression_type: str,
                             chunk_size: int = 1024):
    """Downloads file from source, then decompresses it by the protocol provided."""

    response = session.get(from_location, stream=True)
    response.raise_for_status()
    hex_d = hashlib.sha1()

    with NamedTemporaryFile() as intermediate_buffer, \
            _file_process_p_bar(f"Downloading from {from_location}", size) as p_bar:

        for chunk in response.iter_content(chunk_size=chunk_size):
            p_bar.update(intermediate_buffer.write(chunk))
            hex_d.update(chunk)

        assert sha1 == hex_d.hexdigest(), "Download verification failed."

        p_bar.close()

        intermediate_buffer.seek(0)

        transfer_file: io.IOBase

        wrapper = _FileWrapper(intermediate_buffer)

        return _decompress(
            wrapper,
            to_location,
            compression_type,
            size
        )


def _automatic_resolve_to_location(_from_location: str, _will_decompress: bool) -> str:
    """Holds logic for automatic destination assignment/file suffix cleanup."""
    last_term = _from_location.split("/")[-1]

    if _will_decompress:
        return re.compile(r"(?:\.gz|\.bz2)$").sub("", last_term, count=1)

    return last_term


def base_download(
        from_location: str,
        to_location: Optional[str],
        size: int,
        session: requests.Session,
        sha1: str,
        decompress: bool,
        chunk_size: int = 1024):
    """Used internally for creating a Thread that downloads from a specified url,
    and running the download/decompression routine."""

    to_location = to_location if to_location is not None else _automatic_resolve_to_location(
        from_location, decompress
    )

    if not decompress:
        compression_type = None
    elif from_location.endswith(".gz"):
        compression_type = "gz"
    elif from_location.endswith(".bz2"):
        compression_type = "bz2"
    else:
        compression_type = None

    kw = {
        "from_location": from_location,
        "to_location": to_location,
        "size": size,
        "session": session,
        "sha1": sha1,
        "chunk_size": chunk_size,
        "compression_type": compression_type
    }

    func = functools.partial(_download_and_decompress, **kw)

    t = threading.Thread(target=func)
    t.start()
    return t
