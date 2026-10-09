#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: my_test

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

extends_documentation_fragment:
    - my_namespace.my_collection.my_doc_fragment_name

author:
    - Your Name (@yourGitHubHandle)
'''

EXAMPLES = r'''
# Pass in a message
- name: Test with a message
  my_namespace.my_collection.my_test:
    name: hello world

# pass in a message and have changed true
- name: Test with a message and changed output
  my_namespace.my_collection.my_test:
    name: hello world
    new: true

# fail the module
- name: Test failure of the module
  my_namespace.my_collection.my_test:
    name: fail me
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
original_message:
    description: The original name param that was passed in.
    type: str
    returned: always
    sample: 'hello world'
message:
    description: The output message that the test module generates.
    type: str
    returned: always
    sample: 'goodbye'
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

        if p.is_file() and p.read_text(encoding="utf-8") ==  module.params['content']:
            return True

        return False

    def change_file():
        p = Path(module.params['path'])

        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(module.params['content'], encoding="utf-8")

    result['changed'] = not state_is_current()
    result['Path'] = module.params['path']
    result['Content'] = module.params['content']

    if module.check_mode:
        module.exit_json(**result)

    if result['changed']:
        change_file()

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()