#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: yc_instance
short_description: Create a Yandex Compute Cloud virtual machine with the yc CLI
version_added: "1.0.0"
description:
  - Creates a Compute Cloud instance using the Yandex Cloud command line interface.
  - Instance settings are supplied as Ansible module parameters.
options:
  name:
    description: Instance name.
    type: str
    required: true
  hostname:
    description: Hostname assigned to the instance.
    type: str
    required: true
  zone:
    description: Availability zone.
    type: str
    required: true
  platform:
    description: Compute platform identifier.
    type: str
    required: true
  memory:
    description: Memory size in GiB.
    type: int
    required: true
  cores:
    description: Number of CPU cores.
    type: int
    required: true
  core_fraction:
    description: Guaranteed CPU performance, in percent.
    type: int
    required: true
  boot_disk_name:
    description: Boot disk name.
    type: str
    required: true
  boot_disk_type:
    description: Boot disk type.
    type: str
    required: true
  boot_disk_size:
    description: Boot disk size in GiB.
    type: int
    required: true
  boot_disk_block_size:
    description: Boot disk block size in bytes.
    type: int
    required: true
  boot_disk_image_id:
    description: Image ID used to create the boot disk.
    type: str
    required: true
  boot_disk_auto_delete:
    description: Whether to delete the boot disk with the instance.
    type: bool
    default: true
  subnet_id:
    description: Subnet ID for the network interface.
    type: str
    required: true
  nat_ip_version:
    description: Public IP version to assign to the interface.
    type: str
    choices: [ipv4, ipv6]
    default: ipv4
  ipv4_address:
    description: IPv4 address, or auto to assign one automatically.
    type: str
    default: auto
  preemptible:
    description: Whether to create a preemptible instance.
    type: bool
    default: true
  user_data:
    description: Cloud-init user-data passed as instance metadata.
    type: str
    required: true
  ssh_keys:
    description: SSH public keys passed as instance metadata.
    type: str
    required: true
  private_ui_created_from:
    description: Origin metadata value used by the Yandex Cloud console.
    type: str
    default: console
  yc_path:
    description: Path or command name of the yc executable.
    type: path
    default: yc
author:
  - Pavel
'''

EXAMPLES = r'''
- name: Create a Yandex Cloud VM
  my_own_namespace.yandex_cloud_elk.yc_instance:
    name: compute-vm-2-8-10-hdd-1791608534149
    hostname: compute-vm-2-8-10-hdd-1791608534149
    zone: ru-central1-a
    platform: standard-v3
    memory: 8
    cores: 2
    core_fraction: 50
    boot_disk_name: disk-ubuntu-24-04-lts-1791608536901
    boot_disk_type: network-hdd
    boot_disk_size: 10
    boot_disk_block_size: 4096
    boot_disk_image_id: fd8luhgf9o8h5vli509b
    boot_disk_auto_delete: true
    subnet_id: e9b4o9p3a9ack48k46at
    nat_ip_version: ipv4
    ipv4_address: auto
    preemptible: true
    user_data: |-
      #cloud-config
      datasource:
        Ec2:
          strict_id: false
      ssh_pwauth: no
      users:
        - name: pavel
          sudo: ALL=(ALL) NOPASSWD:ALL
          shell: /bin/bash
          ssh_authorized_keys:
            - ssh-ed25519 REPLACE_WITH_PUBLIC_KEY pavel@MSiberian
    ssh_keys: pavel:ssh-ed25519 REPLACE_WITH_PUBLIC_KEY pavel@MSiberian
    private_ui_created_from: console
'''

RETURN = r'''
instance:
  description: JSON representation of the created instance, when returned by yc.
  type: dict
  returned: when available
  sample:
    id: epd1234567890
    name: compute-vm-2-8-10-hdd-1791608534149
