---
id: fix-cors-issues
title: "【转】跨域（CORS）问题分析与解决方案"
description: "给出了解决跨域问题的一些方案"
date: 2022.10.02 10:34
categories:
    - Web
tags: [Web, HTML, Spring]
keywords: CORS, fetch, @CrossFilter, Access-Control-Allow-Origin
cover: /contents/covers/fix-cors-issues.png
---

原文地址：[跨域（CORS）问题分析与解决方案](https://wyiyi.github.io/amber/2022/10/01/CROS/)

## 复现场景

新创建一个 VUE 工程，使用 fetch 函数（如下所示） 调用后台 GET 接口，希望能够在后台获得到响应。

````js
fetch('http://127.0.0.1:8080/api/amber/userinfo/hello')
  .then(response => response)
````

当浏览器访问：`http://127.0.0.1:8181/#/` 就出现了问题：后台能够接到请求，但返回响应被浏览器拦截。
查看浏览器的 NETWORK 中显示：
- Status code : 200
- Response 没有返回正确结果
- Console 报错：提示如下 :

````text
Access to fetch at 'http://127.0.0.1:8080/api/amber/userinfo/hello' from origin 'http://127.0.0.1:8081' has been blocked by CORS policy: 
No 'Access-Control-Allow-Origin' header is present on the requested resource. 
If an opaque response serves your needs, set the request's mode to 'no-cors' to fetch the resource with CORS disabled.
````

看报错信息，显然，遇到了跨域问题。根据浏览器策略，所以将请求拦截。
浏览器通过 URL 是否同源 判别我是否做了跨域的操作。

## origin（源）

在 [Origin 和 Site](https://mp.weixin.qq.com/s/8PY1NlT_dd5EIiLS5tHtHw) 中：

> 在 Web 中，origin（源）是指 协议（scheme）+ 主机名（host）+ 端口号（port）。
>
> 同源（Same origin），意味着 scheme/host/port 三元组完全相同。任意一部分不同，即为跨源（cross-origin，或称为跨域）。

前台地址：`http://127.0.0.1:8181/#/` ，后台地址：`http://127.0.0.1:8080/api/amber/userinfo/hello` ，
其中 端口号（port） 不同，协议（scheme）和 主机名（host） 一致，可见不同源，且进行了跨源操作。

## CORS

Cross-Origin Resource Sharing（CORS），跨源资源共享 或 跨域资源共享，是一种基于 HTTP Header 的机制，用来使服务端指定哪些其他的源可以从这个服务端加载资源。

CORS 在规范区分了预检请求、简单请求。了解 CORS 的工作原理，可以阅读 [CORS](https://mp.weixin.qq.com/s/fKm7aX5wfn9I6-sqfT1HHw) ，
或参阅 [规范](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS) 以获取更多详细信息。

为了允许跨域请求，需要添加 CORS 相关的 HTTP Header。如果在请求的响应中未匹配到 CORS 的 Header，浏览器会拒绝它们。

## CORS 解决方案

有时可能只有某一个或者部分接口允许跨域访问，也可能所有接口都需要允许。

根据作用域不同，分为局部解决方案和全局解决方案。

### 一、局部设置 CORS

#### 方法 1、响应上设置 CORS Header

在请求的响应头上设置：`Access-Control-Allow-Origin: *`。

````java
@GetMapping("/hello")
@ResponseStatus(HttpStatus.OK)
public String getUser(HttpServletResponse response){
   response.setHeader("Access-Control-Allow-Origin", "*");
   return "hello, amber!";
}
````

#### 方法 2、fetch 时关闭 CORS

在 fetch 请求上增加：`mode: 'no-cors'` 参数。

````js
fetch('http://127.0.0.1:8080/api/amber/userinfo/hello', {mode: 'no-cors'})
  .then(response => response)
````

#### 方法3、@CrossOrigin

Spring 从 4.2 版本后开始支持 [@CrossOrigin](https://docs.spring.io/spring-framework/docs/current/reference/html/web.html#mvc-cors-controller) 注解实现跨域，
这在一定程度上简化了我们实现跨域访问的开发成本，
在需要跨域访问的 **方法** 或者 **类** 加上该注解便可允许跨域访问。

①、@CrossOrigin 基于方法级别使用，如下所示：

````java
@RestController
@RequestMapping("/api/amber/userinfo")
public class UserInfoController {

    @GetMapping("/hello")
    @CrossOrigin
    @ResponseStatus(HttpStatus.OK)
    public String getUser(){
        return "hello, amber!";
    }
}
````

②、@CrossOrigin 在类级别也受支持，并由所有方法继承。如下所示：

````java
@CrossOrigin
@RestController
@RequestMapping("/api/amber/userinfo")
public class UserInfoController {

    @GetMapping("/hello")
    @ResponseStatus(HttpStatus.OK)
    public String getUser(){
        return "hello, amber!";
    }
}
````

### 二、全局设置 CORS

除了细粒度、基于注解的配置之外，有时可能还需要全局 CORS 配置。

#### 1、自定义 Filter/HandlerInterceptor

````java
@WebFilter(filterName = "corsFilter", urlPatterns = {"/*"})
@Component
public class CORSConfig implements Filter {

    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) throws IOException, ServletException {
        HttpServletResponse res = (HttpServletResponse) response;
        res.setHeader("Access-Control-Allow-Credentials", String.valueOf(true));
        res.setHeader("Access-Control-Allow-Headers", "Content-Type,Access-Token,Authorization,ybg");
        res.setHeader("Access-Control-Allow-Methods", "POST, GET, OPTIONS, DELETE, PUT");
        res.setHeader("Access-Control-Allow-Origin", "*");
        res.setHeader("Access-Control-Max-Age", "3600");
        chain.doFilter(request, response);
    }
}
````

#### 2、CorsFilter

Spring 4.2 版本后内置了一个 [CorsFilter](https://docs.spring.io/spring-framework/docs/current/reference/html/web.html#mvc-cors-filter) 专门用于处理 CORS 请求问题，所在包的位置：`org.springframework.web.filter.CorsFilter`。

通过配置 CorsFilter 可实现基于 URL 级别控制跨域访问的范围。

````java
CorsConfiguration config = new CorsConfiguration();

// Possibly...
// config.applyPermitDefaultValues()

config.setAllowCredentials(true);
config.addAllowedOrigin("https://domain1.com");
config.addAllowedHeader("*");
config.addAllowedMethod("*");

UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
source.registerCorsConfiguration("/**", config);

CorsFilter filter = new CorsFilter(source);
````