#!/usr/bin/env python


'''
Usage:

watermark.py -w watermark_file -i input_pattern [-o, -p, -s]
  -w File containing the watermark (only the first page will be read)
  -i Glob pattern for identifying the files to process (a single filename is okay)
  -o Path to output directory (output filenames are the same as input filenames)
  -f Force overwrite (be default, files will not be overwritten)
  -p Output filename prefix, appended to original filename (optional)
  -s Output filename suffix, appended to original filename (optional)
'''


# Based on watermarking example from
# https://code.google.com/p/pdfrw/source/browse/trunk/examples/watermark.py?r=114


import argparse
import glob
import os
import traceback

from pdfrw import PdfReader, PdfWriter, PdfDict, IndirectPdfDict, PdfArray
from pdfrw.buildxobj import pagexobj

def watermark_page(page, watermark):

    # Find the page's resource dictionary. Create if none
    resources = page.inheritable.Resources
    if resources is None:
        resources = page.Resources = PdfDict()

    # Find or create the parent's xobject dictionary
    xobjdict = resources.XObject
    if xobjdict is None:
        xobjdict = resources.XObject = PdfDict()

    # Allow for an infinite number of cascaded watermarks
    index = 0
    while '/Watermark.%d' % index in xobjdict:
        index += 1
    xobjdict['/Watermark.%d' % index] = watermark

    # Turn the contents into an array if it is not already one
    contents = page.Contents
    if not isinstance(contents, PdfArray):
        contents = page.Contents = PdfArray([contents])

    # Save initial state before executing page
    contents.insert(0, IndirectPdfDict(stream='q\n'))

    # Restore initial state and append the watermark
    contents.append(IndirectPdfDict(stream='Q %s Do\n' % '/Watermark.%d' % index))
    return page


def process_file(f_input, f_watermark, f_output):

    watermark = pagexobj(PdfReader(f_watermark, decompress=False).pages[0])

    pagestream = PdfReader(f_input, decompress=False)
    for page in pagestream.pages:
        watermark_page(page, watermark)
    PdfWriter().write(f_output, pagestream)

    return len(pagestream.pages)


def batch_watermark(todo, args):

    total_pages = 0
    for row in todo:
        if os.path.exists(row['out']):
            print 'Skipping %s' % row['out'] if not args.overwrite else 'Overwriting %s' % row['out']
            if not args.overwrite: continue

        try:
            total_pages += process_file(row['in'], args.watermark, row['out'])
            print 'Watermarked %s and wrote %s' % (row['in'], row['out'])
        except Exception:
            print 'Failed processing %s' % row['in']
            print traceback.format_exc()[:2000]
            #raise

    print '\nSuccessfully watermarked %d pages' % total_pages


def identify_files_to_process(args):
    todo = []

    dest = args.output
    if not os.path.exists(dest):
        os.mkdir(dest)

    if not os.path.isfile(args.watermark):
        raise 'Could not locate watermark file %s' % args.watermark


    files = []
    for entry in args.input:
        if os.path.isdir(entry):
            files += glob.glob('%s/*.pdf' % entry)
        else:
            files.append(entry)

    for f in files:
        if not os.path.isfile(f):
            print '%s is not a valid input files' % f
        else:
            todo.append(f)

    dirs = [os.path.dirname(x) for x in todo]
    todo = [os.path.basename(x) for x in todo]

    todo = [x[:-4] if x.endswith('.pdf') else x for x in todo]

    if not args.prefix: args.prefix = ''
    if not args.suffix: args.suffix = ''

    return  [{'in': '%s/%s.pdf' % (dirs[i], todo[i]), 'out': '%s/%s%s%s.pdf' % (dest, args.prefix, todo[i], args.suffix) } for i in range(0, len(todo))]



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='watermark.py')
    parser.add_argument('-i', dest='input', required=True, nargs='+', help='Glob pattern for identifying the files to process (a single filename is okay)')
    parser.add_argument('-w', dest='watermark', required=True, help='File containing the watermark (only the first page will be read)')
    parser.add_argument('-o', dest='output', required=True, help='Path to output directory. Output filenames are the same as input filenames)')
    parser.add_argument('-f', dest='overwrite', required=False, action='store_true', help='Force overwrite (by default, files will not be overwritten)')
    parser.add_argument('-p', dest='prefix', required=False, help='Output filename prefix, appended to original filename (optional)')
    parser.add_argument('-s', dest='suffix', required=False, help='Output filename suffix, appended to original filename (optional)')

    args = parser.parse_args()

    todo = identify_files_to_process(args)
    batch_watermark(todo, args)
