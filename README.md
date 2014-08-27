conn
====

审计在运维中占有很重要的一部分，审计追溯历史问题.  

conn堡垒机:支持详细日志审计和录像功能,conn服务器上每一步操作都能记录.  
  conn命令:  登录远端服务器，并记录所有操作和录像  
  connplay:  播放历史录像，审核服务器记录  
  connhost:  正向和反向解析主机名或ip地址(可批量)  


安装部署
```
    堡垒机安装
    git clone https://github.com/shanhuhai5739/conn.git
    cd conn
    pip install -r requirements.txt -i http://pypi.douban.com/simple/
    客户机安装
    yum install xterm -y
    
    如果想让conn支持tab显示主机，将下面命令编辑到/etc/profile
    complete -W "$(echo `cat ~/.ssh/known_hosts | cut -f 1 -d ' ' | sed -e s/,.*//g | uniq | grep -v "\["`;)" conn
    source /etc/profile
```

登录主机
```
    conn 用户@主机名|IP:端口
      支持rsa dsa passwd方式登录，优先rsa登录

    conn coral@118.244.168.45:52101
```

日志审计
```
    20140827-118.244.168.45-coral-detail.log
    日志格式: 时间-主机-用户

    两种日志格式:
    logs/*.log        操作命令记录
    logs/*detail.log  操作命令结果详细记录
    用户在登录状态下可以实时看到输出结果,tail -f xxx-xxx-xxx.log
```

录像审计
```
    20140827173556-118.244.168.45-coral
    录像格式: 时间-主机-用户

    videos/*.his        操作结果录像记录
    用户推出后生成.his和.time文件，使用hostplay进行播放
    connplay ls    显示所有录像记录文件
    connplay play 20140827173556-118.244.168.45-coral    播放该记录文件
```

