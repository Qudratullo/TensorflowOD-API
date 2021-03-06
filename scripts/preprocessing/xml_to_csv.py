"""
Usage:
# Create train data:
python xml_to_csv.py -i [PATH_TO_IMAGES_FOLDER]/train -o [PATH_TO_ANNOTATIONS_FOLDER]/train_labels.csv

# Create test data:
python xml_to_csv.py -i [PATH_TO_IMAGES_FOLDER]/test -o [PATH_TO_ANNOTATIONS_FOLDER]/test_labels.csv
"""

import os
import glob
import pandas as pd
import argparse
from os import listdir
import numpy as np
import cv2
import xml.etree.ElementTree as ET


def xml_to_csv(path, k):
    """Iterates through all .xml files (generated by labelImg) in a given directory and combines them in a single Pandas datagrame.

    Parameters:
    ----------
    path : {str}
        The path containing the .xml files
    Returns
    -------
    Pandas DataFrame
        The produced dataframe
    """

    xml_list = []
    for xml_file in glob.glob(path + '/*.xml'):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for member in root.findall('object'):
            value = (root.find('filename').text,
                     int(root.find('size')[0].text) // k,
                     int(root.find('size')[1].text) // k,
                     member[0].text,
                     int(member[4][0].text) // k,
                     int(member[4][1].text) // k,
                     int(member[4][2].text) // k,
                     int(member[4][3].text) // k
                     )
            xml_list.append(value)
    column_name = ['filename', 'width', 'height',
                   'class', 'xmin', 'ymin', 'xmax', 'ymax']
    xml_df = pd.DataFrame(xml_list, columns=column_name)
    return xml_df


def compress_images(image_dir, k):
    for filename in listdir(image_dir):
        if filename[-3:] != "jpg":
            continue
        print(image_dir + filename)
        img = cv2.imread(image_dir + filename)
        width = int(img.shape[1] / k)
        height = int(img.shape[0] / k)
        dim = (width, height)
        img = cv2.resize(img, dim)

        img_path = image_dir + filename
        cv2.imwrite(img_path, img)


def main():
    # Initiate argument parser
    parser = argparse.ArgumentParser(
        description="Sample TensorFlow XML-to-CSV converter")
    parser.add_argument("-i",
                        "--inputDir",
                        help="Path to the folder where the input .xml files are stored",
                        type=str)
    parser.add_argument("-o",
                        "--outputFile",
                        help="Name of output .csv file (including path)", type=str)

    parser.add_argument("--kCompressImage",
                        help="Coefficient of compress image", type=int)

    args = parser.parse_args()

    if args.inputDir is None:
        args.inputDir = os.getcwd()
    if args.outputFile is None:
        args.outputFile = args.inputDir + "/labels.csv"
    if args.kCompressImage is None:
        args.kCompressImage = 1

    assert (os.path.isdir(args.inputDir))

    xml_df = xml_to_csv(args.inputDir, args.kCompressImage)
    xml_df.to_csv(
        args.outputFile, index=None)
    print('Successfully converted xml to csv.')

    compress_images(args.inputDir, args.kCompressImage)
    print('Successfully compressed images.')


if __name__ == '__main__':
    main()
