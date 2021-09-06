"""Module to perform libvirtd related operations"""

from time import time
import paramiko
import subprocess as sp

SSH_PORT = 22
service_name = "libvirtd.service"

"""
Get ssh connection
:param str hostname: the server to connect to
None means localhost
:param int port: the server port to connect to
:param str username:
    the username to authenticate as (defaults to the current local
    username)
:param str password:Used for password authentication
:raises:
    `.BadHostKeyException` -- if the server's host key could not be
    verified
    :raises: `.AuthenticationException` -- if authentication failed
    :raises:
    `.SSHException` -- if there was any other error connecting or
    establishing an SSH session
    :raises socket.error: if a socket error occurred while connecting

"""
def get_ssh_connection(hostname,port=SSH_PORT,username=None,password=None):
    if None == hostname:
        return None
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname,port,username=username, password=password)
    return client

"""
Close the ssh connection
:param SSHClient conn:
    the conneciton object of SSHClient
"""
def close_ssh_connection(conn):
    if conn and isinstance(conn,paramiko.SSHClient):
        conn.close()

class Libvirtd(object):
    """
    Class to manage libvirtd service on hosts.
    """
    def __init__(self,conn=None):
        """
        Init libvirtd obj
        :param SSHClient conn:the conneciton object of SSHClient
            if None == conne,localhost libvirtd service will be
        managed
        """
        self.ssh_conn = None
        if conn and isinstance(conn,paramiko.SSHClient):
            self.ssh_conn = conn

    def _wait_for_start(self, timeout=60):
        """
        Wait n seconds for libvirt to start.
        """
        sp_obj = sp.Popen(f"systemctl start {service_name}",
        stdout=sp.PIPE,stderr=sp.PIPE,shell=True)
        out,err = sp_obj.communicate(timeout=timeout)
        err_info = err.decode()
        if len(err_info) > 0:
            print(err_info)
            return False
        print(out.decode())
        return True

    def _wait_for_stop(self, timeout=60):
        """
        Wait n seconds for libvirt to stop.
        """
        sp_obj = sp.Popen("systemctl stop libvirtd-admin.socket",
        stdout=sp.PIPE,stderr=sp.PIPE,shell=True)
        sp_obj.communicate(timeout=timeout)
        sp_obj = sp.Popen("systemctl stop libvirtd-ro.socket",
        stdout=sp.PIPE,stderr=sp.PIPE,shell=True)
        sp_obj.communicate(timeout=timeout)
        sp_obj = sp.Popen("systemctl stop libvirtd.socket",
        stdout=sp.PIPE,stderr=sp.PIPE,shell=True)
        sp_obj.communicate(timeout=timeout)
        sp_obj = sp.Popen(f"systemctl stop {service_name}",
        stdout=sp.PIPE,stderr=sp.PIPE,shell=True)
        out,err = sp_obj.communicate(timeout=timeout)
        err_info = err.decode()
        if len(err_info) > 0:
            print(err_info)
            return False
        print(out.decode())
        return True

    def _wait_for_restart(self, timeout=60):
        """
        Wait n seconds for libvirt to restart.
        """
        sp_obj = sp.Popen(f"systemctl restart {service_name}",
        stdout=sp.PIPE,stderr=sp.PIPE,shell=True)
        out,err = sp_obj.communicate(timeout=timeout)
        err_info = err.decode()
        if len(err_info) > 0:
            print(err_info)
            return False
        print(out.decode())
        return True

    def _is_running(self,timeout=60):
        """
        Check whether libvirtd.service is running
        """
        sp_obj = sp.Popen(f"systemctl status {service_name}",
        stdout=sp.PIPE,stderr=sp.PIPE,shell=True)
        out,err = sp_obj.communicate(timeout=timeout)
        err_info = err.decode()
        if len(err_info) > 0:
            print(err_info)
            return False
        if "Active: active" in out.decode():
            print("running")
            return True
        else:
            return False

    def start(self,timeout=60):
        if self.ssh_conn:
            _,out,err = self.ssh_conn.exec_command(
                f"systemctl start {service_name}",timeout=timeout)
            err_info = err.read().decode().strip()
            if len(err_info) > 0:
                print(err_info)
                return False
            print(out.read().decode())
            return True
        else:
            return self._wait_for_start(timeout)

    def stop(self,timeout=60):
        if self.ssh_conn:
            self.ssh_conn.exec_command(
                "systemctl stop libvirtd-admin.socket",
                timeout=timeout)
            self.ssh_conn.exec_command(
                "systemctl stop libvirtd-ro.socket",
                timeout=timeout)
            self.ssh_conn.exec_command(
                "systemctl stop libvirtd.socket",
                timeout=timeout)
            _,out,err = self.ssh_conn.exec_command(
                f"systemctl stop {service_name}",timeout=timeout)
            err_info = err.read().decode().strip()
            if len(err_info) > 0:
                print(err_info)
                return False
            print(out.read().decode())
            return True
        else:
            return self._wait_for_stop(timeout)

    def restart(self,timeout=60):
        if self.ssh_conn:
            _,out,err = self.ssh_conn.exec_command(
                f"systemctl restart {service_name}",timeout=timeout)
            err_info = err.read().decode().strip()
            if len(err_info) > 0:
                print(err_info)
                return False
            print(out.read().decode())
            return True
        else:
            return self._wait_for_restart(timeout)

    def is_running(self,timeout=60):
        if self.ssh_conn:
            _,out,err = self.ssh_conn.exec_command(
                f"systemctl status {service_name}",timeout=timeout)
            err_info = err.read().decode().strip()
            if len(err_info) > 0:
                print(err_info)
                return False
            if "Active: active" in out.read().decode():
                print("active")
                return True
            else:
                return False
        else:
            return self._is_running(timeout)
        

if __name__ == "__main__":
    pass
    # ssh_conn = get_ssh_connection(
    #     hostname="",
    #     username="",
    #     password="")
    # print("remtoe test begin")
    # o_libvirt = Libvirtd(ssh_conn)
    # o_libvirt.start()
    # o_libvirt.is_running()
    # o_libvirt.stop()
    # o_libvirt.is_running()
    # o_libvirt.restart()
    # o_libvirt.is_running()
    # print("remtoe test end")
    # print("local test begin")
    # o_local = Libvirtd()
    # o_local.start()
    # o_local.is_running()
    # o_local.stop()
    # o_local.is_running()
    # o_local.restart()
    # o_local.is_running()
    # print("local test end")





