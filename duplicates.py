#!/usr/bin/env python3
import os, hashlib, sys, argparse
from collections import defaultdict
'''Searches and finds a list of files which are duplicates in content (but not necessarily filename) in user specified directories.'''

'''Options I'd like to add:
   - Finer control over descending into subdirs, symlinks
   - Printing options: compact printing (1 set of duplicates per line, useful for sort) vs pretty printing (one file per line, for example
   - Figure out if we can increase performance -- still slowish on big dirs'''


def main():
    parser = _make_parser()
    args = parser.parse_args()
    output = _check_output(args.output_filename)     #Want to call _check_output() before find_duplicates() because 
    h=find_duplicates(args.input_dirs, args.verbose) #user can cancel in _check_output() if s/he would overwrite something important
    output_duplicates(h, output, args.verbose)
   

def find_duplicates(base_paths, verbose=False) :
    '''Searches over dirs in base_paths (and their subdirs) to group files with equivalent contents 
    into a dict {search criterion(md5hash) : [filelist] } to filenames'''
    sizemap=_build_size_dict(base_paths, verbose)
    return _md5hash_dict(sizemap, verbose)


def _md5hash_dict(sizemap, verbose=False) :
    '''Builds a dict mapping the md5 hash of files in path (recursively searched) to filenames of duplicates.
    sizemap is assumed to be a dict mapping { initial_criterion : [list of duplicate candidates] }'''
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
                print("Warning: Can't open {}".format(os.path.abspath(fullname)), file=sys.stderr)
                continue #Just skip files we can't open
    hashmap=_purge(hashmap)
    return hashmap


def _build_size_dict(base_paths, verbose=False) :
    '''Builds a dictionary mapping {file size in bytes : list of files with that filesize},
    ignoring size 0 files, and only returning those that have duplicates.''' 
    try:
        _check_paths(base_paths)
    except OSError:
        print("Error: Bad input directory or directories. Cannot continue.", file=sys.stderr)
        exit(1)
    sizemap=defaultdict(list)
    if verbose :
        print("Creating candidates for duplicates based on filesize")
    #Maybe: Write this as generator/comprehension? Would be less readable nested this deep
    for base_path in base_paths :
        for (dirpath, _ , filenames) in os.walk(base_path) :
            for filename in filenames :
                fullname = os.path.join(dirpath, filename)
                try:
                    sz = os.path.getsize(fullname)
                except OSError:
                    print("Skipping file: couldn't get filesize of {}".format(fullname))
                    continue
                if sz > 0 :
                    sizemap[sz].append(fullname)
    sizemap=_purge(sizemap) #Consider inlining _purge so sizemap doesn't have to get passed around
    if verbose :
        print("Found {} unique filesizes that are duplicate candidates.".format(len(sizemap)))
    return sizemap


def _purge(search_map) :
    '''Takes a dict {search criterion : [filelist]} and removes (k,v) pairs with len(v) <= 1,
    i.e. those without duplicates. Sorts individual filelists for easier reading'''
    to_delete=set() #Can't operate on the dict as we iterate over it
    for (s, filelist) in search_map.items() :
        if len(filelist) <= 1 :
            to_delete.add(s)
        else :
            filelist.sort()
    for n in to_delete :
        del search_map[n]
    return search_map


def _make_parser() :
    '''Command line parser'''
    parser = argparse.ArgumentParser(description="Searches directory and its subdirectories for files with duplicate contents, optionally writing out duplicates to either a text file or stdout")
    parser.add_argument('-o', '--output', help='optional output text file', nargs='?',  default=sys.stdout, dest="output_filename")
    parser.add_argument("input_dirs", nargs='+', help='Input directories to be search, separated by whitespace.  Note that subdirectories are searched')
    parser.add_argument('-v', '--verbose', help='Increase verbosity', action='store_true', default=False)
    return parser


def output_duplicates(hashmap, output=sys.stdout, verbose=False) :
    '''Simple printer function that takes a dict {search_criteria : [files]}, and prints the files which have duplicates.  If verbose, will print duplicates to both stdout and the output file, if they're different.'''
    _printer(hashmap, output)
    if not output is sys.stdout and verbose :
        _printer(hashmap, sys.stdout)
    print("\nFound {} unique files with at least 1 duplicate.".format(len(hashmap)))
    if not output is sys.stdout :
        print("It may be helpful to run 'sort {} > some_new_output.txt' ".format(output.name))


def _printer(d, out) :
    for (k, v) in d.items() :
        print('[ ', file=out, end=" ")
        for f in v : 
            print(f, file=out, end=" ")
        print(']', file=out)


def _check_paths(paths) :
    '''Input sanitization on input paths: checks all paths, and throws an exception if any fail'''
    paths_ok=True
    for path in paths :
        if not os.path.exists(path) :
            print("Error: {} is not an existing path".format(path), file=sys.stderr)
            paths_ok=False
    if not paths_ok :
        raise OSError("Couldn't open some input directories")
    return paths_ok


def _check_output(out) :
    '''Takes out to either be sys.stdout, or a filename of a text file to write to.  Ensures user doesn't accidentally overwrite something they want to keep.  Returns an appropriate output file handle if possible'''
    #TODO: Too coupled?
    if out is sys.stdout :
        return out
    if os.path.exists(out) :
        answer = input("Output file {} exists and will be overwritten: continue? (y/N)".format(out))
        while answer not in "yYnN" :
            answer = input("Please enter y/n:")
        if answer in "nN" :
            print("Got {}, exiting".format(answer))
            exit(0)
    try:
        f=open(out, 'w')
    except PermissionError :
        print("Error: Couldn't write to {}. Check that you have write permissions.".format(out), file=sys.stderr)
        exit(1)
    except :
        print("Error: Unknown error in opening {}".format(out), file=sys.stderr)
        exit(1)
    return f


if __name__ == "__main__" :
    main()
