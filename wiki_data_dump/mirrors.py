import enum
from typing import NamedTuple


class _Mirror(NamedTuple):
    """Used to store details about a mirror source - including its name and index file url."""
    name: str
    index_location: str


class MirrorType(enum.Enum):
    """Contains valid wiki mirror destinations."""

    WIKIMEDIA = _Mirror(
        "Wikimedia",
        "https://dumps.wikimedia.org/index.json"
    )

    ACC_UMEA_UNI = _Mirror(
        "Academic Computer Club, Umeå University",
        "https://gemmei.ftp.acc.umu.se/mirror/wikimedia.org/dumps/index.json"
    )

    BYTEMARK = _Mirror(
        "Bytemark",
        "https://wikimedia.bytemark.co.uk/index.json"
    )

    BRING_YOUR = _Mirror(
        "BringYour",
        "https://wikimedia.bringyour.com/index.json"
    )

    YOUR = _Mirror(
        "Your",
        "https://dumps.wikimedia.your.org/index.json"
    )
