#!/usr/bin/env python

from subprocess import check_output
import sys

def get_merged_branches_by_change_id():
    '''a list of merged branches, by change id excluding support branches and master'''
    raw_changeIds = check_output('git log origin/master | grep -i change-id | awk {\' print $2 \'}', shell=True)
    changeIds = [b.strip() for b in raw_changeIds.split('\n') if b.strip()]
    raw_branches = check_output('git branch -a', shell=True)
    branches = [b.strip() for b in raw_branches.split('\n')
        if b.strip() and not b.startswith('*') and \
            not b.strip().startswith('onos') and not b.strip().startswith('remotes') and b.strip() != 'master']
    to_delete = []
    for branch in branches:
        raw_local_change_ids = check_output('git show %s | grep -i change-id | awk {\' print $2 \'}' % branch, shell=True)
        local_change_ids = [ b.strip() for b in raw_local_change_ids.split('\n') if b.strip() ]
        for local_change_id in local_change_ids:
            if local_change_id in changeIds and branch not in to_delete:
                to_delete.append(branch)

    return to_delete


def delete_branch(branch):
    return check_output('git branch -D %s' % branch, shell=True).strip()


if __name__ == '__main__':
    dry_run = '--confirm' not in sys.argv
    one_by_one = '--one-by-one' in sys.argv
    to_delete = get_merged_branches_by_change_id()
    if len(to_delete) == 0:
        print "Nothing to clean"
        sys.exit(0)
    for branch in to_delete:
        if dry_run:
            print branch
        else:
            if one_by_one:
                print 'Do you want to delete branch %s [y/N]' % branch
                ans = raw_input()
                if ans == 'y' or ans == 'Y':
                    print delete_branch(branch)
            else:
                    print delete_branch(branch)
    
    if dry_run:
        print '*****************************************************************'
        print 'Did not actually delete anything yet, pass in --confirm to delete'
        print 
