#!/bin/bash

commit_changes() {
	cd /var/lib/git/ubuntu-config || exit 1
	if [[ $(git status --porcelain) ]]; then
		git add .
		git commit -m "chore: update"
	else
		echo "No changes"
	fi
}

i=0
while [ $i -lt 12 ]; do
	commit_changes & #run your command
	sleep 5
	i=$((i + 1))
done
