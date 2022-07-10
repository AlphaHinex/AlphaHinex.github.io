---
id: spring-webmvc-interceptor
title: "【转】Spring 之 Interceptor"
description: "在 Spring Web MVC 中，拦截器（Interceptor）同 Servlet 中的过滤器（Filter）类似，都可以实现对用户的请求做出相应的处理。"
date: 2022.07.10 10:26
categories:
    - Spring
tags: [Spring, Servlet, Java]
keywords: Web MVC, interceptor, filter
cover: /contents/covers/spring-webmvc-interceptor.png
---

原文地址：https://wyiyi.github.io/amber/2022/07/01/interceptor/

### 什么是拦截器
在 Spring Web MVC 中，拦截器（Interceptor）同 [Servlet 中的过滤器（Filter）](https://wyiyi.github.io/amber/2021/10/01/filter/) 类似，都可以实现对用户的请求做出相应的处理。

所有 `HandlerMapping` 的实现都支持处理程序拦截器，当想将特定功能应用于某些请求时很有用 —— 例如检查权限。
拦截器必须实现 `org.springframework.web.servlet` 包中 `HandlerInterceptor` 接口的三个方法，
这些方法能够提供足够的灵活性来进行各种预处理和后处理：

> preHandle(..): Before the actual handler is run   // 在实际 handler 之前运行
>
> postHandle(..): After the handler is run  // 在 handler 之后运行
>
> afterCompletion(..): After the complete request has finished   // 在整个请求完成后运行

preHandle 方法返回一个布尔值，可以用该方法中断或者继续执行链的处理。
- 当返回 true 时，执行链会继续执行； 
- 当返回 false 时，DispatcherServlet 假定拦截器本身已经处理了请求（例如，呈现了适当的视图）并且不会继续执行其他拦截器和执行链中的实际处理程序。

【注意】：`postHandle` 对于 `@ResponseBody` 和 `ResponseEntity` 方法的用处不大，因为这些方法的响应是在 `HandlerAdapter` 中和 `postHandle` 之前写入和提交的。
[这意味着对响应进行任何更改都为时已晚，例如添加额外的请求头。](https://stackoverflow.com/questions/2030152/cannot-set-header-in-jsp-response-already-committed)
对于此类场景，您可以实现 `ResponseBodyAdvice` 并将其声明为 `Controller Advice` bean 或直接在 `RequestMappingHandlerAdapter` 上进行配置。


### 自定义拦截器

1、定义拦截器：监控请求时间

- 在进入处理器之前记录开始时间，即在拦截器的 preHandle 记录开始时间；
- 在结束请求处理之后记录结束时间，即在拦截器的 afterCompletion 记录结束实现，并用结束时间-开始时间得到这次请求的处理时间。

```java
@Component
public class TimeTrackingInterceptor implements HandlerInterceptor {

    private static Logger log = LoggerFactory.getLogger(TimeTrackingInterceptor.class);
    private static final ThreadLocal<Long> logTimeThreadLocal = new NamedThreadLocal<>("ThreadLocal StartTime");

    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
        long beginTime = System.currentTimeMillis();
        logTimeThreadLocal.set(beginTime);
        log.info(request.getRequestURI() + " 开始执行时间：" + beginTime);
        return true;
    }

    public void postHandle(HttpServletRequest request, HttpServletResponse response, Object handler, ModelAndView modelAndView) throws Exception {
    }

    public void afterCompletion(HttpServletRequest request, HttpServletResponse response, Object handler, Exception ex) throws Exception {
        long beginTime = logTimeThreadLocal.get();
        long endTime = System.currentTimeMillis();
        log.info(request.getRequestURI() + " 执行结束时间：" + endTime);
        log.info("耗时：" + (endTime - beginTime) + "ms");
    }
}
```
2、controller 类
```java
@RestController
public class InterceptorController {

    @RequestMapping("/index")
    public Map<String,String> hello(Model model){
        Map<String,String> response=new HashMap<>();
        response.put("msg","hello");
        return response;
    }
}
```
### 配置拦截器
有关如何配置拦截器的示例，[可参阅 MVC 配置部分中的拦截器](https://docs.spring.io/spring-framework/docs/current/reference/html/web.html#mvc-config-interceptors)。

能够使 TimeTrackingInterceptor 拦截到 /index 生效，将 TimeTrackingInterceptor 注册拦截器配置中即可。

```java
@Configuration
public class InterceptorConfig implements WebMvcConfigurer {
    private final TimeTrackingInterceptor timeTrackingInterceptor;

    public InterceptorConfig(TimeTrackingInterceptor timeTrackingInterceptor) {
        this.timeTrackingInterceptor = timeTrackingInterceptor;
    }

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(timeTrackingInterceptor).addPathPatterns("/index");
    }

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        registry.addResourceHandler("/**").addResourceLocations("classpath:/my/");
    }

}
```
### 启动应用，运行效果

启动后通过访问 http://127.0.0.1:8080/index ，发现已经拦截到请求，在控制台日志中打印了上述日志信息。

![](https://wyiyi.github.io/amber/contents/interceptor/127001.png)

![](https://wyiyi.github.io/amber/contents/interceptor/logs.png)

### 参考资料

* [Interceptor 官方文档](https://docs.spring.io/spring-framework/docs/current/reference/html/web.html#mvc-handlermapping-interceptor)
* [Interceptor 拦截器配置](https://docs.spring.io/spring-framework/docs/current/reference/html/web.html#mvc-config-interceptors)
