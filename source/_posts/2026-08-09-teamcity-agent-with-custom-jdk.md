---
id: teamcity-agent-with-custom-jdk
title: "TeamCity Agent 使用自定义 JDK 版本执行构建"
description: "自定义工具的安装及引用说明"
date: 2026.08.09 10:26
categories:
    - Java
tags: [Java, TeamCity, JDK]
keywords: TeamCity, custom JDK, java, TeamCity Agent, node, Node.js, custom archive, tools, build, build step
cover: /contents/teamcity-agent-with-custom-jdk/cover.png
---

## TeamCity Agent JDK

[TeamCity On-Premises 2026.1 Agent 支持的 Java 版本](https://www.jetbrains.com/help/teamcity/2026.1/supported-platforms-and-environments.html#Supported+Java+Versions+for+TeamCity+Agent) 是 `OpenJDK and Oracle Java 21 to 25 (32 or 64 bit)`，在 `Agent JDKs` 页面可以上传其他 JDK 版本，但不能低于最小的支持版本：

![Agent JDKs](https://alphahinex.github.io/contents/teamcity-agent-with-custom-jdk/agent-jdks.png)

上面提到的 Java 版本，是指运行 TeamCity Agent 所需的 Java 运行环境版本，不是指在 Agent 中执行构建所能使用的 Java 版本。

当有些项目需要使用低版本 JDK 或其他未绑定的工具执行构建时，若不想提前在 Agent 中执行安装（如 Agent 运行在容器中），可通过在 Agent 中 [安装自定义工具](https://www.jetbrains.com/help/teamcity/installing-agent-tools.html) 实现。

## 使用自定义 JDK 执行构建

以安装 [OpenLogic OpenJDK 11](https://www.openlogic.com/openjdk-downloads?field_java_parent_version_target_id=189&field_operating_system_target_id=198&field_architecture_target_id=185&field_java_package_target_id=188) 执行构建为例，过程如下。

下载 [openlogic-openjdk-11.0.31+11-linux-x64.tar.gz](https://builds.openlogic.com/downloadJDK/openlogic-openjdk/11.0.31+11/openlogic-openjdk-11.0.31+11-linux-x64.tar.gz)，改名为 `openlogic-openjdk-11.0.31-linux-x64.tar.gz` 后（去掉 `+11`，否则在 TeamCity 中作为参数引用时会找不到），上传至 TeamCity：

![Upload Custom Archive](https://alphahinex.github.io/contents/teamcity-agent-with-custom-jdk/install-custom-archive.png)

上传的工具文件包会被存储到 TeamCity Server 的 [\<TeamCity Data Directory>](https://www.jetbrains.com/help/teamcity/teamcity-data-directory.html)`/plugins/.tools` 目录下。

Agent 会在第一个需要该工具的构建执行时，从 TeamCity Server 下载并解压工具包，保存到 [\<Agent Home Directory>](https://www.jetbrains.com/help/teamcity/agent-home-directory.html)`/tools` 下，避免后续构建重复下载。

在构建中引用此工具时，可通过 `%teamcity.tool.<installed_tool_ID>%` 获得解压工具包的路径。

上面上传的 `openlogic-openjdk-11.0.31-linux-x64.tar.gz` 在本例环境中被保存到了 Agent 的 `/opt/buildagent/tools/openlogic-openjdk-11.0.31-linux-x64` 目录下，因为 `openlogic-openjdk-11.0.31-linux-x64.tar.gz` 包中还有一层 `openlogic-openjdk-11.0.31+11-linux-x64` 目录，所以在构建中引用时，需要将 `JDK home path` 设置为 `%teamcity.tool.openlogic-openjdk-11.0.31-linux-x64%/openlogic-openjdk-11.0.31+11-linux-x64/bin`：

![Custom JDK Home Path](https://alphahinex.github.io/contents/teamcity-agent-with-custom-jdk/custom-jdk-home-path.png)

之后便可通过任意 Agent 使用自定义 JDK 版本执行构建了：

```log
03:01:02 Step 1/1: Maven
03:01:02   Initial M2_HOME not set
03:01:02   Current M2_HOME = /opt/buildagent/tools/maven.3.9.8
03:01:02   PATH = /opt/buildagent/tools/maven.3.9.8/bin:/opt/java/openjdk/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
03:01:02   Using watcher: /opt/buildagent/plugins/mavenPlugin/maven-watcher-jdk17/maven-watcher-agent.jar
03:01:02   Using agent local repository at /opt/buildagent/system/jetbrains.maven.runner/maven.repo.local
03:01:02   *** Start reading the project structure ***
03:01:04   Initial MAVEN_OPTS not set
03:01:04   Current MAVEN_OPTS not set
03:01:04   Starting: /opt/buildagent/tools/openlogic-openjdk-11.0.31-linux-x64/openlogic-openjdk-11.0.31+11-linux-x64/bin/java -Dagent.home.dir=/opt/buildagent ... -Dteamcity.version=2026.1.1 (build 222577) -Dmaven.repo.local=/opt/buildagent/system/jetbrains.maven.runner/maven.repo.local -classpath /opt/buildagent/tools/maven.3.9.8/boot/plexus-classworlds-2.8.0.jar: org.codehaus.plexus.classworlds.launcher.Launcher -f /opt/buildagent/work/c36b823fddd68df3/pom.xml -B -Dmaven.test.failure.ignore=true clean test
03:01:04   in directory: /opt/buildagent/work/c36b823fddd68df3
03:01:05   [INFO] Scanning for projects...
```

## 使用自定义 Node 执行构建

截至 `2026.1`，TeamCity 中 [Node.js 的构建步骤只能在 Docker/Podman 容器中运行](https://www.jetbrains.com/help/teamcity/2026.1/nodejs.html#Prerequisites)。

此外，也可通过上述安装自定义工具的方式，在 Agent 中安装指定 Node.js 版本执行构建。

以 [Node.js v24.x (Krypton)](https://nodejs.org/en/download/archive/v24.19.0) 为例，下载 [node-v24.19.0-linux-x64.tar.xz](https://nodejs.org/dist/v24.19.0/node-v24.19.0-linux-x64.tar.xz)。

因上传的工具包格式不支持 `.xz`，先将其解压成 `.tar` 格式：

```bash
$ xz -dk node-v24.19.0-linux-x64.tar.xz
$ ls node-v24.19.0-linux-x64*
node-v24.19.0-linux-x64.tar    node-v24.19.0-linux-x64.tar.xz
```

上传 `node-v24.19.0-linux-x64.tar` 至 TeamCity 后，在构建配置中创建一个命令行构建步骤，并对工具进行引用：

![Command Line](https://alphahinex.github.io/contents/teamcity-agent-with-custom-jdk/command-line.png)

`Custom script` 中填入如下内容，期望可以在构建日志中看到 node 和 npm 的版本：

```bash
cd %teamcity.tool.node-v24.19.0-linux-x64%/node-v24.19.0-linux-x64
export PATH=$(pwd)/bin:$PATH
node -v
npm -v
```

不出意外的话，意外出现了：

```log
06:12:42 Step 2/2: build (1) (Command Line)
06:12:42   Starting: /opt/buildagent/temp/agentTmp/custom_script10766528399743084674
06:12:42   in directory: /opt/buildagent/work/860d69c611cfece6
06:12:42   v24.19.0
06:12:42   node:internal/modules/cjs/loader:1520
06:12:42     throw err;
06:12:42     ^
06:12:42   
06:12:42   Error: Cannot find module '../lib/cli.js'
06:12:42   Require stack:
06:12:42   - /opt/buildagent/tools/node-v24.19.0-linux-x64/node-v24.19.0-linux-x64/bin/npm
06:12:42       at Module._resolveFilename (node:internal/modules/cjs/loader:1517:15)
06:12:42       at wrapResolveFilename (node:internal/modules/cjs/loader:1071:27)
06:12:42       at defaultResolveImplForCJSLoading (node:internal/modules/cjs/loader:1095:10)
06:12:42       at resolveForCJSWithHooks (node:internal/modules/cjs/loader:1122:12)
06:12:42       at Module._load (node:internal/modules/cjs/loader:1294:5)
06:12:42       at wrapModuleLoad (node:internal/modules/cjs/loader:255:19)
06:12:42       at Module.require (node:internal/modules/cjs/loader:1617:12)
06:12:42       at require (node:internal/modules/helpers:153:16)
06:12:42       at Object.<anonymous> (/opt/buildagent/tools/node-v24.19.0-linux-x64/node-v24.19.0-linux-x64/bin/npm:2:1)
06:12:42       at Module._compile (node:internal/modules/cjs/loader:1872:14) {
06:12:42     code: 'MODULE_NOT_FOUND',
06:12:42     requireStack: [
06:12:42       '/opt/buildagent/tools/node-v24.19.0-linux-x64/node-v24.19.0-linux-x64/bin/npm'
06:12:42     ]
06:12:42   }
06:12:42   
06:12:42   Node.js v24.19.0
06:12:42   Process exited with code 1
06:12:19   Process exited with code 1 (Step: build (1) (Command Line))
06:12:42   Step build (1) (Command Line) failed
```

日志中可以看到 node 版本输出正确，但 npm 却报错找不到模块 `../lib/cli.js`，这是因为 `bin` 路径下的软链接在 TeamCity Agent 解压时被破坏了，导致 npm 无法找到其依赖的模块。

正确的软联接：

```bash
$  tree -L 2
.
├── CHANGELOG.md
├── LICENSE
├── README.md
├── bin
│   ├── corepack -> ../lib/node_modules/corepack/dist/corepack.js
│   ├── node
│   ├── npm -> ../lib/node_modules/npm/bin/npm-cli.js
│   └── npx -> ../lib/node_modules/npm/bin/npx-cli.js
├── include
│   └── node
├── lib
│   └── node_modules
└── share
    ├── doc
    └── man

8 directories, 7 files
```

TeamCity Agent 解压后，`bin` 目录下的软链接被破坏了：

```bash
$ ls -alh
total 121M
drwxr-xr-x 2 buildagent buildagent   56 Aug  9 07:12 .
drwxr-xr-x 6 buildagent buildagent  108 Aug  9 07:12 ..
-rwxr--r-- 1 buildagent buildagent  174 Aug  9 06:59 corepack
-rwxr--r-- 1 buildagent buildagent 121M Aug  9 06:59 node
-rwxr--r-- 1 buildagent buildagent   54 Aug  9 06:59 npm
-rwxr--r-- 1 buildagent buildagent 2.9K Aug  9 06:59 npx
```

可在构建步骤执行的脚本中，重新设置软链接，即可正常构建：

```bash
cd %teamcity.tool.node-v24.19.0-linux-x64%/node-v24.19.0-linux-x64
export PATH=$(pwd)/bin:$PATH
ln -sf $(pwd)/lib/node_modules/npm/bin/npm-cli.js $(pwd)/bin/npm
node -v
npm -v
cd %teamcity.build.checkoutDir%
npm is
```

![Custom script](https://alphahinex.github.io/contents/teamcity-agent-with-custom-jdk/custom-script.png)
