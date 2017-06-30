def walltime_to_seconds(walltime):
    try:
        if ':' not in walltime:
            return int(walltime)
        else:
            vals = walltime.split(':')
            vals = map(int, vals)
            if walltime.count(':') == 3:
                return vals[0] * 86400 + vals[1] * 3600 + vals[2] * 60 + vals[3]
            if walltime.count(':') == 2:
                return vals[0] * 3600 + vals[1] * 60 + vals[2]
            if walltime.count(':') == 1:
                return vals[0] * 60 + vals[1]
    except:
        return False