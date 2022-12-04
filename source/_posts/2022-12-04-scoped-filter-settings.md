---
id: scoped-filter-settings
title: "为非全局路径配置 Filter 的两种方法"
description: "设置非全局路径的过滤器时，注意不要 @WebFilter 和 @Component 一起使用"
date: 2022.12.04 10:34
categories:
    - Spring
tags: [Spring, Servlet]
keywords: Filter, Spring, Spring Boot, Servlet, @WebFilter, @Component, FilterRegistrationBean
cover: /contents/scoped-filter-settings/cover.jpg
---

原文地址：https://wyiyi.github.io/amber/2022/12/01/filter-note/

## 一、@WebFilter

Filter 上加 @WebFilter (javax.servlet.annotation.WebFilter)，指定 value，启动类加 @ServletComponentScan

【注意】：[@ServletComponentScan 这个注解仅对内嵌的 tomcat 生效，如果使用单独的 tomcat，这种方式无效](https://docs.spring.io/spring-boot/docs/2.0.9.RELEASE/reference/htmlsingle/#boot-features-embedded-container-servlets-filters-listeners-scanning)。

示例一：

````java
@WebFilter(filterName = "aFilter", value = "/api/amber/*")
public class AFilter implements Filter {
    
    private static final Logger LOGGER = LoggerFactory.getLogger(AFilter.class);
    
    @Autowired
    private UserService userService;
    
    @Override
    public void init(FilterConfig filterConfig) {
        LOGGER.info("A Filter初始化,只初始化一次...");
    }
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) throws IOException, ServletException {
        LOGGER.info("AFilter 处理中...");
        User user = userService.getUserInfo();
        LOGGER.info("USER 信息：" +  user);
        HttpServletRequest servletRequest = (HttpServletRequest) request;
        LOGGER.info(String.valueOf(servletRequest.getRequestURL()));
        chain.doFilter(request, response);
    }
    @Override
    public void destroy() {
        LOGGER.info("A Filter销毁...");
    }
}
````

示例二：

````java
@SpringBootApplication
@ServletComponentScan
@MapperScan({"com.amber.common.dao"})
public class BronzeApplication {
	public static void main(String[] args) {
		SpringApplication.run(BronzeApplication.class, args);
	}
}
````

示例三：

````log
2022-12-01 12:28:38.785  INFO 7052 --- [           main] com.amber.common.filter.AFilter          : A Filter初始化,只初始化一次...
2022-12-01 12:28:39.827  INFO 7052 --- [           main] com.amber.common.BronzeApplication       : Started BronzeApplication in 2.267 seconds (JVM running for 2.808)
2022-12-01 12:28:44.342  INFO 7052 --- [nio-8080-exec-1] o.a.c.c.C.[Tomcat].[localhost].[/]       : Initializing Spring DispatcherServlet 'dispatcherServlet'
2022-12-01 12:28:44.342  INFO 7052 --- [nio-8080-exec-1] o.s.web.servlet.DispatcherServlet        : Initializing Servlet 'dispatcherServlet'
2022-12-01 12:28:44.345  INFO 7052 --- [nio-8080-exec-1] o.s.web.servlet.DispatcherServlet        : Completed initialization in 3 ms
2022-12-01 12:28:44.350  INFO 7052 --- [nio-8080-exec-1] com.amber.common.filter.AFilter          : AFilter 处理中...
2022-12-01 12:28:44.350  INFO 7052 --- [nio-8080-exec-1] com.amber.common.filter.AFilter          : USER 信息：User(screen_name=amber, text=今天星期四, created_at=Thu Dec 01 12:28:44 CST 2022)
2022-12-01 12:28:44.350  INFO 7052 --- [nio-8080-exec-1] com.amber.common.filter.AFilter          : http://localhost:8080/api/amber/weibo
````

可以看到输出日志是正确的。

## 二、@Component + FilterRegistrationBean

在 Filter 上加 @Component ，通过 FilterRegistrationBean addUrlPatterns 进行实例注册。

示例一：

````java
@Component
public class AFilter implements Filter {
    private static final Logger LOGGER = LoggerFactory.getLogger(AFilter.class);
    @Autowired
    private UserService userService;
    @Override
    public void init(FilterConfig filterConfig) {
        LOGGER.info("A Filter初始化,只初始化一次...");
    }
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) throws IOException, ServletException {
        LOGGER.info("AFilter 处理中...");
        User user = userService.getUserInfo();
        LOGGER.info("USER 信息：" +  user);
        HttpServletRequest servletRequest = (HttpServletRequest) request;
        LOGGER.info(String.valueOf(servletRequest.getRequestURL()));
        chain.doFilter(request, response);
    }
    @Override
    public void destroy() {
        LOGGER.info("A Filter销毁...");
    }
}
````

