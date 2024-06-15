#! /usr/bin/env python3

import requests
import subprocess
import yaml

from pathlib import Path


class NextcloudNews:
    def __init__(self, nextcloud_url: str, username: str, password: str):
        self.base_url = f"{nextcloud_url}/index.php/apps/news/api/v1-3"
        self.auth = (username, password)

    def get_folders(self):
        request = requests.get(f"{self.base_url}/folders", auth=self.auth)
        request.raise_for_status()

        folders = {
            -1: "No folder"
        }

        for folder in request.json()["folders"]:
            folders[int(folder["id"])] = folder["name"]

        return folders

    def get_folder_items(self, folder_id: int):
        request = requests.get(f"{self.base_url}/items", auth=self.auth, params={"type": 1, "getRead": "false", "batchSize": -1, "id": folder_id})
        request.raise_for_status()

        return request.json()["items"]

    def mark_item_as_read(self, item_id: int):
        request = requests.post(f"{self.base_url}/items/{item_id}/read", auth=self.auth)
        request.raise_for_status()


def main():
    with Path("~/.config/nextcloud-news-dl.yml").expanduser().open("r") as config_file:
        config = yaml.safe_load(config_file)

    nextcloud_news = NextcloudNews(config.get("url"), config.get("username"), config.get("password"))
    folder_name = config.get("folder")

    folders = nextcloud_news.get_folders()
    folder_id = list(folders.keys())[list(folders.values()).index(folder_name)]

    items = nextcloud_news.get_folder_items(folder_id)

    if not items:
        print(f"No new items found in folder '{folder_name}'")
        return

    print(f"Found {len(items)} items to be downloaded:")

    for item in items:
        title = item.get("title")
        url = item.get("url")

        print(f"  {title} [{url}]")

    print()

    if input("Start download? [Y/n] ").strip().lower().startswith("n"):
        return

    for index, item in enumerate(items):
        item_id = item.get("id")
        title = item.get("title")
        url = item.get("url")

        print(f"Downloading item {index + 1} of {len(items)}: {title} [{url}]")

        exit_code = subprocess.run(config.get("download_command").format_map(item), shell=True).returncode
        if exit_code:
            print(f"Command failed with exit code {exit_code}")
            continue

        if input("Download successful. Mark item as read? [Y/n] ").strip().lower().startswith("n"):
            continue

        nextcloud_news.mark_item_as_read(item_id)


if __name__ == "__main__":
    main()
