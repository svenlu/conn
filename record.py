#!/usr/bin/env python
import os, sys, time

class Record(object):
    def __init__(self, hostname=None, user='root', password=None, port=22):
         self.hostname = hostname
         self.password = password
         self.user = user
         self.port = port

    def logs(self, *args):
        current_time = time.strftime('%Y%m%d-%H:%M:%S')
        logs_dir = '.logs'
        logs_file = '%s/%s-%s-%s' % (logs_dir, current_time, 'web01', 'root')
        if not os.path.isdir(logs_dir): os.mkdir(logs_dir)
        with open(logs_file) as f:
            f.write(11111)
            f.flush()
        #if os.path.isfile('%s/%s' % logs_dir, logs_file):


    def videos(self):
        current_time = time.strftime('%Y%m%d%H%M%S')
        file_name = '%s-%s-%s' % (current_time, self.hostname, self.user)
        cmd = './script -t 2> %s.time -a %s.his -c "python connection.py %s@%s:%d"' % (file_name, file_name, self.user, self.hostname, self.port)
        print cmd
        #os.system(cmd)

def record_videos(func):
    def info(username='root', hostname=None, port=22):
        #print hostname, username, port, '-----------'
        current_time = time.strftime('%Y%m%d%H%M%S')
        file_name = '%s-%s-%s' % (current_time, hostname, username)
        cmd = './script -t 2> videos/%s.time -a videos/%s.his -c "python connection.py %s@%s:%d"' % (file_name, file_name, username, hostname, port)
        #result = func(cmd)
        #print cmd
        os.system(cmd)
    return info
