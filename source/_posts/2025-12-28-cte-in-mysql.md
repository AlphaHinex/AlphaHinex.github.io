---
id: cte-in-mysql
title: "【转】解析 MySQL CTE：WITH 与 WITH RECURSIVE"
description: "在开发过程中，发现在 MYSQL 的 Mapper 文件中会用到 WITH 关键字，有一些疑问：为什么要用 WITH 和 WITH RECURSIVE ？是什么？有何区别？"
date: 2025.12.28 10:26
categories:
    - Database
tags: [SQL, MySQL]
keywords: CTE, Common Table Expressions, WITH, WITH RECURSIVE, MySQL, SQL
cover: /contents/covers/cte-in-mysql.png
---

- 原文地址：https://wyiyi.github.io/amber/2025/12/20/CTE/

在开发过程中，发现在 `MYSQL` 的 `Mapper` 文件中会用到 `WITH` 关键字，有一些疑问：为什么要用`WITH` 和 `WITH RECURSIVE` ？是什么？有何区别？

![](https://alphahinex.github.io/contents/covers/cte-in-mysql.png)

## 一、 CTE 的含义
`MySQL` 从 `8.0` 开始支持 `WITH` 语法，即：[Common Table Expressions （CTE），公用表表达式](https://dev.mysql.com/doc/refman/8.0/en/with.html#common-table-expressions)。

`CTE` 是一个命名的临时结果集合，仅在单个 `SQL` 语句（`select`、`insert`、`update` 或 `delete`）的执行范围内存在。
允许用户在单个查询中定义临时的命名结果集，从而提升复杂查询的可读性和结构化程度。

`CTE` 的主要目的是**将复杂的查询逻辑分解为多个简单、可读的步骤**，从而提升 `SQL` 代码的结构化程度和可维护性。

`CTE` 可以分为两种类型：`非递归 CTE` 和`递归 CTE`。

## 二、 适用场景
为什么需要使用 `WITH` ？

假设场景：找出每个学科中，分数高于该科目平均分的学生。

```text
插入8条数据：
INSERT INTO students (name, subject, score) VALUES
-- 数学: 分数 80, 90, 70 -> 平均分 80
('张三', '数学', 90),  -- 高于平均分
('李四', '数学', 80),  -- 等于平均分
('王五', '数学', 70),  -- 低于平均分

-- 物理: 分数 85, 95 -> 平均分 90
('赵六', '物理', 95),  -- 高于平均分
('孙七', '物理', 85),  -- 低于平均分

-- 化学: 分数 88, 92, 100 -> 平均分 93.33
('周八', '化学', 100), -- 高于平均分
('吴九', '化学', 92),  -- 低于平均分
('郑十', '化学', 88);  -- 低于平均分
```

**方式一：不使用 WITH（传统子查询）**

```SQL
mysql> SELECT s1.*
FROM students s1
WHERE s1.score > (
   -- 每次都要为 s1 的科目计算一次平均分
   SELECT AVG(s2.score)
   FROM students s2
   WHERE s2.subject = s1.subject
);

+----+------+---------+--------+
| id | name | subject | score  |
+----+------+---------+--------+
|  1 | 张三 | 数学    |  90.00 |
|  4 | 赵六 | 物理    |  95.00 |
|  6 | 周八 | 化学    | 100.00 |
+----+------+---------+--------+
3 rows in set (0.01 sec)
```

**方式二：用 WITH**

```SQL
-- 先算好每个科目的平均分
mysql> WITH SubjectAvg AS (
    SELECT subject, AVG(score) AS avg_score
    FROM students
    GROUP BY subject
)
-- 再用这个平均分去筛选学生
SELECT s.*
FROM students s
JOIN SubjectAvg a ON s.subject = a.subject
WHERE s.score > a.avg_score;

+----+------+---------+--------+
| id | name | subject | score  |
+----+------+---------+--------+
|  1 | 张三 | 数学    |  90.00 |
|  4 | 赵六 | 物理    |  95.00 |
|  6 | 周八 | 化学    | 100.00 |
+----+------+---------+--------+
3 rows in set (0.00 sec)
```
这样看来：

| 特性 | 方式一 | 方式二 |
|:-------|:--------------------|:------------------------|
| **逻辑结果**   | 等价                  | 等价                      |
| **核心思想**   | 对每一行数据，都重新计算一次关联值   | 先将所有关联值一次性算好，再进行匹配      |
| **性能**     | 尤其在大数据量下，通常较差（0.01 sec）     | 性能稳定且可预测，通常极佳（0.00 sec） |
| **形象比喻做菜** | 手忙脚乱，现用现配           | 专业从容，提前备料               |

### CTE 可以分为两种类型
1. 非递归 `CTE` 的核心价值在于**提升可读性和模块化**。
    - **简化复杂查询：** 将一个需要多步计算的复杂查询分解成多个 `CTE`，每一步逻辑清晰，易于理解和维护。
    - **代码复用：** 当一个查询中需要多次使用同一个子查询时，可以将其定义为 `CTE`，避免重复代码。
    - **替代复杂的嵌套子查询：** 用线性的 `CTE` 链条代替深层嵌套的子查询，使代码结构更扁平。

2. 递归 `CTE` 是处理层级结构或图结构数据的“神器”。
   - **组织架构/员工层级查询：** 查询部门及其所有下级部门（包括所有层级的下级部门）。
   - **物料清单分解：** 计算一个产品由哪些零件组成，以及每个零件的成本。
   - **文件系统目录树遍历：** 查询某个目录及其所有子目录下的所有文件。
   - ...

## 三、 非递归 CTE
`非递归 CTE` 是 `CTE` 的基础形式，本质上是一个可以复用的子查询。

### 3.1 语法
要指定公共表表达式，请使用 `WITH` 子句，该子句包含一个或多个以逗号分隔的子句。
每个子句都提供一个用于生成结果集的子查询，并为该子查询关联一个名称。

```SQL
WITH
    cte1 AS (SELECT a, b FROM table1),
    cte2 AS (SELECT c, d FROM table2)
SELECT b, d FROM cte1 JOIN cte2
WHERE cte1.a = cte2.c;
```

在使用了 `WITH` 子句的语句里，可以通过每个 `CTE` 的名字来查询它所生成的结果集。

### 3.2 列名定义规则

`CTE` 的列名可以通过两种方式定义：

1. **显式指定列名**：如果 `CTE` 名称后跟一个带括号的名称列表，那么这些名称就是列名：

```SQL
WITH cte (col1, col2) AS
         (SELECT 1, 2
         UNION ALL
         SELECT 3, 4)
SELECT col1, col2
FROM cte;
```

2. **从子查询中继承：** 列名来源于 AS (subquery) 部分中第一个 SELECT 的选择列表：

```SQL
WITH cte AS
        (SELECT 1 AS col1, 2 AS col2
         UNION ALL
         SELECT 3, 4)
SELECT col1, col2
FROM cte;
```
### 3.3. 使用上下文

`WITH` 子句非常灵活，可以在多种 `SQL` 语句中使用：

1. 在 `SELECT`、`UPDATE` 和 `DELETE` 语句的开头：

```SQL
WITH ... SELECT ...
WITH ... UPDATE ...
WITH ... DELETE ...
```

**示例：** 更新所有上月活跃但本月不活跃的用户。

```SQL
WITH LastMonthActive AS (
  SELECT user_id FROM activity_log WHERE MONTH(log_date) = MONTH(CURDATE() - INTERVAL 1 MONTH)
),
ThisMonthActive AS (
  SELECT user_id FROM activity_log WHERE MONTH(log_date) = MONTH(CURDATE())
)
UPDATE users
SET status = 'dormant'
WHERE user_id IN (SELECT user_id FROM LastMonthActive)
AND user_id NOT IN (SELECT user_id FROM ThisMonthActive);
```

2. 在子查询（包括派生表子查询）的开头：

```SQL
SELECT ... WHERE id IN (WITH ... SELECT ...) ...
SELECT * FROM (WITH ... SELECT ...) AS dt ...
```

3. 紧跟在包含 `SELECT` 语句的 `SELECT` 之前：

```SQL
INSERT ... WITH ... SELECT ...
REPLACE ... WITH ... SELECT ...
CREATE TABLE ... WITH ... SELECT ...
CREATE VIEW ... WITH ... SELECT ...
DECLARE CURSOR ... WITH ... SELECT ...
EXPLAIN ... WITH ... SELECT ...
```

**示例：** 将聚合后的数据插入报表表。

```SQL
WITH DailySales AS (
  SELECT product_id, SUM(amount) AS total_sales
  FROM orders
  WHERE order_date = CURDATE() - INTERVAL 1 DAY
  GROUP BY product_id
)
INSERT INTO sales_report (product_id, sales_amount)
SELECT product_id, total_sales FROM DailySales;
```

## 四、 递归 CTE
`递归 CTE` 是一种特殊的 `CTE`，它的子查询会引用其自身的名称，从而实现循环遍历。

### 4.1 语法
如果一个 `CTE` 的子查询引用了其自身的名称，那么该 `CTE` 就是递归的。
如果 `WITH` 子句中的任何 `CTE` 是递归的，则必须包含 `RECURSIVE` 关键字。

**简单来说：就是一个在它的子查询里引用了自己名字的 CTE。**
```SQL
WITH RECURSIVE cte (n) AS
   (
       -- 1. 锚点成员：提供初始结果集，递归的起点
       SELECT 1
       UNION ALL
       -- 2. 递归成员：引用 CTE 自身，不断产生新数据，直到条件不满足
       SELECT n + 1
       FROM cte
       WHERE n < 5)
-- 3. 最终查询：从递归生成的完整结果集中查询数据
SELECT *
FROM cte;
```

```text
+------+
| n    |
+------+
|    1 |  -- 来自锚点成员
|    2 |  -- 来自递归成员 (1+1)
|    3 |  -- 来自递归成员 (2+1)
|    4 |  -- 来自递归成员 (3+1)
|    5 |  -- 来自递归成员 (4+1)
+------+
```

### 4.2 结构解析
一个递归 `CTE` 的子查询必须由两部分组成，用 `UNION ALL` 或 `UNION` `[DISTINCT]` 连接：

- **锚点成员：** 执行一次，返回初始结果集。它是递归的“种子”。
- **递归成员：** 反复执行，直到不再返回任何行。它的 `WHERE` 子句是递归的终止条件，非常重要，否则会陷入无限循环。

## 五、WITH 与 WITH RECURSIVE 的区别：

| 特性 | WITH (非递归)           | WITH RECURSIVE (递归)      |
| :--- |:---------------------|:-------------------------|
| **关键字** | `WITH`               | `WITH RECURSIVE`         |
| **自引用** | **不允许**，CTE 不能引用自身   | **允许**，CTE 必须引用自身以实现递归   |
| **主要用途** | 查询逻辑的模块化、代码复用、简化复杂查询 | 遍历具有层级或父子关系的数据结构         |
| **结构** | 一个或多个独立的子查询          | 必须包含**锚点成员**和**递归成员**两部分 |
| **性能** | 通常等同于派生表（子查询），性能相近   | 可能非常消耗资源，必须有明确的终止条件      |
