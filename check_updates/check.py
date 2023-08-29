import json
import os
from urllib.request import urlopen

from docker_registry_client import DockerRegistryClient
from semantic_version import Version

ide_repos = {
    "IIU": "projector-idea-u",
    "IIC": "projector-idea-c",
    "PCP": "projector-pycharm-p",
    "PCC": "projector-pycharm-c",
    "RM": "projector-rubymine",
    "RD": "projector-rider",
    "CL": "projector-clion",
    "GO": "projector-goland",
    "WS": "projector-webstorm",
    "DG": "projector-datagrip",
    "PS": "projector-phpstorm"
}

if __name__ == "__main__":
    registry_username = os.getenv("REGISTRY_USERNAME")
    registry_password = os.getenv("REGISTRY_PASSWORD")
    registry = os.getenv("REGISTRY")

    product_codes = ",".join(ide_repos.keys())
    url = "https://data.services.jetbrains.com/products?code=" + product_codes + "&release.type=release"
    data: list = json.loads(urlopen(url).read())

    dh = DockerRegistryClient(registry, username=registry_username, password=registry_password)

    latest_releases = list()
    for code, repository in ide_repos.items():
        repo = dh.repository(repository)
        try:
            tags = repo.tags()
        except:
            tags = ["latest"]

        if tags is not None:
            tags.remove("latest")
            tags = [Version.coerce(tag) for tag in tags]
            parseTag = str(max(tags, default=2019)) + ".0.0"
            latest_tag = Version.coerce(parseTag)
        else:
            latest_tag = Version.coerce("2019.0.0")

        latest_version = Version.coerce(
            next(product["releases"][0]["version"] for product in data if product["code"] == code))

        if latest_version > latest_tag:
            release = dict()
            release["image"] = registry + "/" + repository
            release["version"] = next(product["releases"][0]["version"] for product in data if product["code"] == code)
            release["download"] = next(
                product["releases"][0]["downloads"]["linux"]["link"] for product in data if product["code"] == code)
            latest_releases.append(release)
            
    final = json.dumps(latest_releases).replace('"', '\\"')
    print(final)
