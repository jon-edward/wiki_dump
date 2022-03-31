from typing import NamedTuple


class Mirror(NamedTuple):
    """Used to store details about a mirror source - including its name and index file url."""
    name: str
    index_location: str


WIKIMEDIA = Mirror(
    "Wikimedia",
    "https://dumps.wikimedia.org/index.json"
)

ACC_UMEA_UNI = Mirror(
    "Academic Computer Club, Umeå University",
    "https://gemmei.ftp.acc.umu.se/mirror/wikimedia.org/dumps/index.json"
)

BYTEMARK = Mirror(
    "Bytemark",
    "https://wikimedia.bytemark.co.uk/index.json"
)

BRING_YOUR = Mirror(
    "BringYour",
    "https://wikimedia.bringyour.com/index.json"
)

YOUR = Mirror(
    "Your",
    "https://dumps.wikimedia.your.org/index.json"
)

_name_to_mirror = {
    "wikimedia": WIKIMEDIA,
    "acc_umea_uni": ACC_UMEA_UNI,
    "bytemark": BYTEMARK,
    "bring_your": BRING_YOUR,
    "your": YOUR
}