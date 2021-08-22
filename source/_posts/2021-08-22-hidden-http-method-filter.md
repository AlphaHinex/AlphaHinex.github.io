---
id: hidden-http-method-filter
title: "HTML <form> 只支持 GET 和 POST！"
description: "这很不 RESTful"
date: 2021.08.22 10:26
categories:
    - Spring
tags: [HTML, Spring]
keywords: RESTful, HTML, form, method, get, post, delete, put, HiddenHttpMethodFilter, MultipartFilter
cover: /contents/covers/hidden-http-method-filter.png
---

HTML form method
================

在 Web 开发中，常规的提交数据方式为使用 `form` 表单，例如：

```html
<form action="" method="get" class="form-example">
  <div class="form-example">
    <label for="name">Enter your name: </label>
    <input type="text" name="name" id="name" required>
  </div>
  <div class="form-example">
    <label for="email">Enter your email: </label>
    <input type="email" name="email" id="email" required>
  </div>
  <div class="form-example">
    <input type="submit" value="Subscribe!">
  </div>
</form>
```

`form` 中各属性的值，可参考 [MDN 文档](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/form)，其中，`method` 属性支持的值如下：

> `method`
>
> The HTTP method to submit the form with. Possible (case insensitive) values:
> * `post`: The POST method; form data sent as the request body.
> * `get`: The GET method; form data appended to the action URL with a ? separator. Use this method when the form has no side-effects.
> * `dialog`: When the form is inside a \<dialog>, closes the dialog on submission.

这在 JSP 时代通常只使用 `get` 和 `post` 两种 method 时并无大碍，但在 RESTful 盛行的今日，无疑显得很不和谐。

Spring 的解决方式
===============

在 Spring 提供的 [form 标签库](https://docs.spring.io/spring-framework/docs/5.2.16.RELEASE/spring-framework-reference/web.html#mvc-view-jsp-formtaglib) 中，对 HTML 中的 form 进行了全面的丰富，在 JSP 页面中引入 taglib：

```JSP
<%@ taglib prefix="form" uri="http://www.springframework.org/tags/form" %>
```

之后可以通过 `<form:form>` 的方式使用，如：

```html
<form:form method="delete">
    <p class="submit"><input type="submit" value="Delete Pet"/></p>
</form:form>
```

`<form:form>` 最终也会被服务端渲染为 `<form>`，那为什么这里的 `method` 不再局限于 HTML 规范中要求的值呢？

HiddenHttpMethodFilter
----------------------

在 Spring 中，使用了一种 [HTTP Method 转换方式](https://docs.spring.io/spring-framework/docs/5.2.16.RELEASE/spring-framework-reference/web.html#mvc-rest-method-conversion)：以上面代码片段为例，实际提交的表单的 method 是 `POST` 类型的，同时在请求参数中包含了一个隐藏的属性，默认为 `_method`，里面存放了真正的 method —— `DELETE`。

在服务端，接收请求时，有一个 [HiddenHttpMethodFilter](https://github.com/spring-projects/spring-framework/blob/v5.2.16.RELEASE/spring-web/src/main/java/org/springframework/web/filter/HiddenHttpMethodFilter.java)，负责将请求的 method 修改为隐藏属性中的实际 method，再传入后续处理流程，以使得我们的 Controller 能够使用 `@DeleteMapping` 接收到请求。

```java
@Override
protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
        throws ServletException, IOException {

    HttpServletRequest requestToUse = request;

    if ("POST".equals(request.getMethod()) && request.getAttribute(WebUtils.ERROR_EXCEPTION_ATTRIBUTE) == null) {
        String paramValue = request.getParameter(this.methodParam);
        if (StringUtils.hasLength(paramValue)) {
            String method = paramValue.toUpperCase(Locale.ENGLISH);
            if (ALLOWED_METHODS.contains(method)) {
                requestToUse = new HttpMethodRequestWrapper(request, method);
            }
        }
    }

    filterChain.doFilter(requestToUse, response);
}
```

一切都还挺美好的，直到……

上传文件为空
----------

Spring 中，需要上传文件时，又同时使用了 `HiddenHttpMethodFilter`，如果配置不当，大概率会遇到 Controller 中接到的 MultipartFile 为空的情况。在 `HiddenHttpMethodFilter` 的 [源码](https://github.com/spring-projects/spring-framework/blob/v5.2.16.RELEASE/spring-web/src/main/java/org/springframework/web/filter/HiddenHttpMethodFilter.java#L48-L51) 中，其实已经说明了这个问题：

> NOTE: This filter needs to run after multipart processing in case of a multipart POST request, due to its inherent need for checking a POST body parameter. So typically, put a Spring org.springframework.web.multipart.support.MultipartFilter before this HiddenHttpMethodFilter in your web.xml filter chain.

只需要让处理上传文件的 Filter 先于处理 HTTP method 隐藏属性的 Filter 即可。