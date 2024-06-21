#! /usr/bin/env python3

import requests
import subprocess
import yaml

from pathlib import Path


class Item:
    id: int
    title: str
    url: str
    data: dict


class NewsAPI:
    def get_categories(self) -> dict[int, str]:
        pass

    def get_category_items(self, category_id) -> list[Item]:
        pass

    def mark_item_as_read(self, item: Item):
        pass


class NextcloudNews(NewsAPI):
    def __init__(self, nextcloud_url: str, username: str, password: str):
        self.base_url = f"{nextcloud_url}/index.php/apps/news/api/v1-3"
        self.auth = (username, password)

    def get_categories(self):
        request = requests.get(f"{self.base_url}/folders", auth=self.auth)
        request.raise_for_status()

        folders = {
            -1: "No folder"
        }

        for folder in request.json()["folders"]:
            folders[int(folder["id"])] = folder["name"]

        return folders

    def get_category_items(self, category_id: int):
        request = requests.get(f"{self.base_url}/items", auth=self.auth, params={"type": 1, "getRead": "false", "batchSize": -1, "id": category_id})
        request.raise_for_status()

        items = []

        for raw_item in request.json()["items"]:
            item = Item()
            item.id = raw_item["id"]
            item.title = raw_item["title"]
            item.url = raw_item["url"]
            item.data = raw_item

            items.append(item)

        return items

    def mark_item_as_read(self, item: Item):
        request = requests.post(f"{self.base_url}/items/{item.id}/read", auth=self.auth)
        request.raise_for_status()


class TTRSS(NewsAPI):
    def __init__(self, base_url: str, username: str, password: str):
        self.api_url = f"{base_url}/api/"
        self.session_id = None

        self.login(username, password)

    def request(self, method: str, parameters: dict):
        response = requests.post(self.api_url, json={"op": method} | parameters)
        response.raise_for_status()
        response_data = response.json()

        status = response_data.get("status")
        if status == 0:
            return response_data.get("content")

        error = response_data.get("content", {}).get("error")

        raise RuntimeError(f"API returned status {status}: {error}")

    def login(self, username: str, password: str):
        self.session_id = self.request("login", {"user": username, "password": password}).get("session_id")

    def logout(self):
        if self.session_id is None:
            return

        self.call_method("logout")

    def call_method(self, method: str, parameters: dict = None):
        if parameters is None:
            parameters = {}

        return self.request(method, {"sid": self.session_id} | parameters)

    def get_categories(self):
        categories = {}

        for category in self.call_method("getCategories"):
            categories[category["id"]] = category["title"]

        return categories

    def get_category_items(self, category_id: int):
        articles = self.call_method("getHeadlines", {"feed_id": category_id, "is_cat": True, "view_mode": "unread"})

        items = []

        for article in articles:
            item = Item()
            item.id = article["id"]
            item.title = article["title"]
            item.url = article["link"]
            item.data = article

            items.append(item)

        return items

    def mark_item_as_read(self, item: Item):
        self.call_method("updateArticle", {"article_ids": item.id, "mode": 0, "field": 2})


def main():
    with Path("~/.config/news-dl.yml").expanduser().open("r") as config_file:
        config = yaml.safe_load(config_file)

    api_type = config.get("type")

    if api_type == "nextcloud-news":
        news_api = NextcloudNews(config.get("url"), config.get("username"), config.get("password"))
    elif api_type == "tt-rss":
        news_api = TTRSS(config.get("url"), config.get("username"), config.get("password"))
    else:
        raise RuntimeError(f"Invalid API type: {api_type}")

    category_name = config.get("category")

    categories = news_api.get_categories()
    category_id = list(categories.keys())[list(categories.values()).index(category_name)]

    items = news_api.get_category_items(category_id)

    if not items:
        print(f"No new items found in category '{category_name}'")
        return

    print(f"Found {len(items)} items to be downloaded:")

    for item in items:
        print(f"  {item.title} [{item.url}]")

    print()

    if input("Start download? [Y/n] ").strip().lower().startswith("n"):
        return

    for index, item in enumerate(items):
        print(f"Downloading item {index + 1} of {len(items)}: {item.title} [{item.url}]")

        exit_code = subprocess.run(config.get("download_command").format_map(item.data), shell=True).returncode
        if exit_code:
            print(f"Command failed with exit code {exit_code}")
            continue

        if input("Download successful. Mark item as read? [Y/n] ").strip().lower().startswith("n"):
            continue

        news_api.mark_item_as_read(item)


if __name__ == "__main__":
    main()
