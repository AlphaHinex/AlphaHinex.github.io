---
id: servlet-filter
title: "Servlet 之 Filter"
description: "Filter 不仅能前置处理 Request，也能后置处理 Response，不过后置处理时，要注意 Response 一旦被提交了，就不能再被修改了"
date: 2021.10.17 10:34
categories:
    - Java
tags: [Servlet]
keywords: Servlet, filter, response is commited
cover: https://wyiyi.github.io/amber/contents/flow/filterChain.png
---

原文地址：https://wyiyi.github.io/amber/2021/10/01/filter/

Servlet 作为Java Web 的基础，在 Servlet API 中提供了一个 Filter 接口，Filter，又称过滤器。 
所谓过滤器顾名思义是用来过滤的，可以从客户端向服务端发送请求进行过滤，也可以对服务器返回响应进行处理。
 
![](https://wyiyi.github.io/amber/contents/flow/filter.png)
 
根据上面的流程可以看出，Filter的作用就是在用户请求到达Servlet之前，进行拦截。在拦截到用户的请求后，我们可以实现一些自定义的业务逻辑。
例如：实现URL级别的权限访问控制（最常用）、字符编码、登录限制、过滤敏感词汇、文件压缩，跨域设置等一些高级功能。
 
### 生命周期
 Filter 与 Servlet 一样都是由服务器负责创建和销毁的，Filter 只会被创建和销毁一次，doFilter 可以执行多次。
 - 在 Web 应用程序启动时，服务器会根据程序的 web.xml 文件中的配置信息调用 init() 方法初始化 Filter。
 - 初始化后，过滤器会对请求进行拦截并调用 doFilter() 方法。
 - 在应用程序关闭时，调用 destroy() 方法销毁 Filter。
 
 ### 应用
 将 Java 类实现 `javax.servlet.Filter` 接口，重写 doFilter() 方法（init()，destroy() 也可重写）
 ```java
public class AFilter implements Filter {
    @Override
    public void init(FilterConfig filterConfig) {}

    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) {}

    @Override
    public void destroy() {}
}
 ```
 #### 一、注册 Filter 方式
 1、通过传统的 web.xml 方式注册。
 ```xml
    <filter>
       <filter-name>AFilter</filter-name>
           <filter-class>com.amber.demo.filter.AFilter</filter-class>
    </filter>
    <filter-mapping>
       <filter-name>AFilter</filter-name>
       <url-pattern>/*</url-pattern>
    </filter-mapping>
 ```
 2、注解方式： @WebFilter，该方式是 web3.0 提供的注解，代替在 web.xml 文件中配置 filter，简化了开发。
```java
@WebFilter(urlPatterns = "/*")
public class AFilter implements Filter {
   // 同上...
}
```
 
 #### 三、FilterChain 的 chain.doFilter
 ![](https://wyiyi.github.io/amber/contents/flow/filterChain.png)
 
1、在 chain.doFilter 中使用 `@WebFilter` 注解，会按照类名的字典顺序执行

 ```java
@Component
@WebFilter(filterName = "aFilter", value = "/*")
public class AFilter implements Filter {
    private static final Logger LOGGER = LoggerFactory.getLogger(AFilter.class);
    
    @Override
    public void init(FilterConfig filterConfig) {
        LOGGER.info("Filter初始化,只初始化一次...");
    }

    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) throws IOException, ServletException {
        LOGGER.info("拦截前执行...");
        chain.doFilter(request,response);
        LOGGER.info("拦截后执行...");
    }

    @Override
    public void destroy() {
        LOGGER.info("Filter销毁...");
    }
   // BFilter、CFilter 同上
}
 ```

以 `AFilter`、`BFilter`、`CFilter` 为例，执行的过滤器的顺序输出为：
 ```text
2021-09-17 14:53:41.116  INFO 2024 --- [nio-8040-exec-1] com.amber.demo.filter.AFilter: A 拦截前执行...
2021-09-17 14:53:41.117  INFO 2024 --- [nio-8040-exec-1] com.amber.demo.filter.BFilter: B 拦截前执行...
2021-09-17 14:53:41.117  INFO 2024 --- [nio-8040-exec-1] com.amber.demo.filter.CFilter: C 拦截前执行...
2021-09-17 14:53:42.230  INFO 2024 --- [nio-8040-exec-1] com.amber.demo.filter.CFilter: C 拦截后执行...
2021-09-17 14:53:42.230  INFO 2024 --- [nio-8040-exec-1] com.amber.demo.filter.BFilter: B 拦截后执行...
2021-09-17 14:53:42.230  INFO 2024 --- [nio-8040-exec-1] com.amber.demo.filter.AFilter: A 拦截后执行...
 ```

2、调整 FilterChain 的执行顺序

由于注解`@WebFilter`的源码（如下）中没有参数指定顺序，但是在Spring中提供了 `@Order` 注解可以指定Filter的执行顺序。

 ```java
@Target({ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface WebFilter {
    String description() default "";

    String displayName() default "";

    WebInitParam[] initParams() default {};

    String filterName() default "";

    String smallIcon() default "";

    String largeIcon() default "";

    String[] servletNames() default {};

    String[] value() default {};

    String[] urlPatterns() default {};

    DispatcherType[] dispatcherTypes() default {DispatcherType.REQUEST};

    boolean asyncSupported() default false;
}
 ```
-  @Order 注解： Order 值越小执行优先级越高。(注意：filterName 的值首字母小写，否则顺序会不生效)
 ```java
@Order(-1)
@WebFilter(filterName = "aFilter", value = "/*")
@Component
public class AFilter implements Filter {
   // 方法同上
}
 ```

- 新增配置文件，通过 `FilterRegistrationBean` 实例注册并定义`Order`的属性（注意：过滤器的`Bean`类的注解只保留`@Component`）
 ```java
@Configuration
public class ComponentFilterOrderConfig {

    @Bean
    public FilterRegistrationBean filterBeanOne() {
        FilterRegistrationBean filterRegistrationBean = new FilterRegistrationBean();
        filterRegistrationBean.setFilter(new AFilter());
        filterRegistrationBean.addUrlPatterns("/*");
        filterRegistrationBean.setOrder(3);
        return filterRegistrationBean;
    }

    @Bean
    public FilterRegistrationBean filterBeanTwo() {
        FilterRegistrationBean filterRegistrationBean = new FilterRegistrationBean();
        filterRegistrationBean.setFilter(new BFilter());
        filterRegistrationBean.addUrlPatterns("/*");
        filterRegistrationBean.setOrder(2);
        return filterRegistrationBean;
    }

    @Bean
    public FilterRegistrationBean filterBeanThree() {
        FilterRegistrationBean filterRegistrationBean = new FilterRegistrationBean();
        filterRegistrationBean.setFilter(new CFilter());
        filterRegistrationBean.addUrlPatterns("/*");
        filterRegistrationBean.setOrder(1);
        return filterRegistrationBean;
    }
}
 ```
 ```java
@Component
public class AFilter implements Filter {
   ... AFilter、BFilter、CFilter 同上...
}
 ```

执行的过滤器的顺序输出为：
 ```text
2021-09-22 09:58:50.537  INFO 2816 --- [nio-8040-exec-1] com.amber.demo.filter.CFilter  : C 拦截后执行...
2021-09-22 09:58:50.537  INFO 2816 --- [nio-8040-exec-1] com.amber.demo.filter.BFilter  : B 拦截后执行...
2021-09-22 09:58:50.537  INFO 2816 --- [nio-8040-exec-1] com.amber.demo.filter.AFilter  : A 拦截后执行...
2021-09-22 09:58:50.537  INFO 2816 --- [nio-8040-exec-1] com.amber.demo.filter.AFilter  : A 拦截后执行...
2021-09-22 09:58:50.537  INFO 2816 --- [nio-8040-exec-1] com.amber.demo.filter.BFilter  : B 拦截后执行...
2021-09-22 09:58:50.537  INFO 2816 --- [nio-8040-exec-1] com.amber.demo.filter.CFilter  : C 拦截后执行...
 ```
  
3、设置请求或响应(Request、Response)
- 在请求前对 Request 进行设置Header、Body的值等；
- 在请求结束后对 Response 响应进行处理：如一个完整请求所用时间、日志等。
  
【注意】：[Filter chain.doFilter 之后 response is committed，不能再设置请求头](https://stackoverflow.com/questions/2030152/cannot-set-header-in-jsp-response-already-committed)
，原因是当响应被提交时，这意味着标头已经发送到客户端，无法设置或者更改标头。