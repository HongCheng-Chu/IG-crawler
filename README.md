# IG-crawler
IG crawler with account/tag/story in Python.
  - Account: IG_account_crawler
  - tag: IG_tag_crawler
  - story: IG_story_crawler

## Functionality:
- Download image and video..
- Store instagram user cookie.

## Operation
1. Enter account and password.
2. After get_cookie finisged, enter target_name which you want to download.
3. Wait and enjoy it.

## Notes
- In IG_story_crawler.py, about get_cookie function, ChromeOptions.add_argument('--headless') can not be hidden.
- IG_tag_crawler.py only download in image.

## Reference
- Algorithm is based on ChiaYu-Chiang/IG-crawler.
