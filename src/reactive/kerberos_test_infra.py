import socket

from charms.reactive import (
    set_flag,
    clear_flag,
    when,
    when_not,
    hook,
    endpoint_from_flag,
)

from charmhelpers.core import hookenv

from kerberos.kerberos_test_infra_utils import (
    debconf_set_selections,
    configure_bind_zone,
    render_kadm_acl,
    configure_systemd_resolved,
)


@hook('install')
def install():
    config = hookenv.config()
    realm = config['realm']
    hostname = socket.gethostname()
    # set debconf selections before apt layer installs packages
    debconf_set_selections("krb5-config krb5-config/default_realm string {}"
                           "".format(realm))
    debconf_set_selections("krb5-config krb5-config/kerberos_servers string {}"
                           "".format(hostname))
    debconf_set_selections("krb5-config krb5-config/admin_server string {}"
                           "".format(hostname))
    render_kadm_acl()


@when_not('kerberos-test-infra.installed')
@when('apt.installed.bind9')
@when('apt.installed.krb5-kdc')
@when('apt.installed.krb5-admin-server')
def install_kerberos_infra():
    set_flag('kerberos-test-infra.installed')
    configure_bind_zone()
    configure_systemd_resolved()
    hookenv.status_set('active', 'kerberos-test-infra is installed')


@when('endpoint.dns-zone.changed.hostname')
def update_zone():
    dns_zone = endpoint_from_flag('endpoint.dns-zone.changed.hostname')
    zone_entries = {}
    for u in dns_zone.all_joined_units.values():
        hostname = u.received.get('hostname')
        addr = u.received.get('ingress-address')
        if hostname and addr:
            zone_entries.update({hostname: addr})
    configure_bind_zone(zone_entries)
    clear_flag('endpoint.dns-zone.changed.hostname')
