import socket
import subprocess
import charmhelpers.core as core
import charmhelpers.core.host as ch_host

from charmhelpers.core.hookenv import (
    config,
    network_get,
)


def debconf_set_selections(line):
    subprocess.run("debconf-set-selections",
                   input=line.encode('utf-8'),
                   shell=True, check=True)


def configure_bind_zone(hosts={}):
    '''
    Render bind9 zone configuration.
    '''
    charm_config = config()
    realm = charm_config['realm']

    ch_host.mkdir('/etc/bind/zones', perms=0o755, owner='root',
                  group='bind')

    ctxt = {}
    ctxt['domain'] = realm

    hosts.update({
        socket.gethostname(): network_get('dns-server')['ingress-addresses'][0]
    })

    ctxt['hosts'] = hosts

    core.templating.render(
        source='bind_zone',
        target='/etc/bind/zones/{}'.format(realm),
        context=ctxt,
        owner='root',
        group='bind',
        perms=0o644,
    )

    ch_host.service_restart('bind9')


def render_kadm_acl():
    '''
    Render an ACL file for kadm. It is required to have it (even an empty one)
    in order to start krb5-admin-server.service.
    '''
    ch_host.mkdir('/etc/krb5kdc/', perms=0o700, owner='root', group='root')
    ctxt = {}

    core.templating.render(
        source='kadm5.acl',
        target='/etc/krb5kdc/kadm5.acl',
        context=ctxt,
        owner='root',
        group='root',
        perms=0o644,
    )


def configure_systemd_resolved(hosts={}):
    '''
    Render a drop-in config file for systemd-resolved at
    /etc/systemd/resolved.conf.d/ and restart the systemd-resolved service.

    This is done in order to use a local bind9 server as a resolver.
    '''
    charm_config = config()
    realm = charm_config['realm']

    ch_host.mkdir('/etc/systemd/resolved.conf.d/', perms=0o755, owner='root',
                  group='root')

    ctxt = {}
    ctxt['domain'] = realm
    ctxt['dns_ip'] = network_get('dns-server')['ingress-addresses'][0]

    core.templating.render(
        source='local-dns-bind.conf',
        target='/etc/bind/zones/{}'.format(realm),
        context=ctxt,
        owner='root',
        group='root',
        perms=0o644,
    )

    ch_host.service_restart('systemd-resolved')
