---
id: linux-rsync
title: "【转】linux大量文件的复制转移好工具之rsync——支持断点续传校验文件完整性"
description: "断点续传时，rsync 会在目标目录下生成一个隐藏的临时文件，以便在传输中断后可以继续传输"
date: 2025.04.13 10:26
categories:
    - Linux
tags: [Linux]
keywords: Linux, rsync, 断点续传, screen, nohup
cover: /contents/covers/rsync.jpg
---

原文地址：https://www.pfjsb.com/kfyw/linux-rsync.html

对于海量文件的稳定复制，推荐使用 `rsync`，因为它支持断点续传、校验文件完整性，并能显示进度。

# 推荐方法：使用 `rsync` 进行稳定复制

```bash
rsync -avh --progress --stats /源目录/ /目标磁盘/目标目录/
```

## 参数解释

- `-a`：归档模式，保持文件的权限、时间戳、符号链接等属性。
- `-v`：显示详细信息（可选）。
- `-h`：人类可读格式（文件大小等）。
- `--progress`：显示复制进度。
- `--stats`：显示最终的统计信息。

## 示例

如果你的源目录是 `/mnt/images/`，目标磁盘是 `/mnt2/backup/`，执行：

```bash
rsync -avh --progress --stats /mnt/images/ /mnt2/backup/
```

这样会把 `/mnt/images/` 整个复制到 `/mnt2/backup/` 目录下。

# 提高复制速度（适用于海量小文件）

## 方法 1：使用 `rsync --info=progress2`（实时进度 + 断点续传）

```bash
rsync -avh --info=progress2 /mnt/images/ /mnt2/backup/
```

- `--info=progress2`：显示整体进度（比 `--progress` 更友好）。
- `rsync` 断点续传，不会重复复制已经存在的文件。

## 方法 2：使用 `rsync --bwlimit` 限制带宽（防止服务器负载过高）

如果你要在生产环境下复制，避免影响业务，可以限制带宽：

```bash
rsync -avh --info=progress2 --bwlimit=100000 /mnt/images/ /mnt2/backup/
```

- `--bwlimit=100000` 限制速度为 100MB/s，你可以根据情况调整。

## 方法 3：使用 `rsync --remove-source-files`（删除已复制的文件，适用于迁移）

如果你想复制完后删除源文件，释放磁盘空间：

```bash
rsync -avh --progress --remove-source-files /mnt/images/ /mnt2/backup/
find /mnt/images/ -type f -empty -delete
```

- `--remove-source-files`：复制成功后删除已复制的文件（但不删除空目录）。
- `find ... -delete`：清理空目录。

> ⚠ 注意：如果你要彻底删除源目录，最后用：
> ```bash
> rm -rf /mnt/images/
> ```

# 其他方法

## 使用 `cp`（不推荐）

```bash
cp -a /mnt/images/ /mnt2/backup/
```

- `cp -a` 可以保持文件属性。

缺点：
- 不支持断点续传，失败后需要重新开始。
- 复制大文件时效率较低，无法显示进度。

# 总结

✅ 推荐

```bash
rsync -avh --info=progress2 /mnt/images/ /mnt2/backup/
```

（稳定、高效、可断点续传）

✅ 限速

```bash
rsync --bwlimit=100000
```

（避免服务器过载）

✅ 迁移

```bash
rsync --remove-source-files
```

（复制完后删除源文件）

❌ 不要用

```bash
cp -a
```

（不稳定，大数据复制容易失败）

# 使用rsync -avh --info=progress2命令中断后，该如何接着上次继续？

`rsync` 默认支持断点续传，如果命令执行中断，你可以直接重新运行相同的 `rsync` 命令，它会自动跳过已完成的文件，仅复制未完成或新变化的文件。

# 💡 继续上次的 `rsync` 复制

假设你之前运行的命令是：

```bash
rsync -avh --info=progress2 /mnt/images/ /mnt2/backup/
```

如果中断了，直接运行 同样的命令：

```bash
rsync -avh --info=progress2 /mnt/images/ /mnt2/backup/
```

✅ 它会自动跳过已复制的文件，只同步未完成的文件。

# 🛠 进阶优化（适用于大文件）

如果你复制的文件特别大，可以加上 `--partial` 和 `--append-verify` 参数：

```bash
rsync -avh --info=progress2 --partial --append-verify /mnt/images/ /mnt2/backup/
```

- `--partial`：保留部分已复制的文件，避免重新复制。
- `--append-verify`：对大文件进行增量复制，确保完整性（比 `--append` 更安全）。

🔹 适用于大文件（如 1GB+ 视频、ISO、数据库备份等）。

# 🎯 让 `rsync` 在后台运行（防止 SSH 断连）

如果你的 SSH 连接容易断开，建议用 `screen` 或 `nohup` 让 `rsync` 在后台运行：

## 方法 1：使用 `screen`（推荐）

```bash
screen -S rsync_copy
rsync -avh --info=progress2 /mnt/images/ /mnt2/backup/
```

📌 SSH 断开后，`screen -r rsync_copy` 可恢复进程。

## 方法 2：使用 `nohup`（简单）

```bash
nohup rsync -avh --info=progress2 /mnt/images/ /mnt2/backup/ > rsync.log 2>&1 &
```

📌 SSH 断开后任务仍在运行，可查看 `rsync.log` 进度：

```bash
tail -f rsync.log
```

# 🚀 总结

- 直接重新运行 `rsync`，会自动跳过已完成的文件：

```bash
rsync -avh --info=progress2 /mnt/images/ /mnt2/backup/
```

- 对于大文件，使用 `--partial --append-verify` 防止重新复制：

```bash
rsync -avh --info=progress2 --partial --append-verify /mnt/images/ /mnt2/backup/
```

- 使用 `screen` 或 `nohup`，防止 SSH 断连导致中断：

```bash
screen -S rsync_copy
rsync -avh --info=progress2 /mnt/images/ /mnt2/backup/
```

SSH 断开后，输入

```bash
screen -r rsync_copy
```

恢复任务。

这样，即使 `rsync` 复制任务被中断，你也可以无缝续传，确保数据完整性！🚀
