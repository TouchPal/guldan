# -*- coding: utf-8 -*-
import argparse
import sys

from pip.utils import get_installed_distributions


def main():
    parser = argparse.ArgumentParser(description="Read all installed packages from sys.path and list licenses.")
    args = parser.parse_args()

    meta_files_to_check = ['PKG-INFO', 'METADATA']

    for installed_distribution in get_installed_distributions():
        found_license = False
        for metafile in meta_files_to_check:
            if not installed_distribution.has_metadata(metafile):
                continue
            for line in installed_distribution.get_metadata_lines(metafile):
                if 'License: ' in line:
                    (k, v) = line.split(': ', 1)
                    sys.stdout.write("{project_name}: {license}\n".format(
                        project_name=installed_distribution.project_name,
                        license=v))
                    found_license = True
        if not found_license:
            sys.stdout.write("{project_name}: Found no license information.\n".format(
                project_name=installed_distribution.project_name))

if __name__ == "__main__":
    main()