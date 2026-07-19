"""Download the Tennessee Eastman source files from Harvard Dataverse.

The script keeps raw files outside version control and records a manifest with
the source URL, file identifier, size and SHA-256 checksum for reproducibility.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen


DOI = "doi:10.7910/DVN/6C3JR1"
API_ROOT = "https://dataverse.harvard.edu/api"
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def fetch_json(url: str) -> dict:
    request = Request(url, headers={"User-Agent": "chemical-process-performance-analytics/1.0"})
    with urlopen(request, timeout=60) as response:
        return json.load(response)


def download(url: str, destination: Path) -> str:
    request = Request(url, headers={"User-Agent": "chemical-process-performance-analytics/1.0"})
    digest = hashlib.sha256()
    temporary = destination.with_suffix(destination.suffix + ".part")
    with urlopen(request, timeout=180) as response, temporary.open("wb") as handle:
        while chunk := response.read(1024 * 1024):
            handle.write(chunk)
            digest.update(chunk)
    temporary.replace(destination)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "data" / "raw",
        help="Directory for publisher-supplied files.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Download files again even when they already exist.",
    )
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    metadata_url = f"{API_ROOT}/datasets/:persistentId/?persistentId={quote(DOI)}"
    payload = fetch_json(metadata_url)
    if payload.get("status") != "OK":
        raise RuntimeError(f"Dataverse metadata request failed: {payload}")

    version = payload["data"]["latestVersion"]
    manifest = {
        "dataset_doi": DOI,
        "dataset_version": version.get("versionNumber"),
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "metadata_url": metadata_url,
        "files": [],
    }

    for item in version.get("files", []):
        data_file = item["dataFile"]
        file_id = data_file["id"]
        filename = data_file["filename"]
        destination = args.output_dir / filename
        access_url = f"{API_ROOT}/access/datafile/{file_id}"

        if destination.exists() and not args.force:
            sha256 = hashlib.sha256(destination.read_bytes()).hexdigest()
            status = "existing"
        else:
            sha256 = download(access_url, destination)
            status = "downloaded"

        manifest["files"].append(
            {
                "file_id": file_id,
                "filename": filename,
                "content_type": data_file.get("contentType"),
                "size_bytes": destination.stat().st_size,
                "sha256": sha256,
                "access_url": access_url,
                "status": status,
            }
        )
        print(f"{status:>10}  {filename}")

    manifest_path = args.output_dir / "source_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Manifest written to {manifest_path}")


if __name__ == "__main__":
    main()
