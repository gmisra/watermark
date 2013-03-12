watermark
=========
Simple PDF watermarking tool

usage: 

    watermark.py [-h] -i INPUT [INPUT ...] -w WATERMARK -o OUTPUT [-f] [-p PREFIX] [-s SUFFIX]

    optional arguments:
      -h, --help            show this help message and exit
      -i INPUT [INPUT ...]  Glob pattern for identifying the files to process (a single filename is okay)
      -w WATERMARK          File containing the watermark (only the first page will be read)
      -o OUTPUT             Path to output directory. Output filenames are the same as input filenames)
      -f                    Force overwrite (by default, files will not be overwritten)
      -p PREFIX             Output filename prefix, appended to original filename (optional)
      -s SUFFIX             Output filename suffix, appended to original filename (optional)


PDFRW from: https://code.google.com/p/pdfrw/

Based on the example: https://code.google.com/p/pdfrw/source/browse/trunk/examples/watermark.py?r=114
