Git
===

This document will provide important Git information for the Vizmo NodeJS app.

## Setting the Github repo access localy

Clone the repo:

    git clone https://github.com/FCC/vizmo.git

Set the user credentials:

    git config user.name "Joe Smith"
    git config user.email "joe.smith@fcc.gov"

Set the SSH user/pass (git commands will stop asking you for your user/pass):

    git remote set-url origin https://joe:password@github.com/FCC/vizmo.git

Switch to `node-js` branch:

    git checkout node-js

## git status

    git status -s -b --untracked-files=all --ignored

![example](images/gitstatus.png)

## git Log

1 Liner

    git log --graph --pretty=format:"%Cred%h%Creset %an: %s - %Creset %C(yellow)%d%Creset %Cgreen(%cr)%Creset" --abbrev-commit --date=relative

![example](images/gitlog1.png)

Full graph stats

    git log --decorate --stat --graph --pretty=format:"%d %Cgreen%h%Creset (%ar - %Cgreen%an%Creset), %s%n"

![example](images/gitlog2.png)
