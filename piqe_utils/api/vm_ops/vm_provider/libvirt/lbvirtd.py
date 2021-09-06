"""Module to perform libvirtd related operations"""

from time import asctime, time
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
        if conn and isinstance(conn,paramiko.SSHClient):
            self.ssh_conn = conn
            self.run_cmd = self._get_output_remote
        else:
            self.ssh_conn = None
            self.run_cmd = self._get_output_local

    def _get_output_remote(self,cmd,timeout):
        """
        Get cmd running on remote output
        """
        if self.ssh_conn:
            _,out,err = self.ssh_conn.exec_command(cmd,timeout=timeout)
            err_info = err.read().decode().strip()
            out_info = out.read().decode().strip()
            return out_info,err_info

    def _get_output_local(self,cmd,timeout):
        """
        Get cmd running on local output
        """
        sp_obj = sp.Popen(cmd,stdout=sp.PIPE,stderr=sp.PIPE,shell=True)
        out,err = sp_obj.communicate(timeout=timeout)
        err_info = err.decode()
        out_info = out.decode()
        return out_info,err_info

    def start(self,timeout=60):
        """
        Start libvirtd service
        """
        cmd = f"systemctl start {service_name}"
        out_info,err_info = self.run_cmd(cmd,timeout)
        if len(err_info) > 0:
            print(err_info)
            return False
        print(out_info)
        return True

    def stop(self,timeout=60):
        """
        Stop libvirtd service
        """
        cmd = f"""
        systemctl stop libvirtd-admin.socket
        systemctl stop libvirtd-ro.socket
        systemctl stop libvirtd.socket
        systemctl stop {service_name}
        """
        out_info,err_info = self.run_cmd(cmd,timeout)
        if len(err_info) > 0:
            print(err_info)
            return False
        print(out_info)
        return True

    def restart(self,timeout=60):
        """
        Restart libvirtd service
        """
        cmd = f"systemctl restart {service_name}"
        out_info,err_info = self.run_cmd(cmd,timeout)
        if len(err_info) > 0:
            print(err_info)
            return False
        print(out_info)
        return True

    def is_running(self,timeout=60):
        """
        Check whether libvirtd is running
        """
        cmd = f"systemctl status {service_name}"
        out_info,err_info = self.run_cmd(cmd,timeout)
        if len(err_info) > 0:
            print(err_info)
            return False
        print(out_info)
        if "Active: active" in out_info:
            print("Active")
            return True
        return False

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





