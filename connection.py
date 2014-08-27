#!/usr/bin/env python

import base64
from binascii import hexlify
import getpass
import os
import select
import socket
import sys
import time
import traceback
import paramiko
from paramiko.py3compat import input
from paramiko.py3compat import u
import getpass
# Import conn Lib
from record import record_videos


# windows does not have termios...
try:
    import termios
    import tty
    has_termios = True
except ImportError:
    has_termios = False

def agent_auth(transport, username):
    """
    Attempt to authenticate to the given transport using any of the private
    keys available from an SSH agent.
    """
    
    agent = paramiko.Agent()
    agent_keys = agent.get_keys()
    if len(agent_keys) == 0:
        return
        
    for key in agent_keys:
        print('Trying ssh-agent key %s' % hexlify(key.get_fingerprint()))
        try:
            transport.auth_publickey(username, key)
            print('... success!')
            return
        except paramiko.SSHException:
            print('... nope.')


def manual_auth(username, hostname):
    try:
        default_path = os.path.join(os.environ['HOME'], '.ssh', 'id_rsa')
        path = default_path
        try:
            key = paramiko.RSAKey.from_private_key_file(path)
        except paramiko.PasswordRequiredException:
            password = getpass.getpass('RSA key password: ')
            key = paramiko.RSAKey.from_private_key_file(path, password)
        t.auth_publickey(username, key)
    except IOError:
        default_path = os.path.join(os.environ['HOME'], '.ssh', 'id_dsa')
        path = default_path
        try:
            key = paramiko.DSSKey.from_private_key_file(path)
        except paramiko.PasswordRequiredException:
            password = getpass.getpass('DSS key password: ')
            key = paramiko.DSSKey.from_private_key_file(path, password)
        t.auth_publickey(username, key)
    #except paramiko.AuthenticationException as e:
    except:
        pw = getpass.getpass('Password for %s@%s: ' % (username, hostname))
        try:
            t.auth_password(username, pw)
        except (paramiko.AuthenticationException, KeyboardInterrupt) as error:
            print 'Permission denied, Authentication Error'


username = getpass.getuser()
if len(sys.argv) > 1:
    hostname = sys.argv[1]
    if hostname.find('@') >= 0:
        username, hostname = hostname.split('@')
else:
    hostname = input('Hostname: ')
if len(hostname) == 0:
    print('*** Hostname required.')
    sys.exit(1)
port = 22
if hostname.find(':') >= 0:
    hostname, portstr = hostname.split(':')
    port = int(portstr)

# now connect
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((hostname, port))
except Exception as e:
    print('*** Connect failed: ' + str(e))
    sys.exit(1)


def posix_shell(chan):
    import select
    record = [] 

    oldtty = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin.fileno())
        tty.setcbreak(sys.stdin.fileno())
        chan.settimeout(0.0)


        # needs to be sent to give vim correct size FIX
        chan.send('eval $(resize)\n')


        day =time.strftime('%Y%m%d')
        reduce_log = open('logs/%s-%s-%s.log' % (day, hostname, username), 'a')
        detail_log = open('logs/%s-%s-%s-detail.log' % (day, hostname, username), 'a')
        while True:
            date =time.strftime('%Y-%m-%d %H:%M:%S')
            r, w, e = select.select([chan, sys.stdin], [], [])
            if chan in r:
                try:
                    x = u(chan.recv(1024))
                    if len(x) == 0:
                        sys.stdout.write('\r\n*** EOF\r\n')
                        break
                    sys.stdout.write(x)
                    sys.stdout.flush()
                except socket.timeout:
                    pass
                
                detail_log.write('%s' % x.encode('utf8'))
                detail_log.flush()

            if sys.stdin in r:
                #x = sys.stdin.read(1)
                # history command
                x = os.read(sys.stdin.fileno(), 1)
                if len(x) == 0:
                    break

                # conn record ...
                record.append(x)
                if x == '\b':
                    try:
                        record.pop()
                        record.pop()
                    except IndexError:
                        pass
                    #print record,'-'
                if x == '\r':
                    cmd = ''.join(record).split('\r')[-2]
                    if len(cmd) != 0:
                        reduce_log.write('%s\t%s\t%s\t%s\n' % (date, 'hh-b2c-miorder-backend-web01.bj', 'root', cmd))
                        reduce_log.flush()
                        #print record,'-'
                        record = []
                chan.send(x)

        reduce_log.close()
        detail_log.close()

    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)


try:
    t = paramiko.Transport(sock)
    try:
        t.start_client()
    except paramiko.SSHException:
        print('*** SSH negotiation failed.')
        sys.exit(1)

    try:
        keys = paramiko.util.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
    except IOError:
        try:
            keys = paramiko.util.load_host_keys(os.path.expanduser('~/ssh/known_hosts'))
        except IOError:
            print('*** Unable to open host keys file')
            keys = {}

    # check server's host key -- this is important.
    key = t.get_remote_server_key()
    if hostname not in keys:
        print('*** WARNING: Unknown host key!')
    elif key.get_name() not in keys[hostname]:
        print('*** WARNING: Unknown host key!')
    elif keys[hostname][key.get_name()] != key:
        print('*** WARNING: Host key has changed!!!')
        sys.exit(1)
    else:
        print('*** Host key OK.')

    # get username
    if username == '':
        default_username = getpass.getuser()
        username = input('Username [%s]: ' % default_username)
        if len(username) == 0:
            username = default_username

    agent_auth(t, username)
    if not t.is_authenticated():
        manual_auth(username, hostname)
    if not t.is_authenticated():
        print('*** Authentication failed. :(')
        t.close()
        sys.exit(1)

    chan = t.open_session()
    chan.get_pty()
    chan.invoke_shell()
    print('*** Here we go!\n')

    #interactive.interactive_shell(chan)
    posix_shell(chan)
    chan.close()
    t.close()

except Exception as e:
    print('*** Caught exception: ' + str(e.__class__) + ': ' + str(e))
    traceback.print_exc()
    try:
        t.close()
    except:
        pass
    sys.exit(1)


