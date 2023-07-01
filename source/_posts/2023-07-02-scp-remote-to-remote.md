---
id: scp-remote-to-remote
title: "scp 用法"
description: "可在本地和远程之间，以及远程和远程之间传输文件"
date: 2023.07.02 10:34
categories:
    - Linux
tags: [Linux]
keywords: scp, Linux, BSD, ssh
cover: /contents/covers/scp-remote-to-remote.png
---

scp 是 Linux 上两个网络主机之间传输文件的命令行工具。

# 基本用法

```text
scp [options] source ... target
```

- `options` 有很多，可通过 `man scp` 查看
- `source` 为传输的源文件或路径，可以多个
- `target` 为传输目标路径

`source` 或 `target` 为本地路径时，直接使用文件系统绝对路径即可；当为远程路径时，可使用如下两种格式：

1. `user@host:/path/to/file`
1. `scp://user@host:port//path/to/file`

第一种格式不能指定端口，第二种可以指定所使用的 ssh 端口。

> 注意：第二种格式 `host` 部分和 `path` 部分的间隔符也是 `/`，故如果路径为 `/path/to/file` 格式时，前面还需要再加一个 `/`。

# 实例

下面来看几个实例，假设有如下主机：

1. localhost（本地）
2. user1@host1（使用默认 22 端口）
3. user2@host2:port2（使用非 22 端口）
4. user3@host3:port2（使用与 host2 相同端口）
5. user4@host4:port4（使用非 22 端口）

## 本地文件传输至远程

将本地的 `/path/to/file` 文件传输至 `host1` 主机的 `/remote/path/to/file`：

```bash
scp /path/to/file user1@host1:/remote/path/to/file
```

## 远程文件夹传输至本地

将 `host1` 的 `/remote/path/to/dir` 传输至本地 `/path/to/dir`

```bash
scp -r user1@host1:/remote/path/to/dir /path/to/dir
```

> `-r` 遍历路径下所有文件和文件夹

## 远程文件传输至本地并改名

将 `host1` 的 `/remote/path/to/file` 传输至本地 `/path/to` 路径，并改名为 `newfile`

```bash
scp user1@host1:/remote/path/to/file /path/to/newfile
```

> 如不需修改文件名，目标路径的最后一部分可以省略。

## 本地至远程非 22 端口

将本地 `/path/to/file` 文件传输至 `host2` 主机的 `/remote/path/to/newfile`：

```bash
scp -P port2 /path/to/file user2@host2:/remote/path/to/file
```

> `-P` 用来指定远程主机端口，因为 `-p` 被用作表示保留文件元数据信息，此处指定端口需要用大写的 `P` 参数指定，与 `ssh` 命令指定端口的参数不同

## 多个远程主机的文件同时传输至本地

- 将 `host2` 的 `/remote/path/to/file2` 和 `host3` 的 `/remote/path/to/file3` 同时传输至本地 `/path/to` 路径下：
    ```bash
    scp -P port2 user2@host2:/remote/path/to/file2 user3@host3:/remote/path/to/file3 /path/to/
    ```
- 将 `host1` 的 `/remote/path/to/file1` 和 `host2` 的 `/remote/path/to/file2` 同时传输至本地 `/path/to` 路径下：
    ```bash
    scp user1@host1:/remote/path/to/file1 scp://user2@host2:port2//remote/path/to/file2 /path/to/
    ```
    > 因为 `host1` 使用默认的 `22` 端口，`host2` 使用自定义的 `port2` 端口，此时如果使用 `-P` 参数，则会使用相同的端口连接两个远程主机，所以需要通过 `scp://` 的形式来表示远程主机路径，且两种远程主机路径表示形式可混合使用。 

## 远程非 22 端口至远程非 22 端口

通过本地主机 `localhost`，直接将 `host2` 上的 `/remote/path/to/file` 传输至 `host4` 的 `/remote/path/to/file`：

```bash
scp -3 scp://user2@host2:port2//remote/path/to/file scp://user4@host4:port4//remote/path/to/file
```

> 使用这种远程至远程的文件传输时，如果需要密码访问，且出现输入密码混乱的情况，可以按照 [SSH 免密登录](https://alphahinex.github.io/2020/09/13/ssh-authorized-keys/) 中方式，先对两个主机进行免密登录，再传输文件

远程至远程传输目录时，不像有一方是本地路径会看到传输的具体文件和进度，终端中没有任何输出，可添加 `-v` 参数查看日志，以便了解传输状态。

**这种方式在 `host2` 和 `host4` 无法互相访问，但都可以被 `localhost` 访问时，非常有用！**

# 参考资料

https://askubuntu.com/questions/153960/scp-with-two-different-ports