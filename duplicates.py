#!/usr/bin/env python3
import os, hashlib, sys

def md5hash_dict(base_path):
    '''Builds a dict mapping the md5 hash of files in path (recursively searched) to filenames of duplicates'''
    if not os.path.exists(base_path) :
        print("Error: {} is not an exising path".format(base_path))
        exit(1)
    hashmap = {}
    print("Building md5 hashes of files (this may take a while)")
    for (dirpath, dirnames, filenames) in os.walk(base_path) :
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
                print("Can't open {}".format(os.path.abspath(fullname)))
                continue
    return hashmap

def output_duplicates(hashmap, output=None) :
    if not output or output is sys.stdout:
        output = sys.stdout
        _printer(hashmap, output)
    else:
        with open(output, "w") as f:
            _printer(hashmap, f)

def _printer(hashmap, out) :
    for (k, v) in hashmap.items() :
        if len(v) > 1 :
            print('Duplicates: ', v, file=out)

def _print_usage(args) :
    (_, script_name) = os.path.split(args[0])
    print("\nUsage: {} search_directory [output_filename]\n".format(script_name))
    print(script_name, " searches search_directory and all subdirectories for files with duplicate contents.")
    print("Defaults to printing to stdout if no output file is given.")

if __name__ == "__main__" :
    if not (len(sys.argv) == 2 or len(sys.argv) == 3) :
        _print_usage(sys.argv)
        exit(1)

    if len(sys.argv) == 3 and os.path.isfile(sys.argv[2]) :
        answer = input("File {} exists and will be overwritten: continue? (y/N)".format(sys.argv[2]))
        while answer not in "yYnN" :
            answer = input("Please enter y/n:")
        if answer in "nN" :
            print("Got N, exiting")
            exit(0)

    h=md5hash_dict(sys.argv[1])
    if len(sys.argv) == 3:
        output_duplicates(h, sys.argv[2])
        print("Done.  Duplicates located in {}".format(sys.argv[2]))
    else :
        print("No output file given.  Printing duplicates to stdout.")
        output_duplicates(h, sys.stdout)
        print("Done.")
