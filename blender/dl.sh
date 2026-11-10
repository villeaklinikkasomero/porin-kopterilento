#!/bin/sh
# parallel resumable ranged download
URL=$(cat bpyurl.txt); SIZE=402908800; N=16; CH=$((SIZE/N+1))
i=0
while [ $i -lt $N ]; do
  s=$((i*CH)); e=$((s+CH-1)); [ $e -ge $SIZE ] && e=$((SIZE-1))
  f=part$i; have=0; [ -f $f ] && have=$(stat -c %s $f)
  if [ $((s+have)) -le $e ]; then curl -s -r $((s+have))-$e "$URL" >> $f & fi
  i=$((i+1))
done
wait
