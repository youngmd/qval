#!/usr/bin/env python
import json
import subprocess
import config

def isfloat(x):
    try:
        a = float(x)
    except ValueError:
        return False
    else:
        return True

def isint(x):
    try:
        a = float(x)
        b = int(a)
    except ValueError:
        return False
    else:
        return a == b

def parse_queues():
    qinfo = subprocess.check_output(config.qstat_cmd.split())

    qinfo = qinfo.splitlines()

    queues = {}
    host_counting = False

    for l in qinfo:
        l = l.strip()
        if l.startswith('Queue:'):
            q = l.split()[1]
            queues[q] = {}
            queues[q]['acl_hosts'] = []
        if host_counting and '=' not in l:
            queues[q]['acl_hosts'].extend(l.rstrip(',').split(','))
        if host_counting and '=' in l:
            queues[q]['hostcnt'] = len(queues[q]['acl_hosts'])
            host_counting = False
        if l.startswith('acl_hosts'):
            host_counting = True
            queues[q]['acl_hosts'] = l.split('=')[1].rstrip(',').split(',')
        if not host_counting and '=' in l:
            key,val = l.split('=')

            val = val.strip()
            if isint(val):
                val = int(val)
            elif isfloat(val):
                val = float(val)

            queues[q][key.strip()] = val

    return queues

if __name__ == '__main__':
    q = parse_queues()
    print json.dumps(q)