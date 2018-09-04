#!/bin/sh
#
# Simple script for building book. Add flag --final to run bibtex,
# makeindex etc and build the final version of the book.

FILE=$1

if [ "x$2" = "x--final" ]; then
    pdflatex $FILE
    bibtex $FILE
    pdflatex $FILE
    pdflatex $FILE
else
    pdflatex $FILE
fi
