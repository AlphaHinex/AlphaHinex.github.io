---
id: java-thread-id
title: "【转】CPU飙升排查"
description: "根据进程 ID 及线程 ID 定位具体问题代码示例"
date: 2023.06.24 10:26
categories:
    - Java
tags: [Java, Linux]
keywords: ps, jstack, printf, top
cover: /contents/java-thread-id/bVc7Fau.png
---

原文地址：https://softleadergy.github.io/CPU%E9%A3%99%E5%8D%87%E6%8E%92%E6%9F%A5/

# CPU飙升

线上资源cpu飙升是我们工作中常见的问题，一篇文章搞定排查方法

## 一、问题复现

现在我有两个接口，代码如下

```java
@RestController
public class CPUCheck {
  @RequestMapping("/hello")
  public String helloWorld(){
      return "hello World";
  }

  @RequestMapping("/run")
  public void run(){
      while (true){

      }
  }
}
```

代码很简单 接口1“/hello” 返回“hello World”，接口2“/run” 进入死循环，这样就保证了访问接口2cpu升高。

## 二、测试

1. 我们将项目打包部署在服务器上，并启动
    ![jar](/contents/java-thread-id/view.png)
2. 测试接口
    ```bash
    curl http://localhost:9901/thing-test/hello
    ```
    ![pid](/contents/java-thread-id/bVc7E9o-20230617142818168.png)

## 三、排查

1. 通过`top`命令可以查看到有一个java进程占用cpu资源异常
2. 获取pid为`32306`
3. 通过命令查询`tid`
    ```shell
    命令：ps -mp 【pid】 -o THREAD,tid,time
    实例：ps -mp 32306 -o THREAD,tid,time
    ```
    ![tid](/contents/java-thread-id/bVc7Fau.png)
4. 可以看到引起cpu异常的tid是`32327`
5. 因为现在的tid`32327`是十进制的，需要将其转化为十六进制
    ```shell
    命令：printf "%x\n" 【十进制tid】
    实例：printf "%x\n" 32327
    ```
    ![nid](/contents/java-thread-id/bVc7FaD.png)
6. 根据pid 和 tid查询导致cpu飙升的代码
    ```shell
    命令：jstack 【10进制pid】 | grep 【16进制tid】 -A 20
    实例：jstack 32306 | grep 7e47 -A 20
    ```
    ![jstack](/contents/java-thread-id/bVc7Fby-20230617143253173.png)

![src](/contents/java-thread-id/bVc7FbL.png)

---

end....