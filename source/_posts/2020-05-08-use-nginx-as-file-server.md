---
id: use-nginx-as-file-server
title: "使用 Nginx 作为 HTTP 文件服务"
description: "Http 访问，中文路径及基本权限控制"
date: 2020.05.08 19:34
categories:
    - Nginx
tags: [Nginx, HTTP]
keywords: Nginx, File server, HTTP, Charset, Basic HTTP authentication, ngx_http_auth_basic_module
cover: /contents/covers/use-nginx-as-file-server.jpeg
---


## 伺服文件路径

[ngx_http_autoindex_module](http://nginx.org/en/docs/http/ngx_http_autoindex_module.html) 模块可处理请求并生成目录列表。启用后当 [ngx_http_index_module](http://nginx.org/en/docs/http/ngx_http_index_module.html) 模块无法找到 index 文件时，会将请求交给 `ngx_http_autoindex_module` 模块处理。

配置示例：

```nginx
location / {
    autoindex on;
}
```

其他相关指令可查看 [官方文档](http://nginx.org/en/docs/http/ngx_http_autoindex_module.html)。

另外，需要配合 [ngx_http_core_module](http://nginx.org/en/docs/http/ngx_http_core_module.html) 模块的 [root](http://nginx.org/en/docs/http/ngx_http_core_module.html#root) 指令指定文件服务的根路径，如：

```nginx
location /i/ {
    root /data/w3;
}
```


## 设定字符集

[ngx_http_charset_module](http://nginx.org/en/docs/http/ngx_http_charset_module.html) 提供了 charset 指令，设定相应字符集可以解决中文乱码问题，如：

```nginx
location / {
    charset utf-8;
}
```


## 添加基本访问权限控制

[ngx_http_auth_basic_module](http://nginx.org/en/docs/http/ngx_http_auth_basic_module.html) 提供了使用 “HTTP Basic Authentication” 协议，进行基本的用户名和密码的认证。

配置示例：

```nginx
location / {
    auth_basic           "closed site";
    auth_basic_user_file conf/htpasswd;
}
```

`auth_basic` 可以是任意字符串；`auth_basic_user_file` 需指定一个包含用户名和密码的文件，文件格式如下：

```
# comment
name1:password1
name2:password2:comment
name3:password3
```

密码可使用 `openssl passwd` 命令生成，例如：

```bash
$ openssl passwd -crypt 123456
AvkEiRVc9LrPs
```

> 注意：相同密码每次生成的密文不一致

更多支持的密码类型，可见 [模块文档](http://nginx.org/en/docs/http/ngx_http_auth_basic_module.html)。


## 完整实例

nginx 配置：[https://github.com/AlphaHinex/compose-docker/blob/master/nginx/file_server.conf](https://github.com/AlphaHinex/compose-docker/blob/master/nginx/file_server.conf)

可借助 [docker-compose](https://github.com/AlphaHinex/compose-docker/blob/master/docker-compose.yml) 启动：

```bash
$ docker-compose up -d nginx
```

之后访问 http://localhost:2020

输入用户名 `alpha`，密码 `hinex`，即可看到文件列表。
