url="`cat target_url`"

merge() {
    fname="tmp/final-$1.json"
    touch "$fname"
    python3 merge.py "tmp/$1.json" "$fname" > "$fname.tmp"
    mv "$fname.tmp" "$fname"
}

SUM="`md5sum tmp/rozvrh.json | cut -d' ' -f1,1`"
if [ "`cat SENT_ROZVRH`" != "$SUM" ]
then
    echo 'updating rozvrh'
    curl -F "file=@tmp/final-rozvrh.json" "$url/rozvrh"
    echo "$SUM" > SENT_ROZVRH
fi

SUM="`md5sum tmp/zmeny.json | cut -d' ' -f1,1`"
if [ "`cat SENT_ZMENY`" != "$SUM" ]
then
    echo 'updating zmeny'
    merge zmeny
    curl -F "file=@tmp/final-zmeny.json" "$url/zmeny"
    echo "$SUM" > SENT_ZMENY
fi
echo " Done. "
