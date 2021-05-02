---
id: reclaim-policy
title: "K8s 存储资源回收策略"
description: "数据不丢失，了解一下？"
date: 2021.05.02 10:34
categories:
    - Cloud Native
tags: [K8s]
keywords: PersistentVolume, PersistentVolumeClaim, StorageClass, pv, pvc, sc, K8s, Cloud Native
cover: /contents/covers/reclaim-policy.jpeg
---

在 [Volume、PersistentVolume、PersistentVolumeClaim 和 StorageClass](https://alphahinex.github.io/2021/04/18/v-pv-pvc-sc/) 中，我们介绍了 K8s 存储资源的相关概念。持久卷（PersistentVolume）通过卷插件对位于外部基础设施中的存储资产进行操作，并可通过 `回收策略`，控制持久卷回收时会对外部存储数据产生的影响。

## 回收策略

目前支持的回收策略有三种：

1. `Retain`：手动创建的 PV 所使用的默认回收策略。此策略使得用户可以手动回收资源，当使用 PV 的对象被删除时，PV 仍然存在，对应的数据卷状态变为已释放（Released）。
1. `Delete`：动态供应的 PV 默认为删除策略，对于支持 Delete 回收策略的卷插件，删除动作会将 PersistentVolume 对象从 Kubernetes 中移除，同时也会从外部基础设施（如 AWS EBS、GCE PD、Azure Disk 或 Cinder 卷）中移除所关联的存储资产。
1. `Recycle`： 已弃用，且需要 PV 所使用的卷插件支持。

**所以对于重要的数据，一定要使用 `Retain` 的回收策略，以免部署或 PVC 删除的时候，因 `Delete` 回收策略而使重要数据丢失。**

在使用 `Retain` 策略时，可以通过下面的步骤来手动回收该卷：

1. 删除 PersistentVolume 对象。与之相关的、位于外部基础设施中的存储资产（例如 AWS EBS、GCE PD、Azure Disk 或 Cinder 卷）在 PV 删除之后仍然存在。
2. 根据情况，手动清除所关联的存储资产上的数据。
3. 手动删除所关联的存储资产；如果你希望重用该存储资产，可以基于存储资产的定义创建新的 PersistentVolume 卷对象。

## 持久卷设定回收策略

对 PV 可使用 `persistentVolumeReclaimPolicy` 设置回收策略：

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv0003
spec:
  capacity:
    storage: 5Gi
  volumeMode: Filesystem
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: slow
  mountOptions:
    - hard
    - nfsvers=4.1
  nfs:
    path: /tmp
    server: 172.17.0.2
```

## 存储类设定回收策略

对 SC 可使用 `reclaimPolicy` 进行设置：

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: standard
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp2
reclaimPolicy: Retain
allowVolumeExpansion: true
mountOptions:
  - debug
volumeBindingMode: Immediate
```

## 更改 PV 的回收策略

StorageClass 一旦创建了就不能再更新，如果需要修改已有的默认存储类，可参照 [改变默认 StorageClass][change] 中步骤执行。

PV 的 `persistentVolumeReclaimPolicy` 属性可以通过下面方式进行更改：

```bash
$ kubectl patch pv <your-pv-name> -p '{"spec":{"persistentVolumeReclaimPolicy":"Retain"}}'
```

## 重新绑定 Retain 的 PV

PVC 与 PV 之间会建立绑定关系，这种绑定是一种一对一的映射，一旦绑定关系建立，则 PersistentVolumeClaim 绑定就是排他性的，无论该 PVC 申领是如何与 PV 卷建立的绑定关系。实现上使用 `.spec.claimRef` 来表示 PV 卷 与 PVC 申领间的双向绑定关系。

使用 `Retain` 策略的 PV 在 PVC 被删除之后，会处于 `Released` 的状态。此时无法使用新的 PVC 与此 PV 进行绑定。需先将该 PV 与之前 PVC 的绑定关系解除，才能重新进行绑定。

解除绑定时，可以编辑 PV 的信息，删除 `.spec.claimRef` 这段内容。删除之后，PV 的状态会变更为 `Available` 状态，此时即可使用与之前相同存储需求的 PVC 或者通过 selector 选择此 PV 进行重新绑定。

## 参考资料

* [kubernetes pvc重绑Retain策略pv](https://blog.csdn.net/networken/article/details/108304998)

[change]:https://kubernetes.io/zh/docs/tasks/administer-cluster/change-default-storage-class/