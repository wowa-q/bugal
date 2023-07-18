# pylint: skip-file
# flake8: noqa
import os
import hashlib
import zipfile
import csv


def read_lines(csv_file):
    with open(csv_file, encoding='ISO-8859-1') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        for row in reader:
            yield row

def get_checksum(csv_file):
    with open(csv_file, encoding='ISO-8859-1') as csvfile:
        checksum = hashlib.md5(csvfile.read().encode('ISO-8859-1')).hexdigest().upper()
        return checksum