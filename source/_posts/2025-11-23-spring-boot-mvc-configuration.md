---
id: spring-boot-mvc-configuration
title: "【转】自定义SpringBoot默认MVC配置？好几个坑，这篇文章必须珍藏"
description: "恰当的使用 WebMvcConfigurationSupport、WebMvcConfigurer 及 @EnableWebMvc"
date: 2025.11.23 10:26
categories:
    - Spring
tags: [Spring, Spring Boot, MVC]
keywords: Spring, Spring Boot, MVC, WebMvcConfigurer, WebMvcConfigurationSupport, EnableWebMvc, DelegatingWebMvcConfiguration, WebMvcAutoConfiguration
cover: /contents/covers/spring-boot-mvc-configuration.png
---

- 作者：程序新视界
- 链接：https://juejin.cn/post/6917874946005958664
- 来源：稀土掘金
- 著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。

# 前言

前些天，在项目实践过程中出现了一个奇怪的状况，Spring Boot 的参数绑定失效了。而起因只是因为同事把参数上的 @RequestParam 注解去掉了。我们都知道，如果参数名称和 Controller 的方法名相同时，根本不需要 @RequestParam 注解的，Spring Boot 会自动帮我们完成参数的绑定。但为什么自动绑定机制失效了呢？本篇文章会为大家揭开谜底，在此过程中也会全面讲解如何在 Spring Boot 项目中自定义配置 WebMvc，以及这其中的很多坑。

# SpringBoot 自定义 WebMvc

Spring Boot 为 Spring MVC 提供了默认的配置主要包括视图解析器、静态资源处理、类型转化器与格式化器、HTTP 消息转换器、静态主页支持等，可谓简单易用。但实践中，难免需要进行个性化的配置，因此自定义 Web MVC 配置在所难免。Spring Boot 先后提供了 WebMvcConfigurerAdapter、WebMvcConfigurationSupport、WebMvcConfigurer、@EnableWebMvc 等形式来实现 Web MVC 的自定义配置。下面我们来逐一学习。

## 被废弃的 WebMvcConfigurerAdapter

在 Spring Boot1.0 + 中，可以使用 WebMvcConfigurerAdapter 来扩展 Spring MVC 的功能。WebMvcConfigurerAdapter 是 WebMvcConfigurer 的一个抽象实现类，该抽象类中所有的方法实现都为空，子类需要哪些功能就实现哪些功能。

到了 Spring 5.0 之后，也就是在 Spring Boot2.0 版本中，JDK 基于 Java8 来实现了，而在 Java8 中可以将接口的方法定义为 default。接口中被定义为 default 的方法子类可以不进行实现。而接口 WebMvcConfigurer 便运用了 Java8 的特性，因此 WebMvcConfigurerAdapter 存在的意义没有了。

于是，在 Spring Boot2.0 版本中，WebMvcConfigurerAdapter 这个类被弃用了。

```java
@Deprecated
public abstract class WebMvcConfigurerAdapter implements WebMvcConfigurer {
```

查看 WebMvcConfigurerAdapter 的实现，你会发现它就是把接口的所有方法实现为一个空的方法而已，Java8 的 default 特性完全覆盖掉此功能。如果你是基于 Spring Boot 2.x 进行开发，通过 extends（继承）WebMvcConfigurerAdapter 来实现功能，那么可以直接替换为 implements（实现）WebMvcConfigurer 的形式了。关于具体实现，我们后面会讲到。

# 会覆盖的 WebMvcConfigurationSupport

WebMvcConfigurerAdapter 被废弃了，那么我们还可以通过继承 WebMvcConfigurationSupport 来实现 Spring MVC 的拓展。

```java
public class WebMvcConfigurationSupport implements ApplicationContextAware, ServletContextAware {...}
```

这个类很特殊，实现了 ApplicationContextAware 和 ServletContextAware 接口， 提供了一些默认实现，同时提供了很多 @Bean 方法，但是并没有提供 @Configureation 注解，因此这些 @Bean 并不会生效，所以我们需要继承这个类，并在提供的类上提供 @Configureation 注解才能生效。

WebMvcConfigurationSupport 中不仅定义了 Bean，还提供了大量 add、config 开头的方法。对照 WebMvcConfigurer 的方法定义，会发现几乎 WebMvcConfigurer 有的在 WebMvcConfigurationSupport 中都有。需要注意的是，某些方法在 WebMvcConfigurationSupport 中也并未实现具体功能。

比如常见的 addInterceptors 和 addViewControllers：

```java
/**
* Override this method to add Spring MVC interceptors for
* pre- and post-processing of controller invocation.
* @see InterceptorRegistry
 */
protected void addInterceptors(InterceptorRegistry registry) {
}

/**
 * Override this method to add view controllers.
 * @see ViewControllerRegistry
*/
protected void addViewControllers(ViewControllerRegistry registry) {
}
```

