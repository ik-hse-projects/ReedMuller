#!/bin/sh
set -e

MK="latexmk -shell-escape -lualatex -aux-directory=out/ -emulate-aux-dir -interaction=nonstopmode"

if [ "$#" -gt 0 ]; then
    $MK "$@"
else
    $MK ./presentation.tex
    $MK ./with_notes.tex
    $MK ./article.tex
fi

