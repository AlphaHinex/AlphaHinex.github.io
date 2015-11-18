---
layout: post
title:  "docker-machine 设置代理"
description: "随着 Docker 1.8 的发布，docker-machine 将 boot2docker 封装了起来。docker-machine 在需要通过代理访问网络时需要特殊的配置，配置方式如下"
headline: "Hex"
date:   2015-11-12 10:55:47
categories: Cloud
tags: [OSX, Docker, Proxy]
comments: true
---

`docker-machine` 实际是运行在 `OS X` 上的 `VirtualBox` 虚拟机内，将之前的 `boot2docker` 进行了封装，配置代理的方式与之前在 `boot2docker` 中的设置方式不同。具体设置步骤为：

	# ssh 到 default 虚拟机
    $ docker-machine ssh default
    
    # 连接后提示符类似这样：
    # docker@default:~$
    
    # 获得 root 权限
    $ sudo -s
    
    # 此时提示符类似这样：
    # root@default:~$
    
    # 设置代理
    $ echo "export HTTP_PROXY=http://[uid]:[pw]@corporate.proxy.com:[port]" >> /var/lib/boot2docker/profile
    $ echo "export HTTPS_PROXY=http://[uid]:[pw]@corporate.proxy.com:[port]" >> /var/lib/boot2docker/profile
    
    # 验证配置
    $ cat /var/lib/boot2docker/profile
    
    # 退出 root 及 ssh
    $ exit
    $ exit
    
    # 重启 default
    $ docker-machine restart default
    
    # 此时应该可以通过代理获得镜像了
    $ docker pull hello-world
    
> 几乎所有的 `boot2docker` 内的文件都会在重启后被重置，但 `/var/lib/boot2docker/profile` 是个例外，所以上面的配置只需设置一次即可；但若使用了 `DaoCloud` 的加速器，可能会将上面设置的代理信息重置，则需重新配置一遍

**参考资料**

* [How to Run docker-machine from Behind a Corporate Proxy](http://mflo.io/2015/08/13/docker-machine-behind-proxy/)