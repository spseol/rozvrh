if [ ! -d tmp ]
then
    mkdir tmp
fi
if [ -e tmp/zmeny.json ]
then
    rm tmp/zmeny.json
fi
scrapy runspider ../crawl-zmeny.py -o tmp/zmeny.json -t json -L WARNING
