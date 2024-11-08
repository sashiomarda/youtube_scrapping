import os
from googleapiclient.discovery import build
import requests
import re
import csv
import pickle
import argparse

with open("api_key.pkl", "rb") as f:
    api_key = pickle.load(f)

youtube = build("youtube", "v3", developerKey=api_key)


def main(keyword, maxResults, maxPages):
    nextPageToken = None
    page = 1
    while page <= maxPages:
        try:
            if nextPageToken:
                request1 = youtube.search().list(
                    part="snippet",
                    maxResults=maxResults,
                    pageToken=nextPageToken,
                    q=keyword,
                )
            else:
                request1 = youtube.search().list(
                    part="snippet", maxResults=maxResults, q=keyword
                )
            response1 = request1.execute()
            page += 1
            nextPageToken = response1.get("nextPageToken")
            columns = [
                "channel_id",
                "channel_title",
                "subscribe_count",
                "twitter_accounts",
                "facebook_accounts",
                "instagram_accounts",
            ]

            for item in response1["items"]:
                data = []
                request2 = youtube.channels().list(
                    part="snippet,statistics", id=item["snippet"]["channelId"]
                )
                response2 = request2.execute()
                x = requests.get(
                    f"https://www.youtube.com/channel/{item['snippet']['channelId']}/about"
                )
                twitter_accounts = list(
                    set(re.findall(r"(twitter.com/\b[a-zA-Z]*)", x.text))
                )
                fb_accounts = list(
                    set(re.findall(r"(facebook.com/\b[a-zA-Z]*)", x.text))
                )
                ig_accounts = list(
                    set(re.findall(r"(instagram.com/\b[a-zA-Z]*)", x.text))
                )
                if len(twitter_accounts) > 0:
                    twitter_accounts = ",".join(twitter_accounts)
                else:
                    twitter_accounts = ""
                if len(fb_accounts) > 0:
                    fb_accounts = ",".join(fb_accounts)
                else:
                    fb_accounts = ""
                if len(ig_accounts) > 0:
                    ig_accounts = ",".join(ig_accounts)
                else:
                    ig_accounts = ""

                data.append(item["snippet"]["channelId"])
                data.append(response2["items"][0]["snippet"]["title"])
                data.append(response2["items"][0]["statistics"]["subscriberCount"])
                data.append(twitter_accounts)
                data.append(fb_accounts)
                data.append(ig_accounts)

                with open("data.csv", "a", newline="") as csvfile:
                    writer = csv.writer(csvfile)
                    if os.stat("data.csv").st_size == 0:
                        writer.writerows([columns])
                    writer.writerows([data])
        except Exception as e:
            print("error ", e)
            continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--keyword", help="type of keyword to search for, example: game"
    )
    parser.add_argument("--maxresults", help="max results, example: 50")
    parser.add_argument("--maxpages", help="max pages, example: 1")
    args = parser.parse_args()
    keyword = str(args.keyword) if args.keyword else "game"
    maxResults = int(args.maxresults) if args.maxresults else 50
    maxPages = int(args.maxpages) if args.maxpages else 1
    main(keyword, maxResults, maxPages)