继承 WebMvcConfigurationSupport 之后，可以使用方法来添加自定义的拦截器、视图解析器等功能，示例如下：

```java
@Configuration
public class WebMvcConfig extends WebMvcConfigurationSupport {
    @Override
    protected void addViewControllers(ViewControllerRegistry registry) {
        registry.addViewController("/").setViewName("login");
        registry.addViewController("/login.html").setViewName("login");
    }
}
```

此时，你以为万事大吉，可以开心的写业务逻辑了？其实此时问题刚刚开始。当通过继承 WebMvcConfigurationSupport 的形式来实现 MVC 配置时，会对 Spring Boot 默认的 MVC 配置进行顶替。一旦进行顶替，Spring Boot 默认提供的那些约定优于配置的功能可能就会失效，比如静态资源访问不到、返回数据不成功，当然还有开篇提到的参数绑定失效的问题。

那么，为什么继承 WebMvcConfigurationSupport 会顶替到 Spring Boot 默认的 MVC 配置呢？先来看一下 Spring Boot 中对 WEB MVC 相关组件自动装配的实现：

```java
@Configuration(proxyBeanMethods = false)
@ConditionalOnWebApplication(type = Type.SERVLET)
@ConditionalOnClass({Servlet.class, DispatcherServlet.class, WebMvcConfigurer.class})
@ConditionalOnMissingBean({WebMvcConfigurationSupport.class})
@AutoConfigureOrder(-2147483638)
@AutoConfigureAfter({DispatcherServletAutoConfiguration.class, TaskExecutionAutoConfiguration.class, ValidationAutoConfiguration.class})
public class WebMvcAutoConfiguration {...}
```

Spring Boot 通过 WebMvcAutoConfiguration 配置类来对 MVC 的默认参数（约定）进行设置，但 WebMvcAutoConfiguration 生效是有限制条件的。@ConditionalOnMissingBean({WebMvcConfigurationSupport.class}) 指定了，当 Spring 容器中不存在类型为 WebMvcConfigurationSupport 的 bean 的时候，才会进行默认配置。一定自定义了 WebMvcConfigurationSupport，那么将导致 WebMvcAutoConfiguration 无法实例化，进而内部初始化配置将全部无法实例化。

这种情况下，相关的配置都需要自己去实现了，除非对代码有极好的把控能力，或者大量特殊化定制，才会考虑此种形式。否则，一些列的约定便不复存在，可能会出现一些莫名其妙的问题。

# 终极杀手锏 WebMvcConfigurer

讲了上述两种不可行或有坑的方式之后，按照剧情的发展，当然该出现最终的解决方案了，那就是实现 WebMvcConfigurer 接口。

但在学习了 WebMvcConfigurationSupport 的方式之后，你是否心有余悸，会不会也出现覆盖的情况？很显然，WebMVC 自动配置类中并没有 WebMvcConfigurer 的 Bean 是否存在的限制条件。因此，并不会因为实现了该接口而导致默认配置失效。不仅如此，Spring Boot 还支持存在多个 WebMvcConfigurer 的实现类。

上面已经提到，Spring Boot2.x 是基于 Java8 的，Java8 有个重大的改变就是接口中可以有 default 方法，而 default 方法是不需要强制实现的。上述的 WebMvcConfigurerAdapter 类就是实现了 WebMvcConfigurer，所以我们不需要继承 WebMvcConfigurerAdapter 类，可以直接实现 WebMvcConfigurer 接口，用法与继承适配类是一样的。如：

```java
@Configuration
public class MyMVCConfig implements WebMvcConfigurer {

    @Override
    public void addViewControllers(ViewControllerRegistry registry) {
        registry.addViewController("/user").setViewName("success");
    }
}
```

如果还不确定，你可以实践一下，会发现实现 WebMvcConfigurer 接口的方式，Spring Boot 的自动配置并不会失效。通常，也是建议大家通过这种形式来实现 Web MVC 的自定义的。

下面在深入分析一下为什么通过实现 WebMvcConfigurer 接口的方式能保持保持自定义和默认配置同时生效。回到前面的自动配置类 WebMvcAutoConfiguration，在该类内部会初始化一个内部类 EnableWebMvcConfiguration：

```java
@Configuration
public static class EnableWebMvcConfiguration extends DelegatingWebMvcConfiguration {...}
```

该内部类继承了 DelegatingWebMvcConfiguration 类，DelegatingWebMvcConfiguration 是对 Spring MVC 进行配置的一个代理类，它结合缺省配置和用户配置来定义 Spring MVC 运行时最终使用的配置。DelegatingWebMvcConfiguration 继承自 WebMvcConfigurationSupport，而 WebMvcConfigurationSupport 为 Spring MVC 提供缺省配置。

