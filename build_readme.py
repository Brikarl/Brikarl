import datetime
import pathlib
import re

import feedparser

root = pathlib.Path(__file__).parent.resolve()


def replace_chunk(content, marker, chunk, inline=False):
    r = re.compile(
        r"<!\-\- {} starts \-\->.*<!\-\- {} ends \-\->".format(marker, marker),
        re.DOTALL,
    )
    if not inline:
        chunk = "\n{}\n".format(chunk)
    chunk = "<!-- {} starts -->{}<!-- {} ends -->".format(marker, chunk, marker)
    return r.sub(chunk, content)


def fetch_douban():
    entries = feedparser.parse("https://www.douban.com/feed/people/141831176/interests")["entries"]
    return [
        {
            "title": item["title"],
            "url": item["link"].split("#")[0],
            "published": formatGMTime(item["published"])
        }
        for item in entries
    ]


def formatGMTime(timestamp):
    GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
    dateStr = datetime.datetime.strptime(timestamp, GMT_FORMAT) + datetime.timedelta(hours=8)
    return dateStr.date()


if __name__ == "__main__":
    readme = root / "README.md"
    readme_contents = readme.open().read()
    doubans = fetch_douban()

    doubans_md = "\n".join(
        ["- [{title}]({url}) - {published}".format(**item) for item in doubans]
    )

    rewritten = replace_chunk(readme_contents, "douban", doubans_md)

    readme.open("w").write(rewritten)