'''

import json
import os
import subprocess
import tempfile

from ansible.module_utils.basic import AnsibleModule


def _run_yc(module, args):
    """Run yc without a shell and report CLI errors through Ansible."""
    try:
        process = subprocess.run(
            [module.params['yc_path']] + args,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
    except OSError as exc:
        module.fail_json(msg='Unable to execute yc: {0}'.format(exc))

    if process.returncode != 0:
        module.fail_json(
            msg='yc command failed with exit code {0}'.format(process.returncode),
            stdout=process.stdout,
            stderr=process.stderr,
        )
    return process.stdout


def _find_existing_instance(module, name):
    output = _run_yc(module, ['compute', 'instance', 'list', '--format', 'json'])
    try:
        instances = json.loads(output or '[]')
    except ValueError as exc:
        module.fail_json(msg='yc returned invalid JSON while listing instances: {0}'.format(exc))

    for instance in instances:
        if instance.get('name') == name:
            return instance
    return None


def run_module():
    module_args = dict(
        name=dict(type='str', required=True),
        hostname=dict(type='str', required=True),
        zone=dict(type='str', required=True),
        platform=dict(type='str', required=True),
        memory=dict(type='int', required=True),
        cores=dict(type='int', required=True),
        core_fraction=dict(type='int', required=True),
        boot_disk_name=dict(type='str', required=True),
        boot_disk_type=dict(type='str', required=True),
        boot_disk_size=dict(type='int', required=True),
        boot_disk_block_size=dict(type='int', required=True),
        boot_disk_image_id=dict(type='str', required=True),
        boot_disk_auto_delete=dict(type='bool', default=True),
        subnet_id=dict(type='str', required=True),
        nat_ip_version=dict(type='str', choices=['ipv4', 'ipv6'], default='ipv4'),
        ipv4_address=dict(type='str', default='auto'),
        preemptible=dict(type='bool', default=True),
        user_data=dict(type='str', required=True),
        ssh_keys=dict(type='str', required=True, no_log=True),
        private_ui_created_from=dict(type='str', default='console'),
        yc_path=dict(type='path', default='yc'),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)
    name = module.params['name']

    existing = _find_existing_instance(module, name)
    if existing:
        module.exit_json(changed=False, instance=existing, msg='Instance already exists')

    if module.check_mode:
        module.exit_json(changed=True, instance=None, msg='Instance would be created')

    params = module.params
    disk_spec = 'name={0},type={1},size={2},block-size={3},image-id={4},auto-delete={5}'.format(
        params['boot_disk_name'],
        params['boot_disk_type'],
        params['boot_disk_size'],
        params['boot_disk_block_size'],
        params['boot_disk_image_id'],
        'yes' if params['boot_disk_auto_delete'] else 'no',
    )
    network_spec = 'subnet-id={0},nat-ip-version={1},ipv4-address={2}'.format(
        params['subnet_id'], params['nat_ip_version'], params['ipv4_address']
    )
    create_args = [
        'compute', 'instance', 'create',
        '--name', name,
        '--hostname', params['hostname'],
        '--zone', params['zone'],
        '--platform', params['platform'],
        '--memory', str(params['memory']),
        '--cores', str(params['cores']),
        '--core-fraction', str(params['core_fraction']),
        '--create-boot-disk', disk_spec,
        '--network-interface', network_spec,
        '--preemptible=' + ('true' if params['preemptible'] else 'false'),
    ]
    metadata_file = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as user_data_file:
            user_data_file.write(params['user_data'])
            metadata_file = user_data_file.name

        create_args.extend([
            '--metadata-from-file', 'user-data=' + metadata_file,
            '--metadata', 'ssh-keys={0},private_ui_created_from={1}'.format(
                params['ssh_keys'], params['private_ui_created_from']
            ),
        ])
        output = _run_yc(module, create_args)
    finally:
        if metadata_file and os.path.exists(metadata_file):
            os.unlink(metadata_file)
    try:
        instance = json.loads(output) if output.strip() else None
    except ValueError:
        instance = None

    module.exit_json(changed=True, instance=instance, stdout=output)


def main():
    run_module()


if __name__ == '__main__':
    main()
