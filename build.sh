#!/bin/sh
set -e

MK="latexmk -shell-escape -lualatex -aux-directory=aux/ -emulate-aux-dir -interaction=nonstopmode ./ReedMuller.tex"

if [ "$#" -gt 0 ]; then
    jobname="$1"
    shift
    $MK -jobname="ReedMuller-$jobname" "$@"
else
    $MK -jobname=ReedMuller-speaker
    $MK -jobname=ReedMuller-article
    $MK -jobname=ReedMuller-handout
    $MK -jobname=ReedMuller-slides
    $MK -jobname=ReedMuller-trans
fi

