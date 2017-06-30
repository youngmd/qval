#!/usr/bin/env python
import os, sys
import json
from common import walltime_to_seconds

PBS_cmds = {
    '-M' : 'contact',
    '-N' : 'jobname',
    '-j' : 'join_out_err',
    '-m' : 'contact_on',
    '-q' : 'queue',
    '-e' : 'error_log',
    '-o' : 'output_log',
    '-r' : 'rerunnable',
    '-a' : 'eligible_at',
    '-V' : 'export_all',
    '-c' : 'checkpointing',
    '-t' : 'job_array'
    }


def parse_l(qsub_dict, line):
    vals = line.split(',')
    for val in vals:
        if val.startswith('nodes'):
            if ':' in val:
                va = val.split(':')
                for v in va:
                    t = v.split('=')
                    qsub_dict[t[0]] = int(t[1])
        else:
            qsub_dict[val.split('=')[0]] = val.split('=')[1]

    if qsub_dict.get('walltime'):
        qsub_dict['walltime'] = walltime_to_seconds(qsub_dict['walltime'])

    return qsub_dict

def parse_qsub(infile):
    qsub = {}
    try:
        f = open(infile, 'r')
        lines = f.readlines()
        f.close()
    except:
        print "Could not read any lines from %s" % infile
        return False

    for l in lines:
        if not l.startswith('#PBS'):
            continue
        vals = l.split()
        if PBS_cmds.get(vals[1]):
            qsub[PBS_cmds[vals[1]]] = vals[2]
        elif vals[1] == '-l':
            qsub = parse_l(qsub, vals[2])

    return qsub

def main():
    try:
        infile = sys.argv[1]
        if not os.path.isfile(infile):
            raise
    except:
        print '\nPlease call with the path to a qsub file'

    print json.dumps(parse_qsub(infile))

if __name__ == '__main__':
    main()