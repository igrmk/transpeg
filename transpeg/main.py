#!/usr/bin/python3

import io
import sys
import base64
import os
import argparse
import codecs
import gzip

import svgwrite
from PIL import Image
from PIL import UnidentifiedImageError

__version__ = '1.1.2'


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def to_base64(img, **params):
    stream = io.BytesIO()
    img.save(stream, **params)
    return base64.b64encode(stream.getvalue()).decode('ascii')


def png_mask(mask_img, args):
    if args.mask_colors != 0:
        colors = args.mask_colors
        mask_img = mask_img.convert('P', palette=Image.ADAPTIVE, colors=colors)
    return to_base64(mask_img, format='png', compress_level=9)


def jpeg_mask(mask_img, args):
    quality = args.mask_quality
    return to_base64(mask_img, format='jpeg', optimize=True, quality=quality)


def to_jpeg_and_mask(img, args):
    rgb = img.convert('RGB')
    quality = args.quality
    jpeg_str = to_base64(rgb, format='jpeg', optimize=True, quality=quality)
    mask_img = Image.new("L", img.size)
    mask_img.paste(img.convert('RGBA').split()[-1])
    return jpeg_str, mask_proc[args.mask_type](mask_img, args)


mask_proc = {'png': png_mask, 'jpeg': jpeg_mask}


def main():
    parser = args_parser()
    args = parser.parse_args()
    try:
        with open(args.input, "rb") as file:
            input_bytes = io.BytesIO(file.read())
        img = Image.open(input_bytes, mode='r')
    except FileNotFoundError:
        eprint(f"File not found: '{args.input}'")
        sys.exit(1)
    except UnidentifiedImageError:
        eprint(f"Unknown format: '{args.input}'")
        sys.exit(1)
    except OSError:
        eprint(f"Could not read the image: '{args.input}'")
        sys.exit(1)

    jpeg_str, mask_str = to_jpeg_and_mask(img, args)
    dwg = svgwrite.Drawing(size=img.size)
    mask = dwg.defs.add(dwg.mask(id='mask'))

    href = f'data:image/{args.mask_type};base64,{mask_str}'
    mask.add(dwg.image(href=href, size=img.size))

    href = f'data:image/jpeg;base64,{jpeg_str}'
    dwg.add(dwg.image(href=href, size=img.size, mask='url(#mask)'))

    stream = io.BytesIO()
    write_params = {} if args.svgz else {'pretty': True, 'indent': 4}
    dwg.write(codecs.getwriter('utf-8')(stream), **write_params)
    buf = stream.getbuffer()

    if args.svgz:
        buf = gzip.compress(buf, mtime=0)

    try:
        with open(args.output, 'wb') as f:
            f.write(buf)
    except OSError:
        eprint(f"Could not write the image: '{args.output}'")
        return 1

    eprint(f'JPEG size: {len(jpeg_str)}')
    eprint(f'Mask size: {len(mask_str)}')
    input_size = input_bytes.tell()
    output_size = os.path.getsize(args.output)
    eprint(f'Overall compression ratio: {input_size / output_size :.2f}')


def args_parser():
    def formatter_class(prog):
        return argparse.RawTextHelpFormatter(
            prog,
            max_help_position=30,
            width=80)
    parser = argparse.ArgumentParser(
        formatter_class=formatter_class,
        description=(
            'Convert a transparent image into SVG.\n'
            'The color information is stored as JPEG.\n'
            'The transparency is stored as a greyscale mask.'))
    parser.add_argument(
        'input',
        metavar='INPUT',
        help='input file, usually PNG')
    parser.add_argument(
        'output',
        metavar='OUTPUT',
        help=('output file'))
    parser.add_argument(
        '-m',
        '--mask-type',
        metavar='TYPE',
        help='mask type, either png or jpeg\ndefault is jpeg',
        default='jpeg',
        choices=mask_proc.keys())
    parser.add_argument(
        '-c',
        '--mask-colors',
        metavar='N',
        help=(
            'use a PNG palette with this number of colors for the mask\n'
            'applicable only for PNG masks\n'
            '0 — disable a palette\n'
            'default — 8'),
        default=8,
        type=int)
    parser.add_argument(
        '-q',
        '--quality',
        metavar='Q',
        help='colored JPEG output quality',
        default=75,
        type=int)
    parser.add_argument(
        '-y',
        '--mask-quality',
        metavar='Q',
        help='JPEG mask output quality\napplicable only for JPEG masks',
        default=75,
        type=int)
    parser.add_argument(
        '-z',
        '--svgz',
        dest='svgz',
        action='store_true',
        help='compress with gzip')
    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version=f'%(prog)s {__version__}')
    return parser


if __name__ == "__main__":
    main()
