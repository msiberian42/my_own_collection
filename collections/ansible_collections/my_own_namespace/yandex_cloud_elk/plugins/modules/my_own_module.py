#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: my_own_module

short_description: This is my test module

version_added: "1.0.0"

description: This is my longer description explaining my test module.

options:
    path:
        description: Path.
        required: true
        type: str
    content:
        description:
           Content.
        required: false
        type: str

author:
    - Pavel
'''

EXAMPLES = r'''
# Создание файла с текстом
- name: Create a file
  my_own_namespace.yandex_cloud_elk.my_own_module:
    path: /tmp/example.txt
    content: Hello, World!

# Создание корневых директорий
- name: Create a file in a nested directory
  my_own_namespace.yandex_cloud_elk.my_own_module:
    path: /tmp/example/example.txt
    content: Hello, World!
'''

RETURN = r'''
changed:
    description: Whether the file was created or its content changed.
    type: bool
    returned: always
    sample: true
Path:
    description: The path of the file.
    type: str
    returned: always
    sample: /tmp/example.txt
Content:
    description: The content for the file.
    type: str
    returned: always
    sample: Hello, Ansible!
'''

from ansible.module_utils.basic import AnsibleModule
from pathlib import Path


def run_module():
    module_args = dict(
        path=dict(type='str', required=True),
        content=dict(type='str', required=False, default='Default Content')
    )

    result = dict(
        changed=False,
        Path='',
        Content=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    def state_is_current() -> bool:
        p = Path(module.params['path'])

        if not p.exists():
            return False
        if not p.is_file():
            raise OSError('Это не файл')
        return p.read_text(encoding="utf-8") == module.params['content']

    def change_file():
        p = Path(module.params['path'])

        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(module.params['content'], encoding="utf-8")

    result['Path'] = module.params['path']
    result['Content'] = module.params['content']

    try:
        result['changed'] = not state_is_current()
    except (OSError, UnicodeError) as e:
        module.fail_json(msg='Невозможно проверить файл {0}: {1}'.format(module.params['path'], e), **result)

    if module.check_mode:
        module.exit_json(**result)

    if result['changed']:
        try:
            change_file()
        except OSError as e:
            module.fail_json(msg='Unable to write file {0}: {1}'.format(module.params['path'], e), **result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
