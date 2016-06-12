bkcfg
=====
Backup network device configure file.

文件结构
========
├── group_vars #定义组变量，目录中的文件名要与组名保持一致，all代表所有主机
│   └── all.yml
├── hosts #定义主机组
├── inventory # -i
├── library #自定义模块 -M
│   └── ios_copy_run_tftp.py #拷贝runing configure文件到tftp服务器
├── README.md
├── roles
│   └── ios_run_tftp #角色ios_run_tftp的定义
│       ├── tasks
│       │   └── main.yml
│       └── vars
│           └── main.yml
├── secrets.yml #ansible-vault edit 编辑已加密的文件
├── site.retry
└── site.yml  #全局配置文件

调试
====
~/ansible/hacking/test-module -m ios_copy_run_tftp.py -a 'auth_pass=超级用户密码 host=网络设备IP password=密码 username=用户名 remote=TFTP服务器IP'

示例
====

[root@hostname bkcfg]# ansible-playbook -i inventory -M ./library/ios_copy_run_tftp.py site.yml --ask-vault-pass
Vault password:

PLAY [copy network device configure file to tftp server] ***********************

TASK [ios_run_tftp : Cisco device copy running-config to tftp server] **********
ok: [ZB-F05-C2_SW-A01]

PLAY RECAP *********************************************************************
ZB-F05-C2_SW-A01           : ok=1    changed=0    unreachable=0    failed=0

[root@hostname bkcfg]#

