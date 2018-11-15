# Copyright 2018 miruka
# This file is part of pydecensooru, licensed under LGPLv3.

from datetime import datetime
from pathlib import Path
from typing import Generator, Iterable, Optional

import appdirs
import dulwich.porcelain as git

from . import __about__

DATA_DIR:            Path = Path(appdirs.user_data_dir(__about__.__pkg_name__))
REPO_DIR:            Path = DATA_DIR / "repository"
BATCHES_DIR:         Path = REPO_DIR / "batches"
LAST_PULL_DATE_FILE: Path = DATA_DIR / "last_pull_date"

REPO_URL: str = "git://github.com/friendlyanon/decensooru"


def decensor_iter(posts_info: Iterable[dict], subdomain: str = "danbooru"
                 ) -> Generator[dict, None, None]:
    """Apply decensoring on an iterable of posts info dicts from Danbooru API.
    Any censored post is automatically decensored if needed."""
    for info in posts_info:
        yield decensor(info, subdomain)


def decensor(post_info: dict, subdomain: str = "danbooru") -> dict:
    "Decensor a post info dict from Danbooru API if needed."
    return post_info \
           if "md5" in post_info else fill_missing_info(post_info, subdomain)



def fill_missing_info(info: dict, subdomain: str = "danbooru") -> dict:
    "Add missing info in a censored post info dict."
    try:
        md5, ext = find_censored_md5ext(info["id"])
    except TypeError:  # None returned by find_..
        return info

    sample_ext = "jpg" if ext != "zip" else "webm"

    if info["id"] > 2_800_000:
        url_base   = f"https://{subdomain}.donmai.us"
        file_url   = f"{url_base}/data/{md5}.{ext}"
        sample_url = f"{url_base}/data/sample/sample-{md5}.{sample_ext}"
    else:
        server     = "raikou2" if info["id"] > 850_000 else "raikou1"
        url_base   = f"https://{server}.donmai.us"
        file_url   = f"{url_base}/{md5[:2]}/{md5[2:4]}/{md5}.{ext}"
        sample_url = (f"{url_base}/sample/{md5[:2]}/{md5[2:4]}/"
                      f"sample-{md5}.{sample_ext}")

    if info["image_width"] < 850:
        sample_url = file_url

    return {**info, **{
        "file_ext":         ext,
        "md5":              md5,
        "file_url":         file_url,
        "large_file_url":   sample_url,
        "preview_file_url": (f"https://raikou4.donmai.us/preview/"
                             f"{md5[:2]}/{md5[2:4]}/{md5}.jpg"),
    }}


class _DummyFile():
    @staticmethod
    def write(*args, **kwargs):
        pass
_DUMMY_FILE = _DummyFile()


def find_censored_md5ext(post_id: int) -> Optional[str]:
    "Find MD5 for a censored post's ID, return None if can't find."
    DATA_DIR.mkdir(exist_ok=True, parents=True)

    if REPO_DIR.exists():
        try:
            last_pull_date = LAST_PULL_DATE_FILE.read_text().strip()
        except FileNotFoundError:
            last_pull_date = ""

        date = datetime.utcnow()
        date = f"{date.year}{date.month}{date.day}"

        if last_pull_date != date:
            git.pull(str(REPO_DIR), REPO_URL, errstream=_DUMMY_FILE)
            LAST_PULL_DATE_FILE.write_text(date)
    else:
        git.clone(REPO_URL, target=str(REPO_DIR), errstream=_DUMMY_FILE)
        date = datetime.utcnow()
        LAST_PULL_DATE_FILE.write_text(f"{date.year}{date.month}{date.day}")

    # Faster than converting every ID in files to int
    post_id = str(post_id)

    for batch in BATCHES_DIR.iterdir():
        with open(batch, "r") as content:
            for line in content:
                an_id, its_md5_ext = line.split(":")

                if post_id == an_id:
                    return its_md5_ext.rstrip().split(".")

    return None
