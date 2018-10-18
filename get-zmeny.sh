if [ -e zmeny.json ]
then
    rm zmeny.json
fi
scrapy runspider crawl-zmeny.py -o zmeny.json -t json
