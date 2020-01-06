---
id: using-gradle-behind-proxy
title:  "Using Gradle Behind Proxy"
date:   2020.01.06
categories: Java
tags: [Proxy, Gradle, Java]
cover: https://www.ionos.com/digitalguide/fileadmin/DigitalGuide/Teaser/proxy-t.jpg
---

在网络代理环境下使用 Gradle 时，可能会遇到以下三个问题：
1. `gradlew` 下载对应 Gradle 发布版时无法下载
2. 下载依赖时，提示连接超时
3. SSL 证书无效


`gradlew` 下载对应 Gradle 发布版时无法下载
--------------------------------------

### 错误提示

`Unable to tunnel through proxy. Proxy returns "HTTP/1.1 407 Proxy Authorization Required"`

### 原因

wrapper 下载发布包时也需要配置代理

### 解决办法

试遍各种为 wrapper 配置代理的方法，均无果。用最直接的办法：按照 `gradle.properties` 中 `distributionUrl` 路径，手动下载好发布包，放到 wrapper 自动创建的路径下（如：`~/.gradle/wrapper/dists/gradle-6.0.1-all/99d3u8wxs16ndehh90lbbir67`），继续执行 gradlew 命令即可。


下载依赖时，提示连接超时
--------------------

### 错误提示

`> Connection timed out: connect`

### 原因

需为 Gradle 配置代理参数

### 解决办法

在 `gradle.properties` 中添加如下内容（注意修改各参数值）：

```properties
systemProp.http.proxyHost=www.somehost.org
systemProp.http.proxyPort=8080
systemProp.http.proxyUser=userid
systemProp.http.proxyPassword=password
systemProp.http.nonProxyHosts=*.nonproxyrepos.com|localhost

systemProp.https.proxyHost=www.somehost.org
systemProp.https.proxyPort=8080
systemProp.https.proxyUser=userid
systemProp.https.proxyPassword=password
systemProp.https.nonProxyHosts=*.nonproxyrepos.com|localhost
```


SSL 证书无效
-----------

### 错误提示

`> sun.security.validator.ValidatorException: PKIX path building failed: sun.security.provider.certpath.SunCertPathBuilderException: unable to find valid certification path to requested target`

### 原因

错误提示中，`unable to find valid certification path` 和 `PKIX path building failed` 表明了这是因 SSL 证书引起的问题。
在通过代理访问网络时，可能需要在本地添加需要信任的根证书（在未添加根证书并信任时，无法通过浏览器访问 https 站点）。
在此种环境下，需要为 Gradle 所使用的 Java 也进行类似操作，才能通过 Java 代码访问 https 资源（如：https://plugins.gradle.org/）。

### 解决办法

#### 1. 确定 Gradle 所使用的 Java 路径

先找到 Gradle 所使用的 Java home，可通过 `./gradlew -v` 查看所使用的 Java 版本。

#### 2. 查看 JDK 中已存在的证书

假设已定义了环境变量 `JAVA_HOME` 代表 JDK 安装路径，可通过如下命令查看 keystore 中已经存在的证书：

```bash
$ keytool -list -keystore $JAVA_HOME/jre/lib/security/cacerts
```

提示需要输入密码时，直接回车即可。

#### 3. 导入新证书

将网络代理方提供的根证书导入到 keystore 中（注意修改 `<>` 中变量）：

```bash
$ sudo keytool -import -alias <alias> -keystore $JAVA_HOME/jre/lib/security/cacerts -file </path/to/cert/file>
```

默认密码：`changeit`

#### 4. 配置信任证书

证书导入至 keystore 之后，还需将其加入 truststore。

在 `gradle.properties` 中添加如下内容（注意修改 `<>` 中内容）：

```properties
systemProp.javax.net.ssl.trustStore=<JAVA_HOME>/jre/lib/security/cacerts
systemProp.javax.net.ssl.trustStorePassword=changeit
```

配置完成后，可能需要重新开启终端，继续执行 Gradle 命令，即可生效。


参考资料
-------

1. [Solutions for “Unable to resolve dependency” on building with Android Studio 3.0](https://www.cresco.co.jp/blog/entry/2014/)
1. [AndroidStudio构建项目异常:PKIX path building failed: sun.security.provider.certpath.SunCertPathBuilderE...](https://www.jianshu.com/p/60278f144fc6)
1. [import a .cer file to .keysore file](http://www.voidcn.com/article/p-shfykodk-pw.html)
1. [Truststore setup for gradle plugin in IntelliJ](https://stackoverflow.com/questions/52779083/truststore-setup-for-gradle-plugin-in-intellij)
1. [How to tell Maven to disregard SSL errors (and trusting all certs)?](https://stackoverflow.com/questions/21252800/how-to-tell-maven-to-disregard-ssl-errors-and-trusting-all-certs)
