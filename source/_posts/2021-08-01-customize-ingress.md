---
id: customize-ingress
title: "Ingress 定制配置"
description: "最大化 Ingress 价值"
date: 2021.08.01 10:34
categories:
    - K8s
tags: [K8s, Nginx]
keywords: K8s, Ingress, Ingress Controller, ingress-nginx, KIC, Kong Ingress Controller
cover: /contents/covers/customize-ingress.jpeg
---

[K8s Ingress、Ingress Controller 和 Ingress Class](https://alphahinex.github.io/2021/07/11/ingress-ingress-controller-ingress-class/) 中介绍了 Ingress 相关的概念，接下来让我们看看如何对 Ingress 进行更加灵活的配置。

## Ingress 本身支持的配置

Ingress 的特性至 Kubernetes v1.19 进入了稳定状态，不论使用哪个具体的 Ingress Controller，这些配置都是生效的。

### [Path types](https://kubernetes.io/docs/concepts/services-networking/ingress/#path-types)

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: minimal-ingress
spec:
  rules:
  - http:
      paths:
      - path: /testpath
        pathType: Prefix
        backend:
          service:
            name: test
            port:
              number: 80
```

Ingress 中的每个 `path` 都需要有一个对应的 `pathType`，共有三种类型：

1. `ImplementationSpecific`: 这种类型的路径匹配规则依赖具体的 Ingress Controller 实现，具体实现可以将此类型作为一个单独的类型来对待，也可以将其视为 `Prefix` 或 `Exact` 类型
1. `Exact`: 完全匹配，区分大小写
1. `Prefix`: 按前缀匹配，区分大小写，前缀部分（可补充或去掉结尾的 `/`）需完全匹配

例如：

|path type|Path(s)|请求路径|是否匹配|
|:--------|:------|:------|:-----|
|Prefix|/|任意路径|匹配|
|Exact|/foo|/foo|匹配|
|Exact|/foo|/bar|不匹配|
|Exact|/foo|/foo/|不匹配|
|Exact|/foo/|/foo|不匹配|
|Prefix|/foo|/foo, /foo/|匹配|
|Prefix|/foo/|/foo, /foo/|匹配|
|Prefix|/aaa/bb|/aaa/bbb|不匹配|
|Prefix|/aaa/bbb|/aaa/bbb|匹配|
|Prefix|/aaa/bbb/|/aaa/bbb|匹配，可忽略结尾的 /|
|Prefix|/aaa/bbb|/aaa/bbb/|匹配，可补充结尾的 /|
|Prefix|/aaa/bbb|/aaa/bbb/ccc|匹配|
|Prefix|/aaa/bbb|/aaa/bbbxyz|不匹配，因为前缀未完全匹配|
|Prefix|/, /aaa|/aaa/ccc|匹配，与 /aaa 匹配|
|Prefix|/, /aaa, /aaa/bbb|/aaa/bbb|匹配，与 /aaa/bbb 匹配|
|Prefix|/, /aaa, /aaa/bbb|/ccc|匹配，与 / 匹配|
|Prefix|/aaa|/ccc|不匹配|
|Mixed|/foo (Prefix), /foo (Exact)|/foo|匹配，优先 Exact 类型匹配|

### [Hostname wildcards](https://kubernetes.io/docs/concepts/services-networking/ingress/#hostname-wildcards)

主机名支持完全匹配和通配符匹配两种：

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-wildcard-host
spec:
  rules:
  - host: "foo.bar.com"
    http:
      paths:
      - pathType: Prefix
        path: "/bar"
        backend:
          service:
            name: service1
            port:
              number: 80
  - host: "*.foo.com"
    http:
      paths:
      - pathType: Prefix
        path: "/foo"
        backend:
          service:
            name: service2
            port:
              number: 80
```

**注意：host 中包含通配符时，通配符必须放在起始位置，即不可以设置为 `foo.*.com`**

|Host|请求中的 Host 头|是否匹配|
|:---|:-------------|:------|
|*.foo.com|bar.foo.com|匹配|
|*.foo.com|baz.bar.foo.com|不匹配，通配符仅覆盖了一个 DNS 标签|
|*.foo.com|foo.com|不匹配|

> 上述表格为 [官方文档](https://kubernetes.io/docs/concepts/services-networking/ingress/#hostname-wildcards) 中给出的例子，但实际验证时发现，使用 [简单，却伟大](https://alphahinex.github.io/2021/06/06/simple-but-powerful/) 里面提到的 `nip.io` 作为 host 时，`*.test.192.168.34.26.nip.io` 可以匹配到 `foo.bar.test.192.168.34.26.nip.io`、`another.foo.bar.test.192.168.34.26.nip.io` 等。


## Ingress Controller 提供的配置

除了 Ingress 资源上的通用配置外，我们还可以针对所使用的具体的 Ingress Controller，通过注解的方式添加更灵活且丰富的配置。

这些注解通常由具体的 Controller 所提供，例如：

* `ingress-nginx` 所提供的 https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/annotations/
* Kong 的 `Kubernetes Ingress Controller` 所提供的 https://docs.konghq.com/kubernetes-ingress-controller/latest/references/annotations/

## ingress-nginx

接下来让我们浏览几个 `ingress-nginx` 中的常用注解的作用及用法。

### [Rewrite Target](https://github.com/kubernetes/ingress-nginx/blob/master/docs/examples/rewrite/README.md#rewrite-target)

从 ingress-nginx `0.22.0` 版本起，使用 `nginx.ingress.kubernetes.io/rewrite-target` 注解进行重写目标地址的配置，并且请求路径中的任意要在重写的路径中子路径，都必须明确的通过正则表达式的 [捕获组](https://www.regular-expressions.info/refcapture.html) 进行定义。捕获组以数字进行占位，按定义的先后顺序，表示为 `$1`, `$2` ... `$n`。

```yaml
kind: Ingress
apiVersion: networking.k8s.io/v1
metadata:
  name: rewrite-demo
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /demo/demo-ui/$2
spec:
  rules:
    - host: rewrite.bar.com
      http:
        paths:
          - path: /demo-ui(/|$)(.*)
            pathType: ImplementationSpecific
            backend:
              serviceName: demo-ui
              servicePort: 8080
```

在上面的配置中，请求路径 `/demo-ui/` 后面的部分都会被 `$2` 所捕获，并作为参数传入 `rewrite-target` 注解中。

例如：

* 请求 `rewrite.bar.com/demo-ui` 会转给 `rewrite.bar.com/demo/demo-ui/`
* 请求 `rewrite.bar.com/demo-ui/` 会转给 `rewrite.bar.com/demo/demo-ui/`
* 请求 `rewrite.bar.com/demo-ui/new` 会转给 `rewrite.bar.com/demo/demo-ui/new`

### [App Root](https://github.com/kubernetes/ingress-nginx/blob/master/docs/examples/rewrite/README.md#app-root)

使用 `nginx.ingress.kubernetes.io/app-root` 注解可以设定根路径，例如：

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    nginx.ingress.kubernetes.io/app-root: /app1
  name: approot
  namespace: default
spec:
  rules:
  - host: approot.bar.com
    http:
      paths:
      - backend:
          serviceName: http-svc
          servicePort: 80
        pathType: ImplementationSpecific
        path: /
```

此时，对 http://approot.bar.com/ 的访问，会被重定向到 http://approot.bar.com/app1 ，响应的 HTTP Status 是 `302 Moved Temporarily`。

### [Custom max body size](https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/annotations/#custom-max-body-size)

`nginx.ingress.kubernetes.io/proxy-body-size` 注解等同于 Nginx 中的 `client_max_body_size`，可以设定允许的 request body 大小：

例如：

`nginx.ingress.kubernetes.io/proxy-body-size: 8m`