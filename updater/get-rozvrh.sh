if [ ! -d tmp ]
then
    mkdir tmp
fi
if [ -e tmp/rozvrh.json ]
then
    rm tmp/rozvrh.json
fi
scrapy runspider ../crawl-rozvrh.py -o tmp/rozvrh.json -t json -L WARNING
