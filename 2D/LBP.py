#!/usr/bin/python
# -*- coding: utf-8 -*-
import array

from gimpfu import *


def lbp_histogram_create_1_plugin_main(image, drawable):
    bpp = drawable.bpp
    (bx1, by1, bx2, by2) = drawable.mask_bounds
    width = bx2 - bx1
    height = by2 - by1

    (ox, oy) = drawable.offsets

    src_rgn = drawable.get_pixel_rgn(bx1, by1, width, height, False, False)
    src_pixels = array.array("B", src_rgn[bx1:bx2, by1:by2])
    mode_dict = {1: GRAY_IMAGE, 2: GRAYA_IMAGE, 3: RGB_IMAGE, 4: RGBA_IMAGE}

    layer = gimp.Layer(image, "LBP transformed", width, height, mode_dict[bpp], 100, NORMAL_MODE)
    layer.set_offsets(bx1 + ox, by1 + oy)

    dst_rgn = layer.get_pixel_rgn(0, 0, width, height, TRUE, TRUE)
    dst_pixels = array.array("B", dst_rgn[0:width, 0:height])

    image.add_layer(layer, 0)
    gimp.progress_init('applying local binary pattern filter')

    pict = [[0] * width for i in range(0, height)]

    # convert image to grayscale
    for y in range(0, height):
        for x in range(0, width):
            pos = (y * width + x) * bpp
            pict[y][x] = convert_to_grayscale(bpp, src_pixels[pos:(pos+bpp)])

    for y in range(0, height):
        for x in range(0, width):
            pos = (y * width + x) * bpp
            center_pixel_value = pict[y][x]
            neighbours = []

            # compute neigbours' values                              
            for y_n in range(-1, 2):
                for x_n in range(-1, 2):
                    res = 0
                    try:
                        res = pict[y + y_n][x + x_n]
                        # if the index is out of range, use max value instead
                        if y + y_n < 0 or x + x_n < 0:
                            res = 255
                    except IndexError:
                        res = 255
                        pass
                    finally:
                        neighbours.append(res)

            tmp = get_resulting_center_pixel(neighbours, center_pixel_value, bpp)
            for p in range(0, bpp):
                dst_pixels[pos + p] = tmp[p]

            gimp.progress_update(float(y + 1) / height)

    dst_rgn[0:width, 0:height] = dst_pixels.tostring()
    layer.flush()
    layer.merge_shadow(True)
    layer.update(0, 0, width, height)
    gimp.displays_flush()


def get_resulting_center_pixel(neighbours, my_val, bpp):
    res_indices = [0, 1, 2, 5, 8, 7, 6, 3]
    lbp = [0 if neighbours[x] < my_val else 1 for x in res_indices]
    result = []
    nbr = 0

    for power in range(7, -1, -1):
        nbr += (2 ** power) * lbp[7 - power]

    if bpp % 2 == 0:
        for unused in range(1, bpp):
            result.append(nbr)
        result.append(255)
    else:
        for unused in range(1, bpp + 1):
            result.append(nbr)

    return result


def convert_to_grayscale(bpp, data):
    if bpp > 2:
        value = 0.2126 * data[0] + 0.7152 * data[1] + 0.0722 * data[2]
    else:
        value = data[0]
    return int(round(value))


register(
        "lbp-histogram-create",
        "Vytvoreni LBP histogramu.",
        "Vytvoreni LBP histogramu.",
        "Gabriela Havranova",
        "Gabriela Havranova",
        "2021",
        "<Image>/_Image/Create LBP histogram",
        "RGB*, GRAY*",
        [],
        [],
        lbp_histogram_create_1_plugin_main)
main()
