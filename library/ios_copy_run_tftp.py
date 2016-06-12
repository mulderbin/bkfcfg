#!/usr/bin/python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
---
module: ios_copy_run_tftp
version_added: "0.1"
author: "Luo Jianbina (luojianbin@gmail.com)"
short_description: Copy Cisco IOS running configure file to tftp server
description:
  - Copy IOS running configure file to tftp server
options:
  auth_pass:
    description:
      - Specifies the password to use if required to enter privileged mode on the remote device.
    required: False
    default: '' 
  authorize:
    description:
      - Instructs the module to enter priviledged mode on the remote device before sending any commands.  If
        not specified, the device will attempt to excecute all commands in non-priviledged mode.
    required: False
    default: True
  host:
    description:
      - Specifies the DNS host name or address for connecting to the remote cisco ios device over the specified
        transport.  The value of host is used as the destination address for the transport.
    required: True
  password:
    description:
      - Specifies the password to use to authenticate the connection to the remote device.   The value of
        `password' is used to authenticate the TELNET session.
    required: True
  port:
    description:
      - Specifies the port to use when buiding the connection to the remote device.  The port value will
        default to the well known TELNET port of 23
    required: False
    default: 23
  timeout:
    description:
      - Specifies idle timeout for the connection. Useful if the console freezes before continuing. For
        example when saving configurations.
    required: False
    default: 10 seconds
  username:
    description:
      - Configures the usename to use to authenticate the connection to the remote device.  The value of
        `username' is used to authenticate the TELNET session.
    required: True
  remote:
    description:
      - tftp server
    required: True
  filename:
    description:
      - Saved file name on the tftpserver
    required: False
    default: IOS defaule filename
'''

EXAMPLES = '''
#Test
~/ansible/hacking/test-module -m ios_copy_run_tftp.py -a 'auth_pass=secrte host=cisco-ios-device password=pwd username=name remote=tftp-server'
'''


from ansible.module_utils.basic import *
import telnetlib
import re

USERNAME_RE = [re.compile(r"[\r\n]?username: $", re.I)]

PASSWORD_RE = [re.compile(r"[\r\n]?password: $", re.I)]

CLI_PROMPTS_RE = [
    re.compile(r"[\r\n]?[\w+\-\.:\/\[\]]+(?:\([^\)]+\)){,3}(?:>|#) ?$"),
    re.compile(r"\[\w+\@[\w\-\.]+(?: [^\]])\] ?[>#\$] ?$")
]

CLI_ERRORS_RE = [
    re.compile(r"% ?Error"),
    re.compile(r"% ?Bad secret"),
    re.compile(r"invalid input", re.I),
    re.compile(r"(?:incomplete|ambiguous) command", re.I),
    re.compile(r"connection timed out", re.I),
    re.compile(r"[^\r\n]+ not found", re.I),
    re.compile(r"'[^']' +returned error code: ?\d+"),
]


def ios_copy_run_tftp(module, auth_pass, authorize, host, password, port, timeout, username, remote, filename):
    ERROR_MSG = 'LOGIN: OK'
    try:
        tn = telnetlib.Telnet(host, port, timeout)
        tn.expect(USERNAME_RE, timeout)
        tn.write(username+"\n")
        tn.expect(PASSWORD_RE, timeout)
        tn.write(password+"\n")
        answer_str = tn.expect(CLI_PROMPTS_RE + USERNAME_RE, timeout)
        if USERNAME_RE[0].search(answer_str[2]):
            tn.close()
            ERROR_MSG = 'LOGIN: Username password error'
            return ERROR_MSG 

        if authorize == 'yes':
            tn.write("enable"+"\n")
            tn.expect(PASSWORD_RE, timeout)
            tn.write(auth_pass+"\n")
            answer_str = tn.expect(CLI_PROMPTS_RE, timeout)
            if re.search("Access denied", answer_str[2]):
               tn.close()
               ERROR_MSG = 'LOGIN: Privileged password error'
               return ERROR_MSG

        tn.write("copy running-config tftp:"+"\n")
        tn.read_until("]?")
        tn.write(remote+"\n")
        tn.read_until("]?")
        if filename == '':
            filename = host + '-' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.cfg'
            tn.write(filename+"\n")
        else:
            tn.write(filename+"\n")

        answer_str = tn.expect(CLI_PROMPTS_RE)
        if re.search("Error", answer_str[2]):
            ERROR_MSG = 'LOGIN: ' + answer_str[2]

        tn.write("exit"+"\n")
        tn.close()
        
        return ERROR_MSG 

    except Exception as error:
        print host, 'ERROR', error

def main():
    module = AnsibleModule(
        argument_spec=dict(
            auth_pass=dict(required=False, default=''),
            authorize=dict(required=False, default='yes'),
            host=dict(required=True),
            password=dict(required=True),
            port=dict(required=False, type='int', default=23),
            timeout=dict(requried=False, type='int', default=10),
            username=dict(required=True),
            remote=dict(required=True),
            filename=dict(required=False, default='')
        ),
        supports_check_mode=True
    )


    if module.check_mode:
        module.exit_json(changed=False)

    auth_pass = module.params['auth_pass']
    authorize = module.params['authorize']
    host = module.params['host']
    password = module.params['password']
    port = module.params['port']
    timeout = module.params['timeout']
    username = module.params['username']
    remote = module.params['remote']
    filename = module.params['filename']

    ERROR_MSG = ios_copy_run_tftp(module, auth_pass, authorize, host, password, port, timeout, username, remote, filename)
    if ERROR_MSG =='LOGIN: OK':
        module.exit_json(changed=False)
    else:
        if re.match('LOGIN:', ERROR_MSG):
            msg = ERROR_MSG 
        else:
            msg = "Cound not reach %s" % (host)
        module.fail_json(msg=msg)



if __name__ == '__main__':
    main()

