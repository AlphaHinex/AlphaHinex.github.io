---
id: transform-d3-calendar-view-to-github-contributions-step-by-step
title:  "一步一步将 d3.js Calendar View 转变成 GitHub Contributions"
date:   2015-11-26 16:12:47
modified: 2015-12-02 13:23:49
categories: Javascript
tags: [Data Visualization, D3, GitHub, Calendar, Contributions]
cover: /contents/calendar-view/all.gif
---

GitHub Contributions 日历热图表述力强，容易上瘾，并且引发了多种玩法：涂满或涂成名字、万圣节颜色……，让我们使用 d3.js 提供的 Calendar View 示例，一步一步将其修改成 GitHub 的样式，Let's go！

![All](/contents/calendar-view/all.gif)

先将 [d3.js](http://d3js.org/) 提供的 [Calendar View](http://bl.ocks.org/mbostock/4063318) 做一个 [快照](/contents/calendar-view/snapshot.zip)，以免示例代码更新对本文中的修改造成影响。

修改前的文件为：

* [before.html](/contents/calendar-view/before.html)
* [dji.csv](/contents/calendar-view/dji.csv)

修改后文件为：

* [after.html](/contents/calendar-view/after.html)

最终效果见上面动态图。

只留一年
-------

暂时先只保留 `2008` 年的日历

![One year](/contents/calendar-view/2.png)

```diff
@@ -47,7 +47,7 @@ var color = d3.scale.quantize()
     .range(d3.range(11).map(function(d) { return "q" + d + "-11"; }));

 var svg = d3.select("body").selectAll("svg")
-    .data(d3.range(1990, 2011))
+    .data(d3.range(2008,2009))
   .enter().append("svg")
     .attr("width", width)
     .attr("height", height)
```

修改样式
-------

按照 `GitHub Contributions` 对样式进行调整，包括去掉月份边框，调整单元格大小、间距及颜色

![Change styles](/contents/calendar-view/3.png)

```diff
@@ -8,27 +8,20 @@ body {
 }

 .day {
-  fill: #fff;
-  stroke: #ccc;
+  width: 11px;
+  height: 11px;
+  fill: rgb(238, 238, 238);
 }

-.month {
-  fill: none;
-  stroke: #000;
-  stroke-width: 2px;
+.day:hover {
+  stroke: #555;
+  stroke-width: 1px;
 }

-.RdYlGn .q0-11{fill:rgb(165,0,38)}
-.RdYlGn .q1-11{fill:rgb(215,48,39)}
-.RdYlGn .q2-11{fill:rgb(244,109,67)}
-.RdYlGn .q3-11{fill:rgb(253,174,97)}
-.RdYlGn .q4-11{fill:rgb(254,224,139)}
-.RdYlGn .q5-11{fill:rgb(255,255,191)}
-.RdYlGn .q6-11{fill:rgb(217,239,139)}
-.RdYlGn .q7-11{fill:rgb(166,217,106)}
-.RdYlGn .q8-11{fill:rgb(102,189,99)}
-.RdYlGn .q9-11{fill:rgb(26,152,80)}
-.RdYlGn .q10-11{fill:rgb(0,104,55)}
+.cv .lv1 {fill: #d6e685;}
+.cv .lv2 {fill: #8cc665;}
+.cv .lv3 {fill: #44a340;}
+.cv .lv4 {fill: #1e6823;}

 </style>
 <body>
@@ -37,21 +30,21 @@ body {

 var width = 960,
     height = 136,
-    cellSize = 17; // cell size
+    cellSize = 13; // cell size

 var percent = d3.format(".1%"),
     format = d3.time.format("%Y-%m-%d");

 var color = d3.scale.quantize()
     .domain([-.05, .05])
-    .range(d3.range(11).map(function(d) { return "q" + d + "-11"; }));
+    .range(d3.range(1,5).map(function(d) { return "lv" + d; }));

 var svg = d3.select("body").selectAll("svg")
     .data(d3.range(2008,2009))
   .enter().append("svg")
     .attr("width", width)
     .attr("height", height)
-    .attr("class", "RdYlGn")
+    .attr("class", "cv")
   .append("g")
     .attr("transform", "translate(" + ((width - cellSize * 53) / 2) + "," + (height - cellSize * 7 - 1) + ")");

@@ -73,12 +66,6 @@ var rect = svg.selectAll(".day")
 rect.append("title")
     .text(function(d) { return d; });

-svg.selectAll(".month")
-    .data(function(d) { return d3.time.months(new Date(d, 0, 1), new Date(d + 1, 0, 1)); })
-  .enter().append("path")
-    .attr("class", "month")
-    .attr("d", monthPath);
-
 d3.csv("dji.csv", function(error, csv) {
   if (error) throw error;

@@ -93,17 +80,6 @@ d3.csv("dji.csv", function(error, csv) {
       .text(function(d) { return d + ": " + percent(data[d]); });
 });

-function monthPath(t0) {
-  var t1 = new Date(t0.getFullYear(), t0.getMonth() + 1, 0),
-      d0 = t0.getDay(), w0 = d3.time.weekOfYear(t0),
-      d1 = t1.getDay(), w1 = d3.time.weekOfYear(t1);
-  return "M" + (w0 + 1) * cellSize + "," + d0 * cellSize
-      + "H" + w0 * cellSize + "V" + 7 * cellSize
-      + "H" + w1 * cellSize + "V" + (d1 + 1) * cellSize
-      + "H" + (w1 + 1) * cellSize + "V" + 0
-      + "H" + (w0 + 1) * cellSize + "Z";
-}
-
 d3.select(self.frameElement).style("height", "2910px");

 </script>
 ```

过去一年
-------

将 Calendar View 显示的一整年调整为过去一年

![Last whole year](/contents/calendar-view/4.png)

```diff
@@ -39,27 +39,36 @@ var color = d3.scale.quantize()
     .domain([-.05, .05])
     .range(d3.range(1,5).map(function(d) { return "lv" + d; }));

-var svg = d3.select("body").selectAll("svg")
-    .data(d3.range(2008,2009))
-  .enter().append("svg")
+var svg = d3.select("body").append("svg")
     .attr("width", width)
     .attr("height", height)
     .attr("class", "cv")
   .append("g")
     .attr("transform", "translate(" + ((width - cellSize * 53) / 2) + "," + (height - cellSize * 7 - 1) + ")");

-svg.append("text")
-    .attr("transform", "translate(-6," + cellSize * 3.5 + ")rotate(-90)")
-    .style("text-anchor", "middle")
-    .text(function(d) { return d; });
+var today = new Date();
+var lastYear = new Date(today.getTime() - 365 * 24 * 60 * 60 * 1000);
+var shiftWeeks = 53 - d3.time.weekOfYear(lastYear);
+
+var shiftWeek = function(d) {
+  var year = d.getFullYear();
+  var thisYear = today.getFullYear();
+  var weekOfYear = d3.time.weekOfYear(d);
+  if (year < thisYear) {
+    weekOfYear = weekOfYear - 53 + shiftWeeks;
+  } else {
+    weekOfYear += shiftWeeks - 1;
+  }
+  return weekOfYear;
+};

 var rect = svg.selectAll(".day")
-    .data(function(d) { return d3.time.days(new Date(d, 0, 1), new Date(d + 1, 0, 1)); })
+    .data(d3.time.days(lastYear, today))
   .enter().append("rect")
     .attr("class", "day")
     .attr("width", cellSize)
     .attr("height", cellSize)
-    .attr("x", function(d) { return d3.time.weekOfYear(d) * cellSize; })
+    .attr("x", function(d) { return shiftWeek(d) * cellSize; })
     .attr("y", function(d) { return d.getDay() * cellSize; })
     .datum(format);
```

添加标签
-------

添加周及月份标签

![Add labels](/contents/calendar-view/5.png)

```diff
@@ -46,6 +46,18 @@ var svg = d3.select("body").append("svg")
   .append("g")
     .attr("transform", "translate(" + ((width - cellSize * 53) / 2) + "," + (height - cellSize * 7 - 1) + ")");

+svg.append('text')
+  .attr('transform', 'translate(-14,' + cellSize*1.8 + ')')
+  .text('一');
+
+svg.append('text')
+  .attr('transform', 'translate(-14,' + cellSize*3.8 + ')')
+  .text('三');
+
+svg.append('text')
+  .attr('transform', 'translate(-14,' + cellSize*5.8 + ')')
+  .text('五');
+
 var today = new Date();
 var lastYear = new Date(today.getTime() - 365 * 24 * 60 * 60 * 1000);
 var shiftWeeks = 53 - d3.time.weekOfYear(lastYear);
@@ -62,6 +74,18 @@ var shiftWeek = function(d) {
   return weekOfYear;
 };

+var startYear = lastYear.getFullYear();
+var startMonth = lastYear.getDate() === 1 ? lastYear.getMonth() : lastYear.getMonth() + 1;
+for (var i = 0; i < 12; i ++) {
+  var s = new Date(startYear, startMonth + i, 1);
+  var w = shiftWeek(s) + (s.getDay() > 0 ? 1 : 0);
+  if (w > 52) {
+    break;
+  }
+  var m = s.getMonth() + 1;
+  var l = m > 9 ? m : '0' + m;
+  svg.append('text')
+    .attr('transform', 'translate(' + cellSize * w + ', -5)')
+    .text(l);
+}
+
 var rect = svg.selectAll(".day")
     .data(d3.time.days(lastYear, today))
   .enter().append("rect")
```

修改数据源
--------

将数据来源由 `csv` 调整为 `object`

![Change data source](/contents/calendar-view/6.png)

```diff
@@ -99,19 +99,17 @@ var rect = svg.selectAll(".day")
 rect.append("title")
     .text(function(d) { return d; });

-d3.csv("dji.csv", function(error, csv) {
-  if (error) throw error;
-
-  var data = d3.nest()
-    .key(function(d) { return d.Date; })
-    .rollup(function(d) { return (d[0].Close - d[0].Open) / d[0].Open; })
-    .map(csv);
-
-  rect.filter(function(d) { return d in data; })
-      .attr("class", function(d) { return "day " + color(data[d]); })
-    .select("title")
-      .text(function(d) { return d + ": " + percent(data[d]); });
-});
+
+var data = {
+  '2015-11-24': 0,
+  '2015-11-25': -0.5,
+  '2015-11-26': 0.5
+};
+
+rect.filter(function(d) { return d in data; })
+    .attr("class", function(d) { return "day " + color(data[d]); })
+  .select("title")
+    .text(function(d) { return d + ": " + percent(data[d]); });

 d3.select(self.frameElement).style("height", "2910px");
```
