# Overview

Sets up basic Kerberos infrastructure for functional testing of a applications
that need Kerberos authentication against a target service.

The charm provides the following:

* Installation and basic setup of a Kerberos KDC and Admin Server;
* Installation of bind9 and setup of a basic zone;
* (WIP) Generation of a principle and an ability to download a bundle of keytabs (tar).

# Usage

Keytab files will be archived with the following naming convention:

    <hostname>.keytab

Deployment instructions:

    - juju deploy kerberos-test-infra
    - juju deploy kerberos-test-client
    - juju add-relation kerberos-test-infra kerberos-test-client

A kerberos-test-client machine (WIP) will be set up to use the kerberos-test-infra
ingress-address as a DNS server.
