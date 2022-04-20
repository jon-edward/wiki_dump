import bz2
import functools
import gzip
import hashlib
import io
import re
from tempfile import NamedTemporaryFile
import threading
from types import TracebackType
from typing import Optional, Callable

import requests


ProgressHookType = Callable[[int, int], None]
CompletionHookType = Callable[[Optional[type], Optional[Exception], Optional[TracebackType]], None]


class _FileWrapper(io.IOBase):
    """Wraps a file for tracking how much of the file has been accessed. Used for tracking decompression."""

    def __init__(self, source: io.IOBase):
        self.source: io.IOBase = source
        self.delta = 0

    def read(self, n: int = None):
        if n:
            _content = self.source.read(n)
        else:
            _content = self.source.read()
        self.delta = len(_content)
        return _content


class _CompletionManager:
    """Accepts a hook which is passed arguments similar to those passed to a context manager."""
    hook: CompletionHookType

    def __init__(self, hook: CompletionHookType):
        self.hook = hook

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.hook(exc_type, exc_val, exc_tb)


def _decompress(
        from_file_wrapper: _FileWrapper,
        to_file_path: str,
        compression_type: str,
        progress_hook: ProgressHookType,
        completion_hook: CompletionHookType,
        size: int):
    """Decompresses file contained in a _FileWrapper."""

    assert compression_type in ('bz2', 'gz', None)

    transfer_chunk_size = 1024*10

    transfer_wrapper: io.IOBase = {
        "bz2": lambda: bz2.BZ2File(from_file_wrapper),
        "gz": lambda: gzip.GzipFile(fileobj=from_file_wrapper),
        None: lambda: from_file_wrapper
    }[compression_type]()

    with transfer_wrapper, open(to_file_path, "wb") as to_file_obj, _CompletionManager(completion_hook):
        while content := transfer_wrapper.read(transfer_chunk_size):
            to_file_obj.write(content)
            progress_hook(from_file_wrapper.delta, size)


def _download(
        response: requests.Response,
        intermediate_buffer: NamedTemporaryFile,
        chunk_size: int,
        size: int,
        progress_hook: ProgressHookType,
        completion_hook: CompletionHookType,
        sha1: str):
    """Download file from response and verify sha1 sum if available."""

    hex_d = hashlib.sha1()

    with _CompletionManager(completion_hook):
        for chunk in response.iter_content(chunk_size=chunk_size):
            progress_hook(intermediate_buffer.write(chunk), size)
            hex_d.update(chunk)

    if sha1:
        assert sha1 == hex_d.hexdigest(), "Download verification failed."


def _download_and_decompress(from_location: str,
                             to_location: str,
                             size: int,
                             session: requests.Session,
                             sha1: str,
                             compression_type: str,
                             download_progress_hook: ProgressHookType,
                             download_completion_hook: CompletionHookType,
                             decompress_progress_hook: ProgressHookType,
                             decompress_completion_hook: CompletionHookType,
                             chunk_size: int = 1024):
    """Downloads file from source, then decompresses it by the protocol provided."""

    response = session.get(from_location, stream=True)
    response.raise_for_status()

    with NamedTemporaryFile() as intermediate_buffer:
        _download(response, intermediate_buffer,
                  chunk_size, size,
                  download_progress_hook, download_completion_hook,
                  sha1)

        intermediate_buffer.seek(0)

        wrapper = _FileWrapper(intermediate_buffer)

        return _decompress(
            wrapper,
            to_location,
            compression_type,
            decompress_progress_hook,
            decompress_completion_hook,
            size
        )


def _automatic_resolve_to_location(_from_location: str, _will_decompress: bool) -> str:
    """Holds logic for automatic destination assignment/file suffix cleanup."""
    last_term = _from_location.split("/")[-1]

    if _will_decompress:
        return re.compile(r"(?:\.gz|\.bz2)$").sub("", last_term, count=1)

    return last_term


def progress_hook_noop(delta: int, total: int):
    """
    Does nothing, but takes the arguments that would otherwise be passed to a progress hook.
    """


def completion_hook_noop(exc_type: Optional[type],
                         exc_val: Optional[Exception],
                         exc_tb: Optional[TracebackType]):
    """
    Does nothing, but takes the arguments that would otherwise be passed to a completion hook.
    """


def base_download(
        from_location: str,
        to_location: Optional[str],
        size: int,
        session: requests.Session,
        sha1: str,
        decompress: bool,
        download_progress_hook: ProgressHookType,
        download_completion_hook: CompletionHookType,
        decompress_progress_hook: ProgressHookType,
        decompress_completion_hook: CompletionHookType,
        chunk_size: int = 1024):
    """Contains core logic for path resolution, compression type resolution, hook resolution, and threading."""

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

    def progress_noop_if_none(x) -> ProgressHookType:
        return progress_hook_noop if x is None else x

    def completion_noop_if_none(x) -> CompletionHookType:
        return completion_hook_noop if x is None else x

    kw = {
        "from_location": from_location,
        "to_location": to_location,
        "size": size,
        "session": session,

        "sha1": sha1,
        "chunk_size": chunk_size,
        "compression_type": compression_type,

        "download_progress_hook": progress_noop_if_none(download_progress_hook),
        "download_completion_hook": completion_noop_if_none(download_completion_hook),
        "decompress_progress_hook": progress_noop_if_none(decompress_progress_hook),
        "decompress_completion_hook": completion_noop_if_none(decompress_completion_hook),
    }

    func = functools.partial(_download_and_decompress, **kw)

    t = threading.Thread(target=func)
    t.start()
    return t