```java
@Configuration
public class DelegatingWebMvcConfiguration extends WebMvcConfigurationSupport {
   @Autowired(required = false)
   public void setConfigurers(List<WebMvcConfigurer> configurers) {
      if (!CollectionUtils.isEmpty(configurers)) {
         this.configurers.addWebMvcConfigurers(configurers);
      }
   }
   //...
}
```

DelegatingWebMvcConfiguration 本身使用了注解 @Configuration，所以它是一个配置类，会被作为一个单例 bean 注册到容器和被容器注入相应的依赖。WebMvcConfigurer 注入到 DelegatingWebMvcConfiguration 是通过 setConfigurers(List configurers) 方法来实现的。该方法使用了注解 @Autowired(required = false)，会收集所有的 WebMvcConfigurer 实现类中的配置组合起来，组成一个超级配置。因此，只要我们实现了 WebMvcConfigurer 接口的类都会通过 setConfigurers 方法被注入，多个 WebMvcConfigurer 实例会以 List 形式存储。

所以，直接实现 WebMvcConfigurer 接口的形式不会覆盖掉原有的默认配置，还可以新增客户自定义的配置。那么，使用实现 WebMvcConfigurer 接口的形式就 OK 了吗？如果你在网上找一些示例代码，还会有一些坑等着你，请继续往下看。

# @EnableWebMvc 使用场景

在很多代码示例中，你还会看到它不仅实现了 WebMvcConfigurer 接口，还在实现类上使用了 @EnableWebMvc 注解，此时你需要注意了。@EnableWebMvc 注解会引起新一轮的默认 WebMVC 配置失效。

早期官方版本中有类似如下说明：如果想保持 Spring Boot 默认提供的 WebMVC 特性，然后新增额外的功能，只需要继承 WebMvcConfigurerAdapter 或实现 WebMvcConfigurer 接口，然后在实现类上通过 @Configuration 注解进行实例化即可，不需要使用 @EnableWebMvc。如果你想完全控制 Spring MVC，你可以在实现类上再添加上 @EnableWebMvc 注解。

也就是说 @EnableWebMvc 注解并不是必须配置，只有在要完全覆盖默认配置的情况下才会使用。而且该注解的源码注释中也明确指明，整个项目中只能有一个类使用 @EnableWebMvc 注解，而不像 WebMvcConfigurer 接口的实现类可以有多个。

所以，一旦代码中使用了 @EnableWebMvc 注解，就意味着 Spring MVC 的自动配置会失效，所有的东西都需要我们自动配置。使用示例如下：

```java
@Configuration
@EnableWebMvc
public class WebDispatcherServletConfigure implements WebMvcConfigurer {
    @Bean
    public ViewResolver viewResolver() {
        InternalResourceViewResolver resourceViewResolver = new InternalResourceViewResolver();
        resourceViewResolver.setViewClass(JstlView.class);
        resourceViewResolver.setPrefix("/WEB-INF/jsp/");
        resourceViewResolver.setSuffix(".jsp");
        return resourceViewResolver;
    }
}
```

那么，为什么使用 @EnableWebMvc 注解会导致默认生效呢？我们来看一下它的源码：

```java
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
@Documented
@Import(DelegatingWebMvcConfiguration.class)
public @interface EnableWebMvc {
}
```

在注解 EnableWebMvc 上通过 @Import 导入了 DelegatingWebMvcConfiguration 类。这个类是不是似曾相识？对的，就是上面我们讲到的继承了 WebMvcConfigurationSupport 的类。也就是说，一旦使用 @EnableWebMvc 注解，便会导入一个 WebMvcConfigurationSupport，进而产生了一个 Bean。此时，又回到前面的结论，WebMvcAutoConfiguration 发现已经存在这么一个 Bean，变不会进行实例化操作了。

汇总一下就是 WebMvcConfigurationSupport 有三种实现形式：第一，用户自定义 WebMvcConfigurationSupport 的实现类，此时会导致 WebMvcAutoConfiguration 不会实例化；第二，使用 @EnableWebMvc 注解，等于扩展了 WebMvcConfigurationSupport，但没有重写任何方法，此时同样会导致 WebMvcAutoConfiguration 不会实例化；第三，采用默认配置，WebMvcAutoConfiguration 来实例化对应的 WebMvcConfigurationSupport 的实现类。

因此，通常我们采用实现 WebMvcConfigurer 接口，然后让 Spring Boot 采用默认的配置。

# WebMvc 常见配置

上面了解了各类配置形式的区别以及其中的坑，选择好适合的 WebMVC 配置形式之后，再来看看通常可以有哪些配置，主要围绕接口的实现类。

