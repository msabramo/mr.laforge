from supervisor.options import ClientOptions
from supervisor.xmlrpc import SupervisorTransport
import os
import socket
import subprocess
import sys
import time
import xmlrpclib


def get_rpc(options):
    transport = SupervisorTransport(
        options.username,
        options.password,
        options.serverurl)
    return xmlrpclib.ServerProxy('http://127.0.0.1', transport)


def up():
    options = ClientOptions()
    options.realize()
    status = "init"
    while 1:
        try:
            rpc = get_rpc(options)
            rpc.supervisor.getPID()
            if status == 'shutdown':
                sys.stderr.write("\n")
            break
        except socket.error:
            if status == 'shutdown':
                sys.stderr.write("\n")
            sys.stderr.write("Starting supervisord\n")
            configfile = os.path.join(os.getcwd(), options.configfile)
            retcode = subprocess.call(["./bin/supervisord", "-c", configfile])
            if retcode != 0:
                sys.exit(retcode)
            status = 'starting'
        except xmlrpclib.Fault as e:
            if e.faultString == 'SHUTDOWN_STATE':
                if status == 'init':
                    sys.stderr.write("Supervisor currently shutting down ")
                    sys.stderr.flush()
                    status = 'shutdown'
                else:
                    sys.stderr.write(".")
                    sys.stderr.flush()
                time.sleep(1)
