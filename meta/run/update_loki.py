import concurrent.futures
import hashlib
import os

from meta.common import upstream_path, ensure_upstream_dir, default_session
from meta.common.loki import BASE_DIR, RELEASES_API_URL, VERSIONS_FILE
from meta.common.github import fetch_releases
from meta.model.loki import LokiVersion, LokiIndex
from meta.model.github import GitHubReleaseAsset, GitHubReleaseEntry

UPSTREAM_DIR = upstream_path()

ensure_upstream_dir(BASE_DIR)

sess = default_session()


def convert_to_loki(entry: GitHubReleaseEntry, version: str, asset: GitHubReleaseAsset,
                    is_recommended: bool) -> LokiVersion:
    download_url = asset.browser_download_url

    print(f"Downloading {download_url}")
    r = sess.get(download_url, timeout=30)
    r.raise_for_status()

    return LokiVersion(
        version=version,
        published_at=entry.published_at,
        download_url=download_url,
        file_size=asset.size,
        file_sha1=hashlib.sha1(r.content).hexdigest(),
        prerelease=entry.prerelease,
        recommended=is_recommended
    )


def main():
    print("Getting Loki release manifests")
    releases = fetch_releases(RELEASES_API_URL, sess)

    existing_versions = dict()
    versions_file_path = os.path.join(UPSTREAM_DIR, VERSIONS_FILE)
    if os.path.exists(versions_file_path):
        try:
            existing_index = LokiIndex.parse_file(versions_file_path)
            for v in existing_index.versions:
                existing_versions[v.version] = v
        except Exception as e:
            print(f"Failed to read existing versions: {e}")

    versions = []
    futures = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        has_recommended = False
        for entry in releases:
            version = entry.tag_name.removeprefix("v")
            jar_name = f"Loki-{version}.jar"

            asset = next((a for a in entry.assets if a.name == jar_name), None)
            if asset is None:
                print(f"Skipping {entry.tag_name}: no asset named {jar_name}")
                continue

            recommended = (not entry.prerelease and not has_recommended)
            if recommended:
                has_recommended = True

            if version in existing_versions:
                existing = existing_versions[version]
                existing.recommended = recommended
                versions.append(existing)
            else:
                futures.append(executor.submit(convert_to_loki, entry, version, asset, recommended))

    for future in futures:
        versions.append(future.result())

    if len(versions) == 0:
        raise Exception("Attempted to write empty versions list", versions, releases)

    loki_index = LokiIndex(
        versions=versions,
    )
    loki_index.write(versions_file_path)


if __name__ == "__main__":
    main()
