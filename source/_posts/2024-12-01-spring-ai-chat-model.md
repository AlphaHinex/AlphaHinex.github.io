---
id: spring-ai-chat-model
title: "用 Spring AI 调用 OpenAI 对话接口"
description: "本文以调用智谱 AI 开放平台的 OpenAI 兼容对话接口为例，演示了使用 Spring AI 对接单个或多个对话模型的方法。"
date: 2024.12.01 10:34
categories:
    - AI
    - Spring
tags: [AI, Spring, Spring AI]
keywords: Spring AI, OpenAI, Chat Completions, ChatClient
cover: /contents/spring-ai-chat-model/cover.png
---

# 环境准备

## JDK

使用 [Spring AI](https://github.com/spring-projects/spring-ai) 需要 [JDK 17](https://github.com/spring-projects/spring-ai/blob/main/pom.xml#L171-L172) 及以上版本。

```bash
$ java -version
openjdk version "17.0.2" 2022-01-18
OpenJDK Runtime Environment (build 17.0.2+8-86)
OpenJDK 64-Bit Server VM (build 17.0.2+8-86, mixed mode, sharing)
```

## start.spring.io

从 https://start.spring.io/ 下载一个包含 Spring Web 依赖的 Maven 工程：

![start](/contents/spring-ai-chat-model/start.png)

解压，并使用其中自带的 Maven Wrapper 进行构建：

```bash
$ unzip demo.zip
$ cd demo
$ ./mvnw clean package
...
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  5.569 s
[INFO] Finished at: 2024-11-30T13:58:27+08:00
[INFO] ------------------------------------------------------------------------
```

## 智谱 AI 开放平台

登录到智谱AI开放平台 [API Keys 页面](https://bigmodel.cn/usercenter/apikeys) 获取最新版生成的用户 API Key，用于调用其提供的兼容 OpenAI 对话接口的免费模型 `GLM-4-Flash`：

```bash
$ curl --location 'https://open.bigmodel.cn/api/paas/v4/chat/completions' \
--header 'Authorization: Bearer <你的apikey>' \
--header 'Content-Type: application/json' \
--data '{
    "model": "glm-4-flash",
    "messages": [
        {
            "role": "user",
            "content": "你好"
        }
    ]
}'
{"choices":[{"finish_reason":"stop","index":0,"message":{"content":"你好👋！很高兴见到你，有什么可以帮助你的吗？","role":"assistant"}}],"created":1732946586,"id":"202411301403051925a900b08f4e23","model":"glm-4-flash","request_id":"202411301403051925a900b08f4e23","usage":{"completion_tokens":16,"prompt_tokens":6,"total_tokens":22}}
```

# 添加依赖

在 `pom.xml` 中添加 Spring AI 的 [相关配置及依赖](https://docs.spring.io/spring-ai/reference/getting-started.html)：

`repositories`：

```xml
<repositories>
  <repository>
    <id>spring-milestones</id>
    <name>Spring Milestones</name>
    <url>https://repo.spring.io/milestone</url>
    <snapshots>
      <enabled>false</enabled>
    </snapshots>
  </repository>
  <repository>
    <id>spring-snapshots</id>
    <name>Spring Snapshots</name>
    <url>https://repo.spring.io/snapshot</url>
    <releases>
      <enabled>false</enabled>
    </releases>
  </repository>
</repositories>
```

`dependencyManagement`：

```xml
<dependencyManagement>
  <dependencies>
    <dependency>
      <groupId>org.springframework.ai</groupId>
      <artifactId>spring-ai-bom</artifactId>
      <version>1.0.0-SNAPSHOT</version>
      <type>pom</type>
      <scope>import</scope>
    </dependency>
  </dependencies>
</dependencyManagement>
```

`dependency`：

```xml
<dependency>
  <groupId>org.springframework.ai</groupId>
  <artifactId>spring-ai-openai-spring-boot-starter</artifactId>
</dependency>
```

# 使用 ChatClient 与 OpenAI 兼容模型接口对话

## 仅对接一个大模型时

可直接通过配置项注册并使用 ChatClient。

在 `application.properties` 中添加 Spring AI OpenAI 的相关配置：

```properties
spring.ai.openai.base-url=https://open.bigmodel.cn/api/paas
spring.ai.openai.chat.completions-path=/v4/chat/completions
spring.ai.openai.api-key=<你的apikey>
spring.ai.openai.chat.options.model=glm-4-flash
```

创建一个配置类：

```java
@Configuration
public class Config {

    @Bean
    ChatClient chatClient(ChatClient.Builder builder) {
        return builder.build();
    }

}
```

在工程中自带的 `DemoApplicationTests` 单元测试中，验证对话效果：

```java
@Autowired
ChatClient chatClient;

@Test
void autoConfig() {
    String userMsg = "who r u";
    System.out.println(chatClient.prompt().user(userMsg).call().content());
}
```

执行结果如下：

```text
I am an AI assistant named ChatGLM, which is developed based on the language model jointly trained by Tsinghua University KEG Lab and Zhipu AI Company in 2024. My job is to provide appropriate answers and support to users' questions and requests.
```

## 需要对接多个大模型时

可定义一个工场类创建多个 ChatClient 实例：

```java
public class ChatClientFactory {

    public static ChatClient createOpenAiChatClient(String baseUrl, String apiKey, String model, String completionsPath) {
        if (StringUtils.isBlank(completionsPath)) {
            completionsPath = "/v1/chat/completions";
        }
        OpenAiApi openAiApi = new OpenAiApi(baseUrl, apiKey, completionsPath,
            "/v1/embeddings", RestClient.builder(), WebClient.builder(), RetryUtils.DEFAULT_RESPONSE_ERROR_HANDLER);
        OpenAiChatModel openAiChatModel = new OpenAiChatModel(openAiApi, OpenAiChatOptions.builder().withModel(model).build());
        return ChatClient.create(openAiChatModel);
    }

}
```

```java
@Test
void multiClients() {
    ChatClient llm1 = ChatClientFactory.createOpenAiChatClient("https://open.bigmodel.cn/api/paas", "xxxx", "glm-4-flash", "/v4/chat/completions");
    ChatClient llm2 = ChatClientFactory.createOpenAiChatClient("https://open.bigmodel.cn/api/paas", "xxxx", "glm-4-flash", "/v4/chat/completions");

    String userMsg = "你是谁？";
    System.out.println(llm1.prompt().user(userMsg).call().content());
    System.out.println(llm2.prompt().user(userMsg).call().content());
}
```

# 示例代码

[demo.zip](/contents/spring-ai-chat-model/demo.zip)
