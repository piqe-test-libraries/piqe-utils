import libvirt

def get_hypervisor():
    """Get hypervisor type"""
    return libvirt.open()


def get_uri(ipaddr):
    """Get hypervisor uri"""
    return libvirt.open(f"qemu+ssh://{ipaddr}/system").getURI()


def get_conn(uri=None, username=None, password=None):
    """ get connection object from libvirt module
    """
    if None == username or None == password:
        return libvirt.open(uri)
    else:
        def request_cred(credentials, user_data):
            for credential in credentials:
                if credential[0] == libvirt.VIR_CRED_AUTHNAME:
                    credential[4] = username
                elif credential[0] == libvirt.VIR_CRED_PASSPHRASE:
                    credential[4] = password
            return 0
        auth = [[libvirt.VIR_CRED_AUTHNAME,libvirt.VIR_CRED_PASSPHRASE], request_cred, None]
        return libvirt.openAuth(uri,auth,0)
