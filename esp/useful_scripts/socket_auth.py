#!/usr/bin/python

import sys
import os
import datetime
import traceback
import subprocess

if __name__ == '__main__':
    cur_file = os.path.abspath(__file__)
    django_dir = os.path.abspath(os.path.join(os.path.dirname(cur_file), '..'))
    sys.path.append(django_dir)
    sys.path.append(django_dir + 'esp/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'esp.settings'

from esp import cache_loader
import esp.manage
from esp.users.models import ESPUser

import socket

last_failed = None

def return_(val, conn):
    """ Return the specified return value in the appropriate format """
    if val == True:
        conn.send("true")
        conn.close()
    elif val == False:
        conn.send("false")
        conn.close()
    else:
        conn.send(val)
        conn.close()

def notify_admins(instance, msg):
    print "> notify_admins:"
    print msg,
    rcpts = ['adehnert']
    try:
        cmd = "true zwrite -d -c esp-spew -i".split(' ') + ["socket_auth."+instance] + rcpts
        zwrite = subprocess.Popen(cmd, stdin=subprocess.PIPE, )
        zwrite.communicate(msg)
    except Exception:
        print "Exception in notify_admins:"
        traceback.print_exc()

socket_path = sys.argv[1]

def server(socket_path):
    server_sock = socket.socket(socket.AF_UNIX)
    server_sock.bind(socket_path)
    server_sock.listen(2)
    while True:
        try:
            print ">>> accept()", datetime.datetime.now()
            conn, address = server_sock.accept()
            data = conn.makefile().read()
            args = data.strip().split('\n')
            func, args = args[0], args[1:]
            if func in funcs:
                funcs[func](conn, *args)
            else:
                return_('ERROR_Unknown_Action', conn=conn, )
        except KeyboardInterrupt:
            raise
        except Exception:
            notify_admins('exception', "Exception encountered.\n")
            traceback.print_exc()

def user_exists(conn, username, *args):
    if len(ESPUser.objects.filter(username__iexact=username)[:1]) > 0:
        return_(True, conn=conn,)
    else:
        return_(False, conn=conn, )

def authenticate(conn, username, password, *args):
    global last_failed
    from django.contrib.auth import authenticate
    print ">> Running (authenticate '%s' '[redacted]')" % (username, )
    user = authenticate(username=username, password=password)
    if user is None:
        print "> Result: [failed]  %s" % (user, )
    else:
        print "> Result: [success] '%s' ('%s')" % (user, user.__dict__, )

    if user:
        if last_failed:
            notify_admins("auth.success", "Successfully authenticated '%s'.\nLast failure: '%s' at %s (type: %s)\n" % (username, last_failed['user'], str(last_failed['time']), last_failed['type']))
            last_failed = None
        return_(True, conn=conn,)
    else:
        msg = "Failed to authenticate '%s'\n" % username
        if last_failed:
            msg += "Last failure: '%s' at %s (type: %s)\n" % (last_failed['user'], str(last_failed['time']), last_failed['type'])
        last_failed = {
            'user': username,
            'time': datetime.datetime.now(),
            'type': 'auth-fail',
        }
        notify_admins("auth.fail", msg)
        return_(False, conn=conn,)

def check_userbit(conn, username, qnode, vnode, *args):
    from esp.users.models import UserBit, GetNode
    print ">> Running (check_userbit '%s' '%s')" % (username, vnode, )
    user = ESPUser.objects.get(username=username)
    if UserBit.UserHasPerms(user, GetNode(qnode), GetNode(vnode), recursive_required=True):
        return_(True, conn=conn, )
    else:
        return_(False, conn=conn, )

def finger(conn, username):
    from esp.users.models import UserBit, GetNode
    print ">> Running (finger '%s')" % (username, )
    user = ESPUser.objects.get(username=username)
    ret = "%s\n%s\n%s" % (user.first_name, user.last_name, user.email, )
    return_(ret, conn=conn, )

funcs = {
    'USER EXISTS': user_exists,
    'AUTHENTICATE': authenticate,
    'CHECK USERBIT': check_userbit,
    'FINGER': finger,
}

if __name__ == '__main__':
    server(socket_path)
