#!/usr/bin/env python
from parse_qsub import *
from parse_queues import *
import os, sys, json
from common import walltime_to_seconds

def check_nodes(queue_info, pbs_file):
    if not pbs_file.get('nodes'):
        alert_msg = 'No nodes requested'
        alert_type = 'error'
        return {'severity': alert_type, 'msg': alert_msg}

    if queue_info['resources_max.nodect'] < pbs_file['nodes']:
        alert_msg = 'Requested nodes exceeds max allowed (%s)' % queue_info['resources_max.nodect']
        alert_type = 'error'
        return {'severity': alert_type, 'msg': alert_msg}

    return None

def check_ppn(queue_info, pbs_file):
    if not pbs_file.get('ppn'):
        alert_msg = 'No processors requested'
        alert_type = 'error'
        return {'severity': alert_type, 'msg': alert_msg}

    if not pbs_file.get('nodes'):
        return None

    ncpus = pbs_file['nodes'] * pbs_file['ppn']
    if queue_info['resources_max.ncpus'] < ncpus:
        alert_msg = 'Requested cores exceeds max allowed (%s)' % queue_info['resources_max.ncpus']
        alert_type = 'error'
        return {'severity': alert_type, 'msg': alert_msg}

    return None

def check_walltime(queue_info, pbs_file):
    if not pbs_file.get('walltime'):
        alert_msg = 'No walltime requested'
        alert_type = 'error'
        return {'severity': alert_type, 'msg': alert_msg}

    allowed_walltime = walltime_to_seconds(queue_info['resources_max.walltime'])
    if allowed_walltime < pbs_file['walltime']:
        alert_msg = 'Requested walltime exceeds max allowed (%s)' % queue_info['resources_max.walltime']
        alert_type = 'error'
        return {'severity': alert_type, 'msg': alert_msg}
    else:
        return None

def check_contact(queue_info, pbs_file):
    if pbs_file.get('contact'):
        if '@' not in pbs_file['contact']:
            alert_msg = 'Invalid email address supplied for contact: %s' % pbs_file['contact']
            alert_type = 'warning'
            return {'severity': alert_type, 'msg': alert_msg}
        else:
            return None
    else:
        return None

def check_contact_on(queue_info, pbs_file):
    if pbs_file.get('contact_on') and not pbs_file.get('contact'):
        alert_msg = 'No contact address supplied, but contact requested'
        alert_type = 'warning'
        return {'severity': alert_type, 'msg': alert_msg}

    if pbs_file.get('contact_on'):
        contact_str = pbs_file['contact_on']
        valid_contacts = 'abe'
        for i in contact_str:
            if i not in valid_contacts:
                alert_msg = 'Invalid contact_on requested: %s' % i
                alert_type = 'warning'
                return {'severity': alert_type, 'msg': alert_msg}

rules = [
    check_nodes,
    check_ppn,
    check_walltime,
    check_contact,
    check_contact_on
]

def print_alerts(infile, alerts):
    print "\nEvaluating PBS Script %s\n---------------------------------" % infile
    for a in alerts:
        if a['severity'] == 'error':
            print " ! - %s" % a['msg']
    for a in alerts:
        if a['severity'] == 'warning':
            print " * - %s" % a['msg']
    for a in alerts:
        if a['severity'] == 'info':
            print " ? - %s" % a['msg']

    print "\nPlease correct these errors and re-evaluate\n"

def main():
    try:
        infile = sys.argv[1]
        if not os.path.isfile(infile):
            raise
    except:
        print '\nPlease call with the path to a qsub file'

    queues = parse_queues()
    pbs_file = parse_qsub(infile)

    try:
        queue = queues[pbs_file['queue']]
    except:
        print 'Queue not defined, using normal'
        queue = queues['normal']

    report = []

    for rule in rules:
        try:
            alert = rule(queue, pbs_file)
            if alert:
                report.append(alert)
        except:
            pass

    if len(report) > 0:
        print_alerts(infile, report)
    else:
        print "\nNo problems detected"


if __name__ == '__main__':
    main()