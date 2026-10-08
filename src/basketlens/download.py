"""Fetch an openly licensed UCI dataset into a gitignored local directory."""
from __future__ import annotations
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import zipfile
import requests

DATA_URL = "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"
MAX_ZIP_BYTES = 150_000_000
MAX_XLSX_BYTES = 250_000_000


def download_uci(destination_dir: str | Path, *, url: str = DATA_URL) -> Path:
    """Stream ZIP and extract only an XLSX payload, with size and integrity checks."""
    dest = Path(destination_dir)
    dest.mkdir(parents=True, exist_ok=True)
    target = dest / "online_retail_II.xlsx"
    if target.exists():
        raise FileExistsError(f"Input already exists: {target}. Remove manually if replacement is intended.")
    with tempfile.TemporaryDirectory(prefix=".uci-download-", dir=dest) as working:
        zipped = Path(working) / "download.zip"
        zip_digest = sha256()
        total = 0
        with requests.get(url, stream=True, timeout=(20, 120),
                          headers={"User-Agent": "BasketLens-Research/0.1"}) as response:
            response.raise_for_status()
            with zipped.open("wb") as out:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if not chunk:
                        continue
                    total += len(chunk)
                    if total > MAX_ZIP_BYTES:
                        raise ValueError("Download exceeds expected ZIP size ceiling")
                    out.write(chunk)
                    zip_digest.update(chunk)
        if not zipfile.is_zipfile(zipped):
            raise ValueError("Download was not a valid ZIP archive. Use the UCI dataset page manually.")
        with zipfile.ZipFile(zipped) as archive:
            xlsx = [entry for entry in archive.infolist() if entry.filename.lower().endswith(".xlsx")]
            if len(xlsx) != 1:
                raise ValueError(f"Expected one XLSX in UCI archive, found {len(xlsx)}")
            if xlsx[0].file_size > MAX_XLSX_BYTES:
                raise ValueError("Spreadsheet exceeds allowed uncompressed size")
            payload = Path(working) / "payload.xlsx"
            with archive.open(xlsx[0]) as source, payload.open("wb") as out:
                while piece := source.read(1024 * 1024):
                    out.write(piece)
            if not zipfile.is_zipfile(payload):
                raise ValueError("Extracted spreadsheet failed XLSX integrity check")
            payload.replace(target)
    metadata = {"source": url, "archive_sha256": zip_digest.hexdigest(),
                "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
                "dataset_citation": "Chen, D. (2019). Online Retail II. UCI Machine Learning Repository.",
                "doi": "10.24432/C5CG6D", "license": "CC BY 4.0"}
    (dest / "source_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return target
