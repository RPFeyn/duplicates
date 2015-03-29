#!/usr/bin/env python3
import os, hashlib, sys
import argparse
from collections import defaultdict

#TODO: Refactor main algorithm (building of maps, filtering sizemap, etc) so functions are more single purpose
def main():
    parser = _make_parser()
    args = parser.parse_args()
    output = _check_output(args.output_filename)
    h=md5hash_dict(args.input_dirs, args.verbose)
    output_duplicates(h, output, args.verbose)
    #output.close()
   

def md5hash_dict(base_paths, verbose=False) :
    '''Builds a dict mapping the md5 hash of files in path (recursively searched) to filenames of duplicates'''
    if not _check_paths(base_paths) :
        exit(1)
    sizemap = _build_size_dict(base_paths, verbose)
    if verbose :
        print("Building md5 hashes of files (this may take a while)")
    hashmap = defaultdict(list)
    for (_, filenames) in sizemap.items() :
        for fullname in filenames :
            try :
                with open(fullname, 'rb') as f:
                    d=f.read()
                h=hashlib.md5(d).hexdigest()
                hashmap[h].append(fullname)
            except OSError:
                print("Can't open {}".format(os.path.abspath(fullname)))
                continue
    return hashmap


def _build_size_dict(base_paths, verbose=False) :
    '''Builds a dictionary mapping {file size in bytes : list of files with that filesize}, ignoring size 0 files, and only returning those that have duplicates'''
    #NOTE: Assumes paths have already been checked by _check_paths.  In normal operation this has been done in md5hash_dict
    #TODO: Change above behavior? Probably need to refactor
    sizemap=defaultdict(list)
    if verbose :
        print("Creating candidates for duplicates based on filesize")
    for base_path in base_paths :
        for (dirpath, dirnames, filenames) in os.walk(base_path) :
            for filename in filenames :
                fullname = os.path.join(dirpath, filename)
                try:
                    sz = os.path.getsize(fullname)
                except OSError:
                    print("Skipping file: couldn't get filesize of {}".format(fullname))
                    continue
                if sz > 0 :
                    sizemap[sz].append(fullname)
    to_delete=set()
    for (n_bytes, filelist) in sizemap.items() :
        if len(filelist) <= 1 :
            to_delete.add(n_bytes)
    for n in to_delete:
        del sizemap[n]
    if verbose :
        print("Found {} unique filesizes that are duplicate candidates.".format(len(sizemap)))
    return sizemap


def _make_parser() :
    parser = argparse.ArgumentParser(description="Searches directory and its subdirectories for files with duplicate contents, optionally writing out duplicates to either a text file or stdout")
    parser.add_argument('-o', '--output', help='optional output text file', nargs='?',  default=sys.stdout, dest="output_filename")
    parser.add_argument("input_dirs", nargs='+', help='Input directories to be search, separated by whitespace.  Note that subdirectories are searched')
    parser.add_argument('-v', '--verbose', help='Increase verbosity', action='store_true', default=False)
    return parser



def output_duplicates(hashmap, output=sys.stdout, verbose=False) :
    count = 0
    for (k, v) in hashmap.items() :
        if len(v) > 1 :
            count += 1
            print('Duplicates: ', v, file=output)
            if not output is sys.stdout and verbose :
                print('Duplicates: ', v, file=sys.stdout)
    print("\nFound {} unique files with at least 1 duplicate.".format(count))
    if not output is sys.stdout :
        print("On a unix-like system, it may be helpful to run 'sort {} > some_new_output.txt'".format(output.name))


def _check_paths(paths) :
    paths_ok=True
    for path in paths :
        if not os.path.exists(path) :
            print("Error: {} is not an existing path".format(base_path))
            paths_ok=False
    return paths_ok


def _check_output(out) :
    #TODO: This is a mess
    if out is sys.stdout :
        return out
    if os.path.exists(out) :
        answer = input("Output file {} exists and will be overwritten: continue? (y/N)".format(out))
        while answer not in "yYnN" :
            answer = input("Please enter y/n:")
        if answer in "nN" :
            print("Got {}, exiting".format(answer))
            exit(1)
    try:
        f=open(out, 'w')
    except PermissionError :
        print("Permission error, couldn't write to {}.  Check that you have write permissions.".format(out))
        exit(1)
    except :
        print("Unknown error in opening {}".format(out))
        exit(1)
    return f


if __name__ == "__main__" :
    main()
