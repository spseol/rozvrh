if [ -e rozvrh.json ]
then
    rm rozvrh.json
fi
scrapy runspider crawl-rozvrh.py -o rozvrh.json -t json
