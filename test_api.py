import eventlet
eventlet.monkey_patch()

import httplib
import json
from time import sleep
import sys
import uuid


def generate_uuid():
    return str(uuid.uuid4())


########################################
# Testing script for the Climate Lease API.
# Climate services may be started by the following lines in command lime
# python -m climate.cmd.climate_api --config-file=/etc/climate/climate.conf -d --log-exchange
# python -m climate.cmd.climate_manager --config-file=/etc/climate/climate.conf -d --log-exchange
#
# Config file example:
#
########################################
#
# [DEFAULT]
#
# os_auth_host=<auth_host>
# os_auth_port=<auth_port>
# os_auth_protocol=<http, for example>
# os_admin_username=<username>
# os_admin_password=<password>
# os_admin_tenant_name=<tenant_name>
#
# plugins=dummy.vm.plugin
#
# [virtual:instance]
# on_start = wake_up
# on_end = delete
#
########################################
#
# Running RabbitMQ server required
# Also please set CLIMATE_ADDRESS, USER_ID, TENANT_ID, AUTH_TOKEN variables
# after this description to the actual ones
#
########################################
#
# To use this testing script:
# === list ===
# python test_api.py list
# === create 5 leases ===
# python test_api.py create 5
# === get lease ===
# python test_api.py show <lease_id>
# === update leases name ===
# python test_api.py update <lease_id>
# === delete lease ===
# python test_api.py delete <lease_id>
#
########################################




CLIMATE_ADDRESS = 'host:1234'
USER_ID = 'Keystone user ID'
TENANT_ID = 'Keystone tenant ID'
AUTH_TOKEN = 'Keystone AUTH token'


def lease_create():
    """Test lease creation"""
    conn = httplib.HTTPConnection(CLIMATE_ADDRESS)
    params = {'name': 'lease%s' % generate_uuid(),
              'start_date': '2014-09-26 14:23',
              'end_date': '2014-09-28 14:23',
              'reservations': [
                  {'resource_id': '2345',
                   'resource_type': 'virtual:instance'}
              ]}
    headers = {'X-User-Id': USER_ID, 'X-Tenant-Id': TENANT_ID,
               'X-Auth-Token': AUTH_TOKEN, 'Content-Type': 'application/json'}
    conn.request('POST', '/v1/leases',
                 body=json.dumps(params), headers=headers)
    resp = conn.getresponse()
    print resp.read()
    conn.close()


def lease_delete(lease_id):
    """Test lease deletion"""
    conn = httplib.HTTPConnection(CLIMATE_ADDRESS)
    headers = {'X-User-Id': USER_ID,
               'X-Tenant-Id': TENANT_ID,
               'X-Auth-Token': AUTH_TOKEN}
    conn.request('DELETE', '/v1/leases/%s' % lease_id, headers=headers)
    resp = conn.getresponse()
    print resp.read()
    conn.close()


def lease_list():
    """List leases"""
    conn = httplib.HTTPConnection(CLIMATE_ADDRESS)
    headers = {'X-User-Id': USER_ID,
               'X-Tenant-Id': TENANT_ID,
               'X-Auth-Token': AUTH_TOKEN}
    conn.request('GET', '/v1/leases', headers=headers)
    resp = conn.getresponse()
    print resp.read()
    conn.close()


def lease_show(lease_id):
    """Get info about one lease"""
    conn = httplib.HTTPConnection(CLIMATE_ADDRESS)
    headers = {'X-User-Id': USER_ID,
               'X-Tenant-Id': TENANT_ID,
               'X-Auth-Token': AUTH_TOKEN}
    conn.request('GET', '/v1/leases/%s' % lease_id, headers=headers)
    resp = conn.getresponse()
    print resp.read()
    conn.close()


def lease_update(lease_id):
    """Update lease's name"""
    conn = httplib.HTTPConnection(CLIMATE_ADDRESS)
    headers = {'X-User-Id': USER_ID,
               'X-Tenant-Id': TENANT_ID,
               'X-Auth-Token': AUTH_TOKEN,
               'Content-Type': 'application/json'}
    params = {'name': 'REALLY_NEW_NAME_%s' % generate_uuid()}
    conn.request('PUT', '/v1/leases/%s' % lease_id,
                 body=json.dumps(params), headers=headers)
    resp = conn.getresponse()
    print resp.read()
    conn.close()


if __name__ == '__main__':
    num = 1
    lease_id = None
    try:
        operation = sys.argv[1]
    except IndexError:
        operation = 'show'
    if operation == 'create':
        try:
            # only to create several leases in one time
            num = int(sys.argv[2])
        except IndexError:
            num = 1
    pool = eventlet.GreenPool()
    if operation not in ['create', 'list']:
        try:
            lease_id = sys.argv[2]
        except IndexError:
            raise IndexError('Please set lease id to work with.')
    fn_name = 'lease_%s' % operation
    for i in xrange(num):
        if lease_id:
            pool.spawn_n(locals()[fn_name], lease_id)
        else:
            pool.spawn_n(locals()[fn_name])
        sleep(0.5)
        print >> sys.stderr, '.', pool.waitall()

