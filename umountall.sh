#!/usr/bin/bash

DIR="$1"

for i in $(mount | \
	   grep "${DIR}" | \
	   sed -e "s/^.* on //" | \
	   sed -e "s/ type .*\$//" | \
	   sort -ru) ; do
    umount "$i"
done


