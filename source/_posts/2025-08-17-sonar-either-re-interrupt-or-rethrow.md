---
id: sonar-either-re-interrupt-or-rethrow
title: "【转】sonar对于处理InterruptedException异常提示的原因分析"
description: "Either re-interrupt this method or rethrow the \"InterruptedException\" that can be caught here."
date: 2025.08.17 10:34
categories:
    - Java
tags: [Java, Sonar]
keywords: InterruptedException, Sonar, sleep, Thread, wait, join, re-interrupt, rethrow
cover: /contents/sonar-either-re-interrupt-or-rethrow/cover.png
---

- 原文地址：https://blog.csdn.net/CSDN_WYL2016/article/details/106837995
- 原文作者：[码拉松](https://blog.csdn.net/CSDN_WYL2016?type=blog)

当我们使用会抛出InterruptedException异常的方法时，如果处理不当可能会发生一些预期之外的问题。

下面看一段代码演示：

```java
public class ThreadInterruptedDemo {

    public static void main(String[] args) throws InterruptedException {
        Thread myThread = new MyThread();
        myThread.setName("my thread");
        myThread.start();
        Thread.sleep(10);
        System.out.println("call myThread interrupt method...");
        myThread.interrupt();
    }
}

class MyThread extends Thread {
    @Override
    public void run() {
        String threadName = Thread.currentThread().getName();
        //打印当前线程是否被中断
        System.out.println(threadName + " interrrupted is: " + isInterrupted());
        while (!isInterrupted()) {
            System.out.println(threadName + " is running");
            //打印当前线程是否被中断
            System.out.println(threadName + " circle println interrrupted is: "
                    + isInterrupted());
        }
        System.out.println(threadName + " exit circle interrrupted is: " + isInterrupted());
    }
}
```

![no loop](https://alphahinex.github.io/contents/sonar-either-re-interrupt-or-rethrow/no-loop.png)

上面这个段代码很简单，主要就是在一个调用线程中断方法的前后，打印线程是否被中断的标志位，通过结果我们可以看到，当调用interrupt后，my thread线程的interrrupted状态位变为true，所以退出循环，方法结束。

让我们修改一下，加入一段休眠并且捕获中断异常，做相应业务处理。

```java
public class ThreadInterruptedDemo {

    public static void main(String[] args) throws InterruptedException {
        Thread myThread = new MyThread();
        myThread.setName("my thread");
        myThread.start();
        Thread.sleep(10);
        System.out.println("call myThread interrupt method...");
        myThread.interrupt();
    }
}

class MyThread extends Thread {
    @Override
    public void run() {
        String threadName = Thread.currentThread().getName();
        //打印当前线程是否被中断
        System.out.println(threadName + " interrrupted is: " + isInterrupted());
        while (!isInterrupted()) {
            System.out.println(threadName + " is running");
            //打印当前线程是否被中断
            System.out.println(threadName + " circle println interrrupted is: "
                    + isInterrupted());
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                //哪怕你处理并记录了异常，sonar也会报Either re-interrupt this method or rethrow the "InterruptedException"
                //被外界中断你后，再次打印当前线程是否被中断
                System.out.println(threadName + " InterruptedException println interrrupted is: "
                        + isInterrupted());
            }
        }
        System.out.println(threadName + "end interrrupted is: " + isInterrupted());
    }
}
```

如此我们期望在捕获到外界中断的方法并做出相关业务处理后结束方法。

然而很遗憾，从结果我们可以看出，在输出中断的打印之后，线程并没有退出循环而是一直的在执行，因为通过打印我们可以看出此时的标志位居然还是false。

![only catch](https://alphahinex.github.io/contents/sonar-either-re-interrupt-or-rethrow/only-catch.png)

这就是sonar在此处会有提示的原因，而标志位为false是因为在调用会抛出InterruptedException异常的方法（例如sleep），异常被捕获之后自己会把标志位重置为false。

按照sonar建议，修改如下：

```java
public class ThreadInterruptedDemo {

    public static void main(String[] args) throws InterruptedException {
        Thread myThread = new MyThread();
        myThread.setName("my thread");
        myThread.start();
        Thread.sleep(10);
        System.out.println("call myThread interrupt method...");
        myThread.interrupt();
    }

}

class MyThread extends Thread {
    @Override
    public void run() {
        String threadName = Thread.currentThread().getName();
        System.out.println(threadName + " interrrupted is: " + isInterrupted());
        while (!isInterrupted()) {
            System.out.println(threadName + " is running");
            System.out.println(threadName + " circle println interrrupted is: "
                    + isInterrupted());
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                //哪怕你处理并记录了异常，sonar也会报Either re-interrupt this method or rethrow the "InterruptedException"
                //被外界中断你后，再次打印当前线程是否被中断
                System.out.println(threadName + " InterruptedException println interrrupted is: "
                        + isInterrupted());
                //再次更新中断标志位为true
                Thread.currentThread().interrupt();
                System.out.println(threadName + " InterruptedException 2 println interrrupted is: "
                        + isInterrupted());
            }
        }
        System.out.println(threadName + " exit circle interrrupted is: " + isInterrupted());
    }
}
```

此时已经方法已经能够正常结束了。

![re-interrupt](https://alphahinex.github.io/contents/sonar-either-re-interrupt-or-rethrow/re-interrupt.png)

所以对于sonar这个扫描的问题原因，就是因为在catch到中断异常后，线程是否中断的标志位会被重置为false，如果我们此时再通过标志位进行一些逻辑处理，且又没有在catch代码块中二次发出中断请求，就会出现问题。