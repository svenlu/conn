conn
====

审计在运维中占有很重要的一部分，审计追溯历史问题.

conn堡垒机:支持详细日志审计和录像功能,conn服务器上每一步操作都能记录.
  conn命令:  登录远端服务器，并记录所有操作和录像
  connplay:  播放历史录像，审核服务器记录
  connhost:  正向和反向解析主机名或ip地址(可批量)


```
    git clone https://github.com/shanhuhai5739/conn.git
    
    
```

complete -W "$(echo `cat ~/.ssh/known_hosts | cut -f 1 -d ' ' | sed -e s/,.*//g | uniq | grep -v "\["`;)" conn

    *.log        操作命令记录
    *detail.log  操作命令结果详细记录
    *.his        操作结果录像记录

conn coral@118.244.168.45:52101 
pip install paramiko
yum install xterm -y
