---
id: hide-tomcat-server-info
title: "隐藏 Tomcat 版本信息"
description: "Error Report Valve"
date: 2023.10.22 10:26
categories:
    - Tomcat
tags: [Tomcat]
keywords: Tomcat, server info, Host, Valve, ErrorReportValve
cover: /contents/hide-tomcat-server-info/400-hide.png
---

访问 Tomcat 发布的应用中不存在的页面或 URL 中包含特殊字符时，会看到下面这样的界面：

http://localhost:8080/not-exist

![404](/contents/hide-tomcat-server-info/404.png)

`http://localhost:8080/([%5E`

![400](/contents/hide-tomcat-server-info/400.png)

如遇安全扫描等场景希望不暴露 Tomcat 版本信息时，可以在其配置文件 `conf/server.xml` 中的 `Host` 元素内添加如下内容：

```xml
<Valve className="org.apache.catalina.valves.ErrorReportValve" 
       showReport="false" showServerInfo="false" />
```

以截图中使用的 Tomcat 10.1.15 版本为例，原始的去掉注释部分的 `conf/server.xml` 内容如下：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Server port="8005" shutdown="SHUTDOWN">
  <Listener className="org.apache.catalina.startup.VersionLoggerListener" />
  <Listener className="org.apache.catalina.core.AprLifecycleListener" SSLEngine="on" />
  <Listener className="org.apache.catalina.core.JreMemoryLeakPreventionListener" />
  <Listener className="org.apache.catalina.mbeans.GlobalResourcesLifecycleListener" />
  <Listener className="org.apache.catalina.core.ThreadLocalLeakPreventionListener" />

  <GlobalNamingResources>
    <Resource name="UserDatabase" auth="Container"
              type="org.apache.catalina.UserDatabase"
              description="User database that can be updated and saved"
              factory="org.apache.catalina.users.MemoryUserDatabaseFactory"
              pathname="conf/tomcat-users.xml" />
  </GlobalNamingResources>

  <Service name="Catalina">

    <Connector port="8080" protocol="HTTP/1.1"
               connectionTimeout="20000"
               redirectPort="8443"
               maxParameterCount="1000"
               />
    <Engine name="Catalina" defaultHost="localhost">

      <Realm className="org.apache.catalina.realm.LockOutRealm">
        <Realm className="org.apache.catalina.realm.UserDatabaseRealm"
               resourceName="UserDatabase"/>
      </Realm>

      <Host name="localhost"  appBase="webapps"
            unpackWARs="true" autoDeploy="true">

        <Valve className="org.apache.catalina.valves.AccessLogValve" directory="logs"
               prefix="localhost_access_log" suffix=".txt"
               pattern="%h %l %u %t &quot;%r&quot; %s %b" />

      </Host>
    </Engine>
  </Service>
</Server>
```

添加 `Valve` 后为：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Server port="8005" shutdown="SHUTDOWN">
  <Listener className="org.apache.catalina.startup.VersionLoggerListener" />
  <Listener className="org.apache.catalina.core.AprLifecycleListener" SSLEngine="on" />
  <Listener className="org.apache.catalina.core.JreMemoryLeakPreventionListener" />
  <Listener className="org.apache.catalina.mbeans.GlobalResourcesLifecycleListener" />
  <Listener className="org.apache.catalina.core.ThreadLocalLeakPreventionListener" />

  <GlobalNamingResources>
    <Resource name="UserDatabase" auth="Container"
              type="org.apache.catalina.UserDatabase"
              description="User database that can be updated and saved"
              factory="org.apache.catalina.users.MemoryUserDatabaseFactory"
              pathname="conf/tomcat-users.xml" />
  </GlobalNamingResources>

  <Service name="Catalina">

    <Connector port="8080" protocol="HTTP/1.1"
               connectionTimeout="20000"
               redirectPort="8443"
               maxParameterCount="1000"
               />
    <Engine name="Catalina" defaultHost="localhost">

      <Realm className="org.apache.catalina.realm.LockOutRealm">
        <Realm className="org.apache.catalina.realm.UserDatabaseRealm"
               resourceName="UserDatabase"/>
      </Realm>

      <Host name="localhost"  appBase="webapps"
            unpackWARs="true" autoDeploy="true">

        <Valve className="org.apache.catalina.valves.AccessLogValve" directory="logs"
               prefix="localhost_access_log" suffix=".txt"
               pattern="%h %l %u %t &quot;%r&quot; %s %b" />

        <Valve className="org.apache.catalina.valves.ErrorReportValve" 
               showReport="false" showServerInfo="false" />

      </Host>
    </Engine>
  </Service>
</Server>
```

隐藏后效果如下：

![404-hide](/contents/hide-tomcat-server-info/404-hide.png)

![400-hide](/contents/hide-tomcat-server-info/400-hide.png)


Error Report Valve
------------------

关于 `ErrorReportValve` 的用法，可参照 Tomcat 对应版本的官方文档，如：https://tomcat.apache.org/tomcat-10.1-doc/config/valve.html#Error_Report_Valve

![ErrorReportValve](/contents/hide-tomcat-server-info/ErrorReportValve.png)


特殊字符
-------

如果不想上例中的包含特殊字符的请求（`http://localhost:8080/([%5E`）被 Tomcat 拒绝至 400 错误页，可通过 Tomcat HTTP Connector 的 [标准实现](https://tomcat.apache.org/tomcat-10.1-doc/config/http.html#Standard_Implementation) 中的 `relaxedPathChars` 和 `relaxedQueryChars` 参数配置在请求路径和查询字符串中允许的特殊字符，例如下面的配置可以使 `http://localhost:8080/([%5E` 请求跳转到 404 错误页不是默认的 400 错误页。

```xml
<Connector port="8080" protocol="HTTP/1.1"
            connectionTimeout="20000"
            redirectPort="8443"
            maxParameterCount="1000"
            relaxedPathChars="&lt;>[\]^`{|}"
            />
```

> [系统参数](https://tomcat.apache.org/tomcat-8.5-doc/config/systemprops.html#Other) 中的 `tomcat.util.http.parser.HttpParser.requestTargetAllow` 配置项在 Tomcat 8 中声明弃用，被 `relaxedPathChars` 和 `relaxedQueryChars` Connector 属性取代。