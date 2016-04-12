#!/bin/bash

mkdir -p temp/wip_images

# Run the analysis
python analysis.py

# Create the comparison figure
ORIGINALS=($(find temp/ -type f -name *_original*))
NUM_IMAGES=6
STEP=$((${#ORIGINALS[@]} / ($NUM_IMAGES - 1)))
ORIGINAL_NUMBERS=($(seq 0 $STEP ${#ORIGINALS[@]}))
ALPHABET=({b..z})
mkdir -p temp/comparison_images
for I in $(seq 0 $(($NUM_IMAGES - 1)));
do
    convert ${ORIGINALS[${ORIGINAL_NUMBERS[$I]}]} \
        -fill black \
        -font Helvetica-bold \
        -pointsize 20 \
        -gravity east -extent 200x150 \
        label:"(${ALPHABET[$I]})" \
        -gravity northwest \
        -geometry +10+12 \
        -composite \
        temp/comparison_images/${ALPHABET[$I]}

    convert ${ORIGINALS[${ORIGINAL_NUMBERS[$I]}]/original/gpy} \
        -fill black \
        -font Helvetica-bold \
        -pointsize 20 \
        -gravity east -extent 200x150 \
        label:"(${ALPHABET[$(($I + $NUM_IMAGES))]})" \
        -gravity northwest \
        -geometry +10+12 \
        -composite \
        temp/comparison_images/${ALPHABET[$(($I + $NUM_IMAGES))]}
done
montage $(find temp/comparison_images -type f | sort) \
    -tile x2 \
    -geometry +5+5 \
    temp/multi.png
convert reference.jpg \
    -resize x150 \
    -fill black \
    -font Helvetica-bold \
    -pointsize 20 \
    -gravity east -extent 200x150 \
    label:"(a)" \
    -gravity northwest \
    -geometry +10+12 \
    -composite \
    temp/reference.png
mkdir figures
montage temp/reference.png temp/multi.png \
    -gravity center \
    -geometry +10+12 \
    -tile x1 \
    figures/comparison.png



# Run the R script to plot results
Rscript plot.R

# Clean everything up
# rm -rf temp/
