#!/usr/bin/env python3
import os, hashlib, sys
import argparse

def main():
    parser = _make_parser()
    args = parser.parse_args()
    output = _check_output(args.output_filename)
    h=md5hash_dict(args.input_dirs, args.verbose)
    output_duplicates(h, output, args.verbose)
    #output.close()
   

def md5hash_dict(base_paths, verbose=False) :
    '''Builds a dict mapping the md5 hash of files in path (recursively searched) to filenames of duplicates'''
    #TODO: Speed this up massively.  Maybe try using os.stat to build dictionary of files with same size, then compare md5 hashes of files within size classes. Reading input takes a huge % of time, with md5hash not far behind.
    if not _check_paths(base_paths) :
        exit(1)
    if verbose :
        print("Building md5 hashes of files (this may take a while)")
    hashmap = {}
    for base_path in base_paths :
        for (dirpath, dirnames, filenames) in os.walk(base_path) :
            if verbose :
                print("On directory ", dirpath)
            for filename in filenames :
                fullname = os.path.join(dirpath, filename)
                try:
                    with open(fullname, 'rb') as f :
                        d = f.read()
                    h = hashlib.md5(d).hexdigest()
                    filelist = hashmap.setdefault(h, [])
                    filelist.append(fullname)
                except OSError:
                    #TODO: if verbose on this line or not?  Probably better to leave it...
                    print("Can't open {}".format(os.path.abspath(fullname)))
                    continue
    return hashmap


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
    print("\nFound {} unique files with at least 1 duplicate".format(count))



def _check_paths(paths) :
    paths_ok=True
    for path in paths :
        if not os.path.exists(path) :
            print("Error: {} is not an existing path".format(base_path))
            paths_ok=False
    return paths_ok


def _check_output(out) :
    if out is sys.stdout :
        return out
    if os.path.exists(out) :
        answer = input("Output file {} exists and will be overwritten: continue? (y/N)".format(out))
        while answer not in "yYnN" :
            answer = input("Please enter y/n:")
        if answer in "nN" :
            print("Got {}, exiting".format(answer))
            exit(1)
    f=open(out, 'w')
    return f


if __name__ == "__main__" :
    main()
