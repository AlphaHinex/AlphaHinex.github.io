---
id: TeamCity-for-Java-Project-on-GitHub
title:  "TeamCity for Java Project on GitHub"
date:   2016-06-15 13:53:47
categories: Java
tags: [TeamCity, GitHub, jacoco, Codecov]
cover: https://ardalis.com/wp-content/uploads/2016/11/teamcity_github.jpg
---

GitHub 上 Java 项目使用 TeamCity 和 Codecov 的简易说明

目标
---

- 利用 TeamCity 构建 GitHub 上的 Java 项目
- 构建时进行静态代码质量检查及单元测试，并生成测试覆盖率报告
- 确保每个 PR 和 master 分支的每次提交都能触发构建
- 将构建结果和覆盖率情况可视化展现


环境准备
------

使用 [Docker](https://www.docker.com/) 镜像搭建基础环境：

```bash
$ docker pull propersoft/docker-teamcity:server
$ docker pull propersoft/docker-teamcity:agent-java
```

> `docker-teamcity` 镜像基于 `OpenJDK 7` 构建

> `server` tag 为 TeamCity Server，包含 [TeamCity.GitHub 插件](https://github.com/jonnyzzz/TeamCity.GitHub)，用以通过 [GitHub Change Status API](https://github.com/blog/1227-commit-status-api) 将构建状态展示在 `Pull Request` 中

> `agent-java` tag 为 TeamCity Agent，包含 `gralde` 构建工具，用以构建 java 项目

启动 TeamCity Server，并将 `context` 设置为 `tc`：

```bash
$ docker run --name tc-server -v /home/ds/teamcity:/var/lib/teamcity -p 9090:8111 -e 'TEAMCITY_CONTEXT=tc' -d propersoft/docker-teamcity:server
```

启动 2 个 TeamCity Java Agent：

```bash
$ docker run --name tc-aj1 -p 9091:9090 -e 'TEAMCITY_SERVER=http://SERVER_IP:9090/tc' -e 'TEAMCITY_AGENT_PORT=9091' -e 'TEAMCITY_AGENT_NAME=Java Agent 1' -d propersoft/docker-teamcity:agent-java
$ docker run --name tc-aj2 -p 9092:9090 -e 'TEAMCITY_SERVER=http://SERVER_IP:9090/tc' -e 'TEAMCITY_AGENT_PORT=9092' -e 'TEAMCITY_AGENT_NAME=Java Agent 2' -d propersoft/docker-teamcity:agent-java
```

此时可登录 TeamCity Server，看到有两个 Agent，授权后即可使用。


添加项目及构建
------------

添加 GitHub Repo 至 `VCS Roots` 后，需配置 `Branch Specification`：`+:refs/pull/(*/merge)`

在 gradle 的任务中通过 jacoco 插件生成覆盖率报告。为了在 [codecov](https://codecov.io/) 平台展现总体的覆盖率情况，需设置 jacoco 生成 xml 格式的报告

> 若项目为私有仓库，需在项目根路径创建 `codecov.yml`，并在其中添加 `codecov` 平台提供的 `token`

在构建步骤中添加 `Command Line` 类型步骤，将 `curl -s https://codecov.io/bash | bash` 配置到 `custom script` 中，以将覆盖率报告上传至 `codecov`

添加 `VCS Trigger`，使用默认配置即可

在 `Build Features` 中添加 `Report change status to GitHub` 的 Feature，并调整好相应配置


构建结果和覆盖率情况可视化展现
-------------------------

启用 TeamCity 的 `guest` 账户，并赋予其查看构建结果的权限

通过 TeamCity 的 [status icon](https://blog.jetbrains.com/teamcity/2012/07/teamcity-build-status-icon/) 和 Codecov 提供的 `Badge` 将构建结果和覆盖率情况可视化展现


将 TeamCity 部署至 nginx 后面
---------------------------

```nginx
map $http_upgrade $connection_upgrade {
    default upgrade;
    ''   '';
}

server {
    listen       400;
    server_name  teamcity.public;

    location /tc {
        proxy_pass          http://teamcity.local:8111/tc;
        proxy_http_version  1.1;
        proxy_set_header    X-Forwarded-For $remote_addr;
        proxy_set_header    Host $server_name:$server_port;
        proxy_set_header    Upgrade $http_upgrade;
        proxy_set_header    Connection $connection_upgrade;
    }
}
```

```nginx
http {
    proxy_read_timeout     1200;
    proxy_connect_timeout  240;
    client_max_body_size   0;
    ....
}
```


参考资料
------

- [Automatically Building Pull Requests from GitHub](https://blog.jetbrains.com/teamcity/2013/02/automatically-building-pull-requests-from-github-with-teamcity/)
- [TeamCity build status icon](https://blog.jetbrains.com/teamcity/2012/07/teamcity-build-status-icon/)
- [Build Status Icon](https://confluence.jetbrains.com/display/TCD9/REST+API#RESTAPI-BuildStatusIcon)
- [Set Up TeamCity behind Nginx](https://confluence.jetbrains.com/pages/viewpage.action?pageId=74847395#HowTo...-Nginx)