示例二：

````java
@Configuration
public class ComponentFilterOrderConfig {
    @Bean
    public FilterRegistrationBean filterBeanOne(AFilter aFilter) {
        FilterRegistrationBean filterRegistrationBean = new FilterRegistrationBean();
        filterRegistrationBean.setFilter(aFilter);
        filterRegistrationBean.addUrlPatterns("/api/amber/*");
        filterRegistrationBean.setName("aFilter");
        return filterRegistrationBean;
    }
}
````

示例三：

````log
2022-12-01 12:34:48.366  INFO 16188 --- [           main] com.amber.common.filter.AFilter          : A Filter初始化,只初始化一次...
2022-12-01 12:34:49.458  INFO 16188 --- [           main] com.amber.common.BronzeApplication       : Started BronzeApplication in 2.283 seconds (JVM running for 2.816)
2022-12-01 12:34:54.176  INFO 16188 --- [nio-8080-exec-1] o.a.c.c.C.[Tomcat].[localhost].[/]       : Initializing Spring DispatcherServlet 'dispatcherServlet'
2022-12-01 12:34:54.176  INFO 16188 --- [nio-8080-exec-1] o.s.web.servlet.DispatcherServlet        : Initializing Servlet 'dispatcherServlet'
2022-12-01 12:34:54.180  INFO 16188 --- [nio-8080-exec-1] o.s.web.servlet.DispatcherServlet        : Completed initialization in 4 ms
2022-12-01 12:34:54.184  INFO 16188 --- [nio-8080-exec-1] com.amber.common.filter.AFilter          : AFilter 处理中...
2022-12-01 12:34:54.184  INFO 16188 --- [nio-8080-exec-1] com.amber.common.filter.AFilter          : USER 信息：User(screen_name=amber, text=今天星期四, created_at=Thu Dec 01 12:34:54 CST 2022)
2022-12-01 12:34:54.184  INFO 16188 --- [nio-8080-exec-1] com.amber.common.filter.AFilter          : http://localhost:8080/api/amber/weibo
````

可以看到输出日志是正确的。

## 三、前方高能：@WebFilter + @Component 同时使用

切莫 @WebFilter 指定 value 后又加 @Component，会注册两个 filter，导致走两次

示例一：

````java
@Component
@WebFilter(filterName = "aFilter", value = "/api/amber/*")
public class AFilter implements Filter {
    
    private static final Logger LOGGER = LoggerFactory.getLogger(AFilter.class);
    
    @Autowired
    private UserService userService;
    
    @Override
    public void init(FilterConfig filterConfig) {
        LOGGER.info("A Filter初始化,只初始化一次...");
    }
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) throws IOException, ServletException {
        LOGGER.info("AFilter 处理中...");
        User user = userService.getUserInfo();
        LOGGER.info("USER 信息：" +  user);
        HttpServletRequest servletRequest = (HttpServletRequest) request;
        LOGGER.info(String.valueOf(servletRequest.getRequestURL()));
        chain.doFilter(request, response);
    }
    @Override
    public void destroy() {
        LOGGER.info("A Filter销毁...");
    }
}
````

示例二：