## 静态资源配置

重写 addResourceHandlers 来配置路径访问等，Spring Boot 中默认使用 ResourceHttpRequestHandler 来映射类路径下的 / static、/public、/resources 和 / METAINF/resources 目录或者 ServletContext 的根目录中的静态文件直接映射为 /****。

```java
@Override
public void addResourceHandlers(ResourceHandlerRegistry registry) {	
    //静态资源路径 css,js,img等
    registry.addResourceHandler("/statics/**").addResourceLocations("classpath:/statics/");
    //视图
    registry.addResourceHandler("/templates/**").addResourceLocations("classpath:/templates/");
    //mapper.xml
    registry.addResourceHandler("/mapper/**").addResourceLocations("classpath:/mapper/");
    super.addResourceHandlers(registry);		
}
```

## 拦截器配置

重写 addInterceptors() 方法来配置拦截器（实现了 HandlerInterceptor 接口）等。这里实现的 addInterceptors 方法对应的是 xml 文件中 < mvc:interceptors> 配置。

```java
@Autowired
private MyInteceptor myInteceptor;

@Override
public void addInterceptors(InterceptorRegistry registry) {	
    //注册自定义拦截器，添加拦截路径和排除拦截路径
    registry.addInterceptor(myInteceptor) //添加拦截器
               .addPathPatterns("/**") //添加拦截路径
               .excludePathPatterns(//排除拦截路径
                       "/statics/**/*.*",
                       );
    super.addInterceptors(registry);		
}
```

## 跨域配置

重写 addCorsMappings 方法实现配置 cors 跨域限制等。

```java
@Override
public void addCorsMappings(CorsRegistry registry) {		
    registry.addMapping("/**")//配置允许跨域的路径
        .allowedOrigins("*")//配置允许访问的跨域资源的请求域名
        .allowedMethods("PUT,POST,GET,DELETE,OPTIONS")//配置允许访问该跨域资源服务器的请求方法，如：POST、GET、PUT、DELETE等
        .allowedHeaders("*"); //配置允许请求header的访问，如 ：X-TOKEN
    super.addCorsMappings(registry);
}
```

## 视图控制器配置

重写 addViewControllers 方法配置 view 视图映射等。

```java
@Override
public void addViewControllers(ViewControllerRegistry registry) {	
    registry.addViewController("/").setViewName("/home");//默认视图跳转
    registry.setOrder(Ordered.HIGHEST_PRECEDENCE);
    super.addViewControllers(registry);		
}
```

## 消息转换器配置

重写 configureMessageConverters 方法来对消息进行转换。MessageConverter 用于对 http 请求的返回结果进行转换，以 fastjon、编码格式 application/json;charset=UTF-8 进行转换。

```java
@Override
public void configureMessageConverters(List<HttpMessageConverter<?>> converters) {
    StringHttpMessageConverter converter  = new StringHttpMessageConverter(Charset.forName("UTF-8"));
    converters.add(converter);  
}
```

## 数据格式化器配置

重写 addFormatters 方法来添加数据格式化器，比如将字符串转换为日期类型，可通过 DateFormatter 类来实现自动转换。

formatters 和 converters 用于对日期格式进行转换，默认已注册了 Number 和 Date 类型的 formatters，支持 @NumberFormat 和 @DateTimeFormat 注解，需要自定义 formatters 和 converters 可以实现 addFormatters 方法。

```java
@Override
public void addFormatters(FormatterRegistry registry) {
    super.addFormatters(registry);
    registry.addFormatter(new DateFormatter("yyyy-MM-dd"));
}
```

## 视图解析器配置

重写 configureViewResolvers() 方法来配置视图解析器，主要是配置视图的前后缀。

```java
@Override
public void configureViewResolvers(ViewResolverRegistry registry) {
    InternalResourceViewResolver viewResolver = new InternalResourceViewResolver();
    viewResolver.setPrefix("");
    viewResolver.setSuffix(".html");
    viewResolver.setCache(false);
    viewResolver.setContentType("text/html;charset=UTF-8");
    viewResolver.setOrder(0);		
    registry.viewResolver(viewResolver);
   super.configureViewResolvers(registry);
}
```

也提供了采用简化版本，比如：

```java
@Override
public void configureViewResolvers(ViewResolverRegistry registry) {
    registry.jsp("/", ".jsp");
}
```

# 小结

通过本篇文章的学习，想必大家对 Spring Boot 默认的配置，如何自定义配置，以及具体方法的实现都有了一个详细的了解。最关键的是通过不同的表现形式，不断追踪到底层实现，最终达到从底层原理到上层应用融会贯通的效果。所以，在实践的过程中我们不要忽略掉任何一个小的异常或 bug，深入追加一下就打开一片新的天地。
