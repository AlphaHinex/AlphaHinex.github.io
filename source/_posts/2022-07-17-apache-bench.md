---
id: apache-bench
title: "ApacheBench 简介"
description: "简单易用的 HTTP 服务性能测试工具"
date: 2022.07.17 10:34
categories:
    - Test
tags: [HTTP, Java]
keywords: Apache Bench, ab, test
cover: /contents/apache-bench/cover.png
---

[ApacheBench](https://httpd.apache.org/docs/current/programs/ab.html) 简称 `ab`，是 [Apache HTTP Server](https://httpd.apache.org/) 中的一个性能测试工具，可单独安装，在命令行中直接使用，可基于 HTTP 接口对任意 HTTP 服务器进行性能测试，得到每秒请求数（RPS）、平均请求响应时间等性能指标。

## 安装

### Ubuntu/Debian

```bash
$ sudo apt-get update 
$ sudo apt-get install -y apache2-utils
```

### CentOS/Readhat/Fedora

```bash
$ yum install httpd-tools
```

### MacOS

MacOS 中自带此工具，可在终端中执行 `ab -V` 查看版本信息。

若系统版本较旧没有自带此工具，可参照下面的 [gist](https://gist.github.com/safecat/f450ce5ed5a51b3b6f32) 脚本进行编译安装：

```bash
# ATTENTION PLEASE!
# NOTE BY @riwazp7
# Note for future visitors of this gist: Mac OS has Apache Benchmark by default ab --help

curl -OL http://ftpmirror.gnu.org/libtool/libtool-2.4.2.tar.gz
tar -xzf libtool-2.4.2.tar.gz
cd libtool-2.4.2
./configure && make && sudo make install

# brew install 'https://raw.github.com/simonair/homebrew-dupes/e5177ef4fc82ae5246842e5a544124722c9e975b/ab.rb'
# brew test ab

curl -O https://archive.apache.org/dist/httpd/httpd-2.4.2.tar.bz2
tar zxvf httpd-2.4.2.tar.bz2
cd httpd-2.4.2.tar.bz2
./configure && make && make install
```

### Windows

Windows 下想使用 `ab` 时，可从 [官方文档](https://httpd.apache.org/docs/current/platform/windows.html#down) 中链接的一些提供 Apache HTTP Server 二进制发布包下载的站点下载压缩包，并在解压后将 `bin/ab.exe` 文件提取至目标机器使用即可。

或使用从 [Apache Lounge](https://www.apachelounge.com/download/) 下载的 [Apache 2.4.54 Win64](https://www.apachelounge.com/download/VS16/binaries/httpd-2.4.54-win64-VS16.zip) 包中提取的这个 [ab.exe](/contents/apache-bench/ab.exe)。**下载后运行前注意检查文件 md5 值：`02bd1adc173c5b21172a6babaef3009f` 。**


## 使用

查看版本：

```bash
$ ab -V
This is ApacheBench, Version 2.3 <$Revision: 1879490 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/
```

基本用法：`ab [options] [http[s]://]hostname[:port]/path`

查看参数：

```bash
$ ab -h
Usage: ab [options] [http[s]://]hostname[:port]/path
Options are:
    -n requests     Number of requests to perform
    -c concurrency  Number of multiple requests to make at a time
    -t timelimit    Seconds to max. to spend on benchmarking
                    This implies -n 50000
    -s timeout      Seconds to max. wait for each response
                    Default is 30 seconds
    -b windowsize   Size of TCP send/receive buffer, in bytes
    -B address      Address to bind to when making outgoing connections
    -p postfile     File containing data to POST. Remember also to set -T
    -u putfile      File containing data to PUT. Remember also to set -T
    -T content-type Content-type header to use for POST/PUT data, eg.
                    'application/x-www-form-urlencoded'
                    Default is 'text/plain'
    -v verbosity    How much troubleshooting info to print
    -w              Print out results in HTML tables
    -i              Use HEAD instead of GET
    -x attributes   String to insert as table attributes
    -y attributes   String to insert as tr attributes
    -z attributes   String to insert as td or th attributes
    -C attribute    Add cookie, eg. 'Apache=1234'. (repeatable)
    -H attribute    Add Arbitrary header line, eg. 'Accept-Encoding: gzip'
                    Inserted after all normal header lines. (repeatable)
    -A attribute    Add Basic WWW Authentication, the attributes
                    are a colon separated username and password.
    -P attribute    Add Basic Proxy Authentication, the attributes
                    are a colon separated username and password.
    -X proxy:port   Proxyserver and port number to use
    -V              Print version number and exit
    -k              Use HTTP KeepAlive feature
    -d              Do not show percentiles served table.
    -S              Do not show confidence estimators and warnings.
    -q              Do not show progress when doing more than 150 requests
    -l              Accept variable document length (use this for dynamic pages)
    -g filename     Output collected data to gnuplot format file.
    -e filename     Output CSV file with percentages served
    -r              Don't exit on socket receive errors.
    -m method       Method name
    -h              Display usage information (this message)
    -I              Disable TLS Server Name Indication (SNI) extension
    -Z ciphersuite  Specify SSL/TLS cipher suite (See openssl ciphers)
    -f protocol     Specify SSL/TLS protocol
                    (TLS1, TLS1.1, TLS1.2 or ALL)
    -E certfile     Specify optional client certificate chain and private key
```

## 示例

100 并发，持续 120 秒，添加两个 cookie 属性：

```bash
$ ab -t 120 -c 100 \
-C 'XSRF-TOKEN=xxxx-xxxx' \
-C 'SESSION=XXXX' \
'http://foo/bar'
```

100 并发，发送 1200 个请求，用 POST 方法发送 `msg.json` 文件，指定 Content-Type，通过 Header 添加 Cookie 及 Accept 属性：

```bash
$ ab -n 1200 -c 100 \
-p /path/to/msg.json \
-T application/json \
-H 'Accept: application/json, text/plain, */*' \
-H 'Cookie: XSRF-TOKEN=xxxx-xxxx; SESSION=XXXX' \
'http://foo/bar'
```

## 结果说明

使用 `ab` 执行性能测试后得到的结果如下：

```bash
$ ab -t 120 -c 5 -p msg.json -T application/json http://foo/bar
This is ApacheBench, Version 2.3 <$Revision: 1430300 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking foo (be patient)
Finished 1596 requests


Server Software:        Unknown
Server Hostname:        foo
Server Port:            80

Document Path:          /bar
Document Length:        884 bytes

Concurrency Level:      5
Time taken for tests:   120.057 seconds
Complete requests:      1596
Failed requests:        0
Write errors:           0
Total transferred:      1959888 bytes
Total body sent:        1212800
HTML transferred:       1410864 bytes
Requests per second:    13.29 [#/sec] (mean)
Time per request:       376.119 [ms] (mean)
Time per request:       75.224 [ms] (mean, across all concurrent requests)
Transfer rate:          15.94 [Kbytes/sec] received
                        9.87 kb/s sent
                        25.81 kb/s total

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        1    2  35.9      1    1017
Processing:   324  372  49.2    361     957
Waiting:      324  372  49.2    361     957
Total:        325  374  60.6    362    1383

Percentage of the requests served within a certain time (ms)
  50%    362
  66%    369
  75%    373
  80%    377
  90%    393
  95%    465
  98%    568
  99%    579
 100%   1383 (longest request)
```

主要关注的指标为 每秒请求数（Requests per second）和 请求平均响应时间（第一个 Time per request）。

结果里有两个 `Time per request` 指标：
* 第一个指标的计算公式为 `concurrency * timetaken * 1000 / done`，`timetaken` 的单位是秒，可以理解为用户所感受到的这个请求的响应时间（毫秒）
* 第二个指标的计算公式为 `timetaken * 1000 / done`，是指在多并发的场景下，服务器处理完这些（`done` 个）请求所花费的平均时间（毫秒）

各项指标的详细说明，可见 [官方文档](https://httpd.apache.org/docs/current/programs/ab.html#output)。