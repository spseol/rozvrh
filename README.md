# rozvrh

```
templates/      - html templates for app.py
updater/        - scripts for crawling automation
app.py          - python3.5 and flask
crawl-rozvrh.py - python3.6 (should work under 3.5 too) and scrapy
crawl-zmeny.py  - python3.6 (should work under 3.5 too) and scrapy
get-rozvrh.sh   - shell script that runs crawl-rozvrh.py and stores result in rozvrh.json
get-zmeny.sh    - shell script that runs crawl-zmeny.py and stores result in zmeny.json
rozvrh.json    << app.py requires this file (not provided in repo)
zmeny.json     << app.py requires this file (not provided in repo)
```

*`rozvrh.json` and `zmeny.json` should be located in `app.py`'s working directory*