````log
2022-12-01 12:38:27.535  INFO 21136 --- [           main] w.s.c.ServletWebServerApplicationContext : Root WebApplicationContext: initialization completed in 831 ms
2022-12-01 12:38:27.557 DEBUG 21136 --- [           main] o.s.b.w.s.ServletContextInitializerBeans : Mapping filters: aFilter urls=[/api/amber/*] order=2147483647, characterEncodingFilter urls=[/*] order=-2147483648, formContentFilter urls=[/*] order=-9900, requestContextFilter urls=[/*] order=-105, AFilter urls=[/*] order=2147483647
2022-12-01 12:38:27.557 DEBUG 21136 --- [           main] o.s.b.w.s.ServletContextInitializerBeans : Mapping servlets: dispatcherServlet urls=[/]
2022-12-01 12:38:27.568 DEBUG 21136 --- [           main] o.s.b.w.s.f.OrderedRequestContextFilter  : Filter 'requestContextFilter' configured for use
2022-12-01 12:38:27.568  INFO 21136 --- [           main] com.amber.common.filter.AFilter          : A Filter初始化,只初始化一次...
2022-12-01 12:38:27.568 DEBUG 21136 --- [           main] s.b.w.s.f.OrderedCharacterEncodingFilter : Filter 'characterEncodingFilter' configured for use
2022-12-01 12:38:27.568  INFO 21136 --- [           main] com.amber.common.filter.AFilter          : A Filter初始化,只初始化一次...
2022-12-01 12:38:27.568 DEBUG 21136 --- [           main] o.s.b.w.s.f.OrderedFormContentFilter     : Filter 'formContentFilter' configured for use
2022-12-01 12:38:27.637  INFO 21136 --- [           main] com.zaxxer.hikari.HikariDataSource       : HikariPool-1 - Starting...
2022-12-01 12:38:27.782  INFO 21136 --- [           main] com.zaxxer.hikari.HikariDataSource       : HikariPool-1 - Start completed.
2022-12-01 12:38:28.654  INFO 21136 --- [           main] com.amber.common.BronzeApplication       : Started BronzeApplication in 2.223 seconds (JVM running for 2.775)
2022-12-01 12:38:45.133  INFO 21136 --- [nio-8080-exec-1] o.a.c.c.C.[Tomcat].[localhost].[/]       : Initializing Spring DispatcherServlet 'dispatcherServlet'
2022-12-01 12:38:45.133  INFO 21136 --- [nio-8080-exec-1] o.s.web.servlet.DispatcherServlet        : Initializing Servlet 'dispatcherServlet'
2022-12-01 12:38:45.138  INFO 21136 --- [nio-8080-exec-1] o.s.web.servlet.DispatcherServlet        : Completed initialization in 5 ms
2022-12-01 12:38:45.143  INFO 21136 --- [nio-8080-exec-1] com.amber.common.filter.AFilter          : AFilter 处理中...
2022-12-01 12:38:45.143  INFO 21136 --- [nio-8080-exec-1] com.amber.common.filter.AFilter          : USER 信息：User(screen_name=amber, text=今天星期四, created_at=Thu Dec 01 12:38:45 CST 2022)
2022-12-01 12:38:45.143  INFO 21136 --- [nio-8080-exec-1] com.amber.common.filter.AFilter          : http://localhost:8080/api/amber/weibo
2022-12-01 12:38:45.144  INFO 21136 --- [nio-8080-exec-1] com.amber.common.filter.AFilter          : AFilter 处理中...
2022-12-01 12:38:45.144  INFO 21136 --- [nio-8080-exec-1] com.amber.common.filter.AFilter          : USER 信息：User(screen_name=amber, text=今天星期四, created_at=Thu Dec 01 12:38:45 CST 2022)
2022-12-01 12:38:45.144  INFO 21136 --- [nio-8080-exec-1] com.amber.common.filter.AFilter          : http://localhost:8080/api/amber/weibo
````

可以看到输出日志已经不是期望的结果，发现：
- AFilter init() 初始化 两次
- AFilter doFilter() 处理中 两次

在 ApplicationFilterChain Debug 中发现注册了两个 Filter 分别是：AFilter 和 aFilter，导致走两次。

![](/contents/scoped-filter-settings/jietu.jpg)

### @WebFilter + @Component 同时使用需注意

两个方法全部都一起用是没问题的，会覆盖，切忌的是，
只用 @WebFilter + @Component，不用 @ServletComponentScan 和 FilterRegistrationBean，
这时如果 webFilter 配置的是非全局的过滤器，就会被 @Component 注解再注册一个全局的过滤器了。

其中：
- 当访问的 url 为 `/index/*` 或者 `/product/*` 的时候，该过滤器也执行了！也就是说，WebFilter 注解配置的 urlPatterns 没有起作用。【注意】：@WebFilter 中的 value 属性等价于 urlPatterns 属性，但是两个不应该同时使用。
- `@WebFilter(filterName = "aFilter", value = "/api/amber/*")` 中的 value（或者 urlPatterns）属性，
也可以通过 @Component + FilterRegistrationBean 进行实例注册方式：`filterRegistrationBean.addUrlPatterns("/*");` 解决。

### 小插曲：

当浏览器访问 `http://localhost:8080/index` 发现日志输出了两次， doFilter() 方法执行了两次。

示例一：

````java
@WebFilter(filterName = "aFilter", value = "/*")
public class AFilter implements Filter {
    
    private static final Logger LOGGER = LoggerFactory.getLogger(AFilter.class);
    
    @Autowired
    private UserService userService;
    
    @Override
    public void init(FilterConfig filterConfig) {
        LOGGER.info("A Filter初始化,只初始化一次...");
    }
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) throws IOException, ServletException {
        LOGGER.info("AFilter 处理中...");
        User user = userService.getUserInfo();
        LOGGER.info("USER 信息：" +  user);
    }
    @Override
    public void destroy() {
        LOGGER.info("A Filter销毁...");
    }
}
````

示例二：

````log
2022-11-30 23:55:43.928  INFO 22280 --- [           main] w.s.c.ServletWebServerApplicationContext : Root WebApplicationContext: initialization completed in 795 ms
2022-11-30 23:55:43.952  INFO 22280 --- [           main] com.amber.common.filter.AFilter          : A Filter初始化,只初始化一次...
2022-11-30 23:55:44.022  INFO 22280 --- [           main] com.zaxxer.hikari.HikariDataSource       : HikariPool-1 - Starting...
2022-11-30 23:55:44.170  INFO 22280 --- [           main] com.zaxxer.hikari.HikariDataSource       : HikariPool-1 - Start completed.
2022-11-30 23:56:03.418  INFO 22280 --- [nio-8080-exec-1] o.a.c.c.C.[Tomcat].[localhost].[/]       : Initializing Spring DispatcherServlet 'dispatcherServlet'
2022-11-30 23:56:03.418  INFO 22280 --- [nio-8080-exec-1] o.s.web.servlet.DispatcherServlet        : Initializing Servlet 'dispatcherServlet'
2022-11-30 23:56:03.423  INFO 22280 --- [nio-8080-exec-1] o.s.web.servlet.DispatcherServlet        : Completed initialization in 5 ms
2022-11-30 23:56:03.431  INFO 22280 --- [nio-8080-exec-1] com.amber.common.filter.AFilter          : AFilter 处理中...
2022-11-30 23:56:03.431  INFO 22280 --- [nio-8080-exec-1] com.amber.common.filter.AFilter          : USER 信息：User(screen_name=amber, text=今天星期三, created_at=Wed Nov 30 23:56:03 CST 2022)
2022-11-30 23:56:03.455  INFO 22280 --- [nio-8080-exec-6] com.amber.common.filter.AFilter          : AFilter 处理中...
2022-11-30 23:56:03.456  INFO 22280 --- [nio-8080-exec-6] com.amber.common.filter.AFilter          : USER 信息：User(screen_name=amber, text=今天星期三, created_at=Wed Nov 30 23:56:03 CST 2022)x
````

打开 Network 发现实际的网络请求有两个：
- `/index`—— 实际请求
- `/favicon.ico`——浏览器展示tab上的网站图标。

![](/contents/scoped-filter-settings/network.jpg)

示例三：

````java
@Override
public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) throws IOException, ServletException {
    LOGGER.info("AFilter 处理中...");
    User user = userService.getUserInfo();
    LOGGER.info("USER 信息：" +  user);
    HttpServletRequest servletRequest = (HttpServletRequest) request;
    LOGGER.info(servletRequest.getRequestURI());
    }
````

通过 doFilter() 方法中获取 HttpServletRequest 的 getRequestURI() 方法 中发现有 `/favicon.ico` 请求。

示例四：

````log
2022-12-01 00:11:11.428  INFO 13616 --- [nio-8080-exec-2] o.a.c.c.C.[Tomcat].[localhost].[/]       : Initializing Spring DispatcherServlet 'dispatcherServlet'
2022-12-01 00:11:11.428  INFO 13616 --- [nio-8080-exec-2] o.s.web.servlet.DispatcherServlet        : Initializing Servlet 'dispatcherServlet'
2022-12-01 00:11:11.431  INFO 13616 --- [nio-8080-exec-2] o.s.web.servlet.DispatcherServlet        : Completed initialization in 3 ms
2022-12-01 00:11:11.436  INFO 13616 --- [nio-8080-exec-2] com.amber.common.filter.AFilter          : AFilter 处理中...
2022-12-01 00:11:11.436  INFO 13616 --- [nio-8080-exec-2] com.amber.common.filter.AFilter          : USER 信息：User(screen_name=amber, text=今天星期三, created_at=Thu Dec 01 00:11:11 CST 2022)
2022-12-01 00:11:11.436  INFO 13616 --- [nio-8080-exec-2] com.amber.common.filter.AFilter          : /index
2022-12-01 00:11:11.449  INFO 13616 --- [nio-8080-exec-6] com.amber.common.filter.AFilter          : AFilter 处理中...
2022-12-01 00:11:11.449  INFO 13616 --- [nio-8080-exec-6] com.amber.common.filter.AFilter          : USER 信息：User(screen_name=amber, text=今天星期三, created_at=Thu Dec 01 00:11:11 CST 2022)
2022-12-01 00:11:11.450  INFO 13616 --- [nio-8080-exec-6] com.amber.common.filter.AFilter          : /favicon.ico
````

**小插曲是因为浏览器会自动发一个获取网站图标的请求，而过滤器配置的是全局过滤器，所以就会走两次。**