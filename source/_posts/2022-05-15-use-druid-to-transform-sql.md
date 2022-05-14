---
id: use-druid-to-transform-sql
title: "使用 Alibaba Druid 进行 SQL 翻译"
description: "Alibaba Druid 不仅仅是一个连接池组件"
date: 2022.05.15 10:34
categories:
    - Java
    - Database
tags: [MySQL, H2, Java, Database, Druid]
keywords: MySQL, H2, druid, parser, converter, SQL, SQLUtils
cover: /contents/use-druid-to-transform-sql/cover.jpeg
---

Alibaba Druid
=============

![logo](/contents/use-druid-to-transform-sql/druid-logo.jpg)

[Alibaba Druid](https://github.com/alibaba/druid) 是阿里云计算平台 [DataWorks](https://help.aliyun.com/document_detail/137663.html) 团队出品，为监控而生的数据库连接池。

Apache 旗下也有一个 [Apache Druid](https://github.com/apache/druid)，是一个高性能的实时分析数据库。

本文提到的 `Druid`，指 `Alibaba Druid`。

`Druid` 其实是一个 JDBC 组件库，不仅包含数据库连接池组件，还有 SQL Parser 等组件，被大量业务和技术产品使用或集成，从 GitHub 的 Start 数量（`25.5k`），和 `Used by` 数量（`206k`）可见一斑。

![github](/contents/use-druid-to-transform-sql/github.png)

网上关于 `Druid` 的文档，大多是数据库连接池组件的。SQL Parser 组件的文档，目前以官网 [wiki](https://github.com/alibaba/druid/wiki) 中的内容为主。

SQL Parser
----------

[SQL Parser](https://github.com/alibaba/druid/wiki/SQL-Parser) 文档对此组件进行了简单清晰的介绍，重点内容如下：

> Druid的 sql parser 是目前支持各种数据语法最完备的 SQL Parser。目前对各种数据库的支持如下：
>
> |数据库	|DML	|DDL|
> |:--------|:------|:--|
> |odps	|完全支持	|完全支持|
> |mysql	|完全支持	|完全支持|
> |postgresql	|完全支持	|完全支持|
> |oracle	|支持大部分	|支持大部分|
> |sql server	|支持常用的	|支持常用的ddl|
> |db2	|支持常用的	|支持常用的ddl|
> |hive	|支持常用的	|支持常用的ddl|
>
> druid 还缺省支持 sql-92 标准的语法，所以也部分支持其他数据库的 sql 语法。

> Druid SQL Parser 分三个模块：
>
> * Parser：parser 是将输入文本转换为 ast（抽象语法树），parser 有包括两个部分，Parser 和Lexer，其中Lexer实现词法分析，Parser实现语法分析。
> * AST：AST是Abstract Syntax Tree的缩写，也就是抽象语法树。AST是parser输出的结果。
> * Visitor：Visitor是遍历AST的手段，是处理AST最方便的模式，Visitor是一个接口，有缺省什么都没做的实现VistorAdapter。

> Druid SQL Parser 的使用场景
> * MySql SQL全量统计
> * Hive/ODPS SQL执行安全审计
> * 分库分表SQL解析引擎
> * 数据库引擎的SQL Parser

还有一些更具体的场景，比如：

* [SQL 格式化](https://github.com/alibaba/druid/wiki/SQL_Format)
* [SQL 添加条件](https://github.com/alibaba/druid/wiki/%E5%A6%82%E4%BD%95%E4%BF%AE%E6%94%B9SQL%E6%B7%BB%E5%8A%A0%E6%9D%A1%E4%BB%B6)
* [SQL 移除条件](https://github.com/alibaba/druid/wiki/SQL_RemoveCondition_demo)
* [SQL 参数化](https://github.com/alibaba/druid/wiki/SQL_Parser_Parameterize)
* [SQL 翻译](https://github.com/alibaba/druid/wiki/SQL-Parser#6-sql%E7%BF%BB%E8%AF%91)

SQL 翻译
========

> SQL-92、SQL-99 等都是标准 SQL，mysql/oracle/pg/sqlserver/odps 等都是方言，也就是dialect。parser/ast/visitor 都需要针对不同的方言进行特别处理。—— [方言](https://github.com/alibaba/druid/wiki/SQL-Parser#45-%E6%96%B9%E8%A8%80)

SQL 翻译，即将一种方言，翻译成另一种。比如输入 MySQL 的 SQL 脚本，使用 MySQL 的 Parser 进行解析，再使用 Oracle 的 Visitor 进行遍历输出，就可以完成 MySQL 脚本到 Oracle 脚本的翻译：

```java
List<SQLStatement> sqlStatements = SQLUtils.parseStatements(mysqlSql, DbType.mysql);

String oracleSql = SQLUtils.toSQLString(sqlStatements, DbType.oracle);
System.out.println(oracleSql);
```

然而在执行类似上面的代码片段进行 SQL 翻译时，你可能会遇到类似下面的报错：

```log
java.lang.IllegalArgumentException: not support visitor type : com.alibaba.druid.sql.dialect.oracle.visitor.OracleOutputVisitor

	at com.alibaba.druid.sql.dialect.mysql.ast.statement.MySqlStatementImpl.accept0(MySqlStatementImpl.java:37)
	at com.alibaba.druid.sql.dialect.mysql.ast.statement.MySqlHintStatement.accept0(MySqlHintStatement.java:42)
	at com.alibaba.druid.sql.ast.SQLObjectImpl.accept(SQLObjectImpl.java:49)
	at com.alibaba.druid.sql.SQLUtils.toSQLString(SQLUtils.java:436)
	at com.alibaba.druid.sql.SQLUtils.toSQLString(SQLUtils.java:364)
	at com.alibaba.druid.sql.SQLUtils.toSQLString(SQLUtils.java:356)
```

这种时候，想完成翻译的动作，就需要付出一些努力了。下面通过一个实例，来看一下如何将 MySQL 的脚本翻译成 [H2](https://h2database.com/) 可用的脚本。


MySQL 脚本翻译成 H2 脚本
======================

在当前最新的 [1.2.8](https://github.com/alibaba/druid/tree/1.2.8) Release 版本中，[H2OutputVisitor.java](https://github.com/alibaba/druid/blob/1.2.8/src/main/java/com/alibaba/druid/sql/dialect/h2/visitor/H2OutputVisitor.java) 针对 H2 的方言处理并不多，直接进行翻译时，大概率会遇到类似上面的报错，或翻译出来的结果无法在 H2 中执行。

此时需要参照官方文档 [实现自己的Visitor](https://github.com/alibaba/druid/wiki/SQL_Parser_Demo_visitor#1-%E5%AE%9E%E7%8E%B0%E8%87%AA%E5%B7%B1%E7%9A%84visitor)（或如下示例），在 Visitor 中针对 H2 方言进行处理，如：

```java
public class CustomH2OutputVisitor extends H2OutputVisitor {

    public CustomH2OutputVisitor(Appendable appender) {
        super(appender);
    }

    public CustomH2OutputVisitor(Appendable appender, DbType dbType) {
        super(appender, dbType);
    }

    public CustomH2OutputVisitor(Appendable appender, boolean parameterized) {
        super(appender, parameterized);
    }

    public boolean visit(SQLCreateDatabaseStatement x) {

        /*
        https://h2database.com/html/commands.html#create_schema
        CREATE SCHEMA [ IF NOT EXISTS ]
        { name [ AUTHORIZATION ownerName ] | [ AUTHORIZATION ownerName ] }
        [ WITH tableEngineParamName [,...] ]
        */

        printUcase("CREATE SCHEMA ");

        if (x.isIfNotExists()) {
            printUcase("IF NOT EXISTS ");
        }
        x.getName().accept(this);

        return false;
    }

}
```

可参照下方示例，或 [文档](https://github.com/alibaba/druid/wiki/SQL_Parser_Demo_visitor#2-%E4%BD%BF%E7%94%A8visitor) 使用自己实现的 Visitor：

```java
String sql = "CREATE SCHEMA hinex;CREATE TABLE hinex.employees (jobTitle VARCHAR2(50));CREATE FULLTEXT INDEX hinex.jobTitle USING BTREE ON hinex.employees(jobTitle);";

List<SQLStatement> stmtList = SQLUtils.parseStatements(sql, DbType.mysql);

StringBuilder out = new StringBuilder();
SQLASTOutputVisitor visitor = new CustomH2OutputVisitor(out);

for (SQLStatement stmt : stmtList) {
    stmt.accept(visitor);
    visitor.println();
}

System.out.println(out);
```

运行上面代码，会得到如下结果：

```output
CREATE SCHEMA hinex;
CREATE TABLE hinex.employees (
	jobTitle VARCHAR2(50)
);
CREATE INDEX hinex.jobTitle ON hinex.employees (jobTitle);
```

然而在逐步提升方言的翻译能力时，你会发现有些问题无法仅通过扩展 Visitor 来实现，比如上面提到的 `java.lang.IllegalArgumentException: not support visitor type : com.alibaba.druid.sql.dialect.oracle.visitor.OracleOutputVisitor` 这个报错，是由 `MySqlStatementImpl.java:37` 抛出的：

```java
@Override
protected void accept0(SQLASTVisitor visitor) {
    if (visitor instanceof MySqlASTVisitor) {
        accept0((MySqlASTVisitor) visitor);
    } else {
        throw new IllegalArgumentException("not support visitor type : " + visitor.getClass().getName());
    }
}
```

在这个 MySQL 的 `Statement` 中，仅支持通过 `MySqlASTVisitor` 进行遍历，遇到其他类型的 Visitor 都会抛出异常。如果我们是想将 MySQL 方言翻译成其他的方言，就需要修改这个类使其支持其他类型的 Visitor。

这类修改就不仅仅是扩展 `Druid` 了，而是要覆盖它的默认行为。这种覆盖类的方式，在 [Override same class](https://alphahinex.github.io/2020/12/27/override-same-class/) 中有所讨论：

* 如果我们能够将定制的类以 class 的形式放到发布包中，并且发布包是依赖 Servlet 容器运行的，依照 Servlet 规范中的要求及推荐，以及 Tomcat 的具体实现，能够实现覆盖；
* 但如果我们的目标是提供一个基础类库，供其他项目依赖，即定制的类也是在 JAR 包里时，就不好办了，因为原版 `Druid` JAR 包中，和我们基础类库的 JAR 包中，会存在相同的类。

怎么办？提供两种方法。

Pull Request
------------

可以将扩展内容直接通过 Pull Request 提交给 Druid，如 [#4777](https://github.com/alibaba/druid/pull/4777) 和 [#4778](https://github.com/alibaba/druid/pull/4778)，待代码合并进主干，并且 Druid 发布包含这些 PR 内容的新版本后，就可以直接使用了。

maven-assembly-plugin
---------------------

当然，上面那种方法的流程可能会比较长，如果等不及，可以在定制的类库中，使用 [maven-assembly-plugin](https://maven.apache.org/plugins/maven-assembly-plugin/) 来将所有的依赖发布成一个定制版的 `Druid` JAR 包，在使用时用定制版替代原版即可。

在 `pom.xml` 中添加类似下面的内容：

```xml
<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-assembly-plugin</artifactId>
  <configuration>
    <appendAssemblyId>false</appendAssemblyId>
    <descriptorRefs>
      <descriptorRef>jar-with-dependencies</descriptorRef>
    </descriptorRefs>
  </configuration>
  <executions>
    <execution>
      <id>make-assembly</id> <!-- this is used for inheritance merges -->
      <phase>package</phase> <!-- bind to the packaging phase -->
      <goals>
        <goal>single</goal>
      </goals>
    </execution>
  </executions>
</plugin>
```

这样在执行 `mvn package` 打包的时候，就会构建出一个包含了所有依赖的版本。通过 `install` 或 `deploy` 等命令将定制版 `Druid` 发布到 Maven 仓库中，就可以被其他项目所使用了。

> 注意：仅发布包含依赖版本时，需设置上面的 `appendAssemblyId` 属性为 `false`，否则会发布包含依赖和不包含依赖两个版本。

在 [MySQL 脚本转 H2](https://alphahinex.github.io/2022/05/08/mysql2h2/) 中介绍过一个 `mysql2h2-converter` 项目，其 [v0.2.2](https://github.com/AlphaHinex/mysql2h2-converter/tree/v0.2.2) 版本是使用 [JavaCC](https://alphahinex.github.io/2022/05/01/javacc-in-action/) 编写的 MySQL Parser。[v0.3.0](https://github.com/AlphaHinex/mysql2h2-converter/tree/v0.3.0) 版本便是基于 Druid 1.2.8 进行的扩展，并提供了可以独立使用的 [命令行工具](https://github.com/AlphaHinex/mysql2h2-converter/releases/download/v0.3.0/mysql2h2-converter-tool-0.3.0.jar) 和可被项目依赖的 [定制版本](https://jitpack.io/#AlphaHinex/mysql2h2-converter/v0.3.0)，在需要进行 MySQL 脚本转 H2 脚本操作的时候，可以直接使用。

这里是其中最主要的 [H2OutputVisitor.java](https://github.com/AlphaHinex/mysql2h2-converter/blob/enhance/src/main/java/com/alibaba/druid/sql/dialect/h2/visitor/H2OutputVisitor.java) 和 [单元测试](https://github.com/AlphaHinex/mysql2h2-converter/blob/enhance/src/test/java/com/granveaud/mysql2h2converter/converter/ConverterTest.java) 。