---
id: kubesphere34-s2i-cert-expired
title: "《kubesphere3.4 S2i证书过期修复记录》增强版"
description: "https://github.com/openksc"
date: 2026.11.15 10:34
categories:
    - K8s
tags: [KubeSphere, Kubernetes]
keywords: KubeSphere, s2i, x509, certificate, expired, openssl, ks-installer, base64, s2ioperator, kubesphere-devops-system, caBundle, tls.crt, tls.key
cover: /contents/covers/kubesphere34-s2i-cert-expired.png
---

本文基于 [kubesphere3.4 S2i证书过期修复记录](https://www.jianshu.com/p/a573e9893577) 内容，对部分内容进行了调整、优化及补充。

## 现象

![](https://alphahinex.github.io/contents/covers/kubesphere34-s2i-cert-expired.png)

报错信息：

```err
InternalError
Internal error occurred: failed calling webhook "s2ibuilder.kb.io": failed to call webhook: Post "https://webhook-server-service.kubesphere-devops-system.svc:443/mutate-devops-kubesphere-io-v1alpha1-s2ibuilder?timeout=10s": x509: certificate has expired or is not yet valid: current time 2026-11-09T07:47:34Z is after 2024-02-14T06:08:48Z
```

KubeSphere 版本 `v3.4.0`

## 罪魁祸首

[ks-installer/roles/ks-devops/files/ks-devops/charts/ks-devops-0.2.2.tgz](https://github.com/kubesphere/ks-installer/blob/release-3.4/roles/ks-devops/files/ks-devops/charts/ks-devops-0.2.2.tgz) 导致

> https://github.com/openksc/ks-installer/tree/v3.4.1/roles/ks-devops/files/ks-devops/charts

devops 组件由 ks-installer 通过 helm 的方式进行安装

```yaml
- name: ks-devops | Upgrading or installing ks-devops
  args:
    executable: /bin/bash
  shell: |
    # Delete Job migrate because 'helm upgrade' will try to update immutable fields of Job, which is not allowed.
    {{ bin_dir }}/kubectl delete job -n kubesphere-devops-system migrate --ignore-not-found

    ks_devops_chart_version=0.2.2
    charts_folder={{ kubesphere_dir }}/ks-devops/charts
    ks_devops_chart=$charts_folder/ks-devops-$ks_devops_chart_version.tgz

    # Create or update CRDs manually
    tar xzvf $ks_devops_chart -C $charts_folder
    {{ bin_dir }}/kubectl apply -f $charts_folder/ks-devops/crds
    {{ bin_dir }}/kubectl apply -f $charts_folder/ks-devops/charts/s2i/crds

    # Waiting for CRD to complete the upgrade
    sleep 10

    # Import the templates seperately due the potential webhook issues
    rm -rf s2i-templates
    helm template  $charts_folder/ks-devops/charts/s2i/ \
      -f {{ kubesphere_dir }}/ks-devops/ks-devops-values.yaml \
      -s templates/binary.yaml \
      -s templates/java.yaml \
      -s templates/nodejs.yaml \
      -s templates/python.yaml \
      -s templates/tomcat.yaml > s2i-templates\templates.yaml
    rm -rf $charts_folder/ks-devops/charts/s2i/templates/binary.yaml
    rm -rf $charts_folder/ks-devops/charts/s2i/templates/java.yaml
    rm -rf $charts_folder/ks-devops/charts/s2i/templates/nodejs.yaml
    rm -rf $charts_folder/ks-devops/charts/s2i/templates/python.yaml
    rm -rf $charts_folder/ks-devops/charts/s2i/templates/tomcat.yaml

    {{ bin_dir }}/helm upgrade --install devops $ks_devops_chart \
    -n kubesphere-devops-system \
    -f {{ kubesphere_dir }}/ks-devops/ks-devops-values.yaml --wait

    {{ bin_dir }}/kubectl apply -f s2i-templates\templates.yaml
  register: devops_upgrade_result
  until: devops_upgrade_result is succeeded
  retries: 3
  delay: 10
```

通过拆解分析我们了解 ca 相关证书内容，在 chart values.yaml 进行定义 `ks-devops-0.2.2/ks-devops/charts/s2i/values.yaml`

即以下内容：

```yaml
s2ioperator:
  image:
    name: "s2ioperator"
    tag: "v3.2.1"
  secret:
    caBundle: |
      -----BEGIN CERTIFICATE-----
      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
      jF9FR0nTiGgtyJkHubjKMd8YBu9S9q0HgGOm
      -----END CERTIFICATE-----
    key: |
      -----BEGIN RSA PRIVATE KEY-----
      MIIEowIBAAKCAQEAx78d2JIYf0EXTO4fN3VHqJiQUlnmYMVcGgoIK/TeHI0irrCK
      N1wnTfxPNEE4/W0yvLARKpF+hzf3r3VWr0Ab7pKr8UEAYtTXRz0YdwL/Ek4XBCX0
      7/nGaPM/lRgg8UW05aeSg+VrMSVxt53hiIPMY3+JdM9tEI6DJbLsa2ECNQ/VU9Uh
      KXd8YUTxEcKDkBWnqTiihVTk0RafAvIUcIIwu7+mz0+tlN/YHMxfvK+pkJaeA92H
      OnTifMGQ+YbpV8YwUpYfi71MJbuo5AAWuDl0GfoiawkIUzT2Hl7BDCrHnnZ5p7La
      tLcDEqHANGRBlN1G6oxFVTtQdVtA3m53i/3Y+QIDAQABAoIBAEF5SeU1bkY4JdUX
      sK/TB5wh9hyoTzWlO51lcGxIJY4iTR4JzCR9VnzfmW69elrHsnvbEqVrb5gPJmcj
      BTkIwJ8hAK9h6Sh8L9ywEBbiqo1rf2virTkEHJ9GLK9Ia3Pqr3MfzIzjZJGFfpL7
      c3P2D8cFhR7+5vcoX6C513kTIVAWvWB5+LhTLqIH0zBNVY4L8Y7F9TngEMWFuQnZ
      xCesFTzBZfaCtT42IQ3wjJVPTpFfl2+HNdMWctVwvTeEgUEEsn5dttCP0A5859gA
      vzokoTHsGBKX5ixcSbCiwqeS9/zaNitn4wUT6WyCOmaN2dIz9XarDoHntqRocwHs
      kAQBxgkCgYEA/NiCXonkmdKbt2Ji/vq8UgeoJ/mnasOHy250s1WxOwbiPvxogbke
      cMGO/ygUnYW32ixeyfPlsHPKY/W43+crf/NEr0cWiRTM5PxZQvapiFI2fIytsbe7
      jG44JPykvtp4qeiKqSn1Le10CsWmLYrqoLwZUUcUfMn0AdIoqiPxSE8CgYEAyj0H
      en+W/zDwzs/ypXUt3bzudK848fFC3HOKrbav6keyr8eM0eX2wLV6yoADtAQHJ2H2
      XpR4GfC1LALCa6pCUZJ8rtpMCvIUg6NJ+rzeXcV1+Sju9NZo94M+C/sOAwwullv1
      qRrw8j3NmX1r0q+GTd6NNEzO8deBwa1Y6vo/sDcCgYEAtG0Tar7ff9zH/W6Z0fW+
      WJLaLdx62Ta6OjKR2D73/3UEEYowURF2ZWPZ1L4XJ+j5rxgmc9o1N1sJO5dm22+s
      nNtNUf5aWGudYnGoiJ5Xj82K0AnbEIxZqvYj3lDihsaDgEtOVzR3ntRpEB7GXI1a
      rGRNdLBSMFI0avA60F5hmQUCgYBjvP9wMXaFelx4kmOnqAerwJ6VW0kpQQPpdu4g
      x+UwFJYSTMatSc2MsrPRJJsu74GbsZtwf6ZPnL+s6dt6f6hfVHA7R5uTFlp5pVE5
      4GWGN3j8HWzjwM5Zqxcxj2oUpLBhJQ8djBTiUwqPtSQ07q28v5JCBdNVwCPVIaml
      kS9RtwKBgBZ39A7HvuOHtIpA2cH15vO5fvVw5HHDnWf7kwQJAv8sUYwiljgx/9/G
      PZhijwPnuTbBCLZ8YkHGqtUaT1Dv81dhcw44RY7ykBpUXM2lFEoWyOGqSlpYyKeV
      ZE90IxqhGtCsj6YegHyxLzse2gdFN1a2hFirkqWG8/m7HJfh96Fz
      -----END RSA PRIVATE KEY-----
    certificate: |
      -----BEGIN CERTIFICATE-----
      MIIE0TCCArmgAwIBAgIJAOoJB0y3z6bMMA0GCSqGSIb3DQEBCwUAMFoxCzAJBgNV
      BAYTAkFVMRMwEQYDVQQIDApTb21lLVN0YXRlMSEwHwYDVQQKDBhJbnRlcm5ldCBX
      aWRnaXRzIFB0eSBMdGQxEzARBgNVBAMMCktVQkVTUEhFUkUwHhcNMjEwNDI2MDYx
      MjU1WhcNMzEwNDI0MDYxMjU1WjAhMR8wHQYDVQQDDBZ3ZWJob29rLXNlcnZlci1z
      ZXJ2aWNlMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAx78d2JIYf0EX
      TO4fN3VHqJiQUlnmYMVcGgoIK/TeHI0irrCKN1wnTfxPNEE4/W0yvLARKpF+hzf3
      r3VWr0Ab7pKr8UEAYtTXRz0YdwL/Ek4XBCX07/nGaPM/lRgg8UW05aeSg+VrMSVx
      t53hiIPMY3+JdM9tEI6DJbLsa2ECNQ/VU9UhKXd8YUTxEcKDkBWnqTiihVTk0Raf
      AvIUcIIwu7+mz0+tlN/YHMxfvK+pkJaeA92HOnTifMGQ+YbpV8YwUpYfi71MJbuo
      5AAWuDl0GfoiawkIUzT2Hl7BDCrHnnZ5p7LatLcDEqHANGRBlN1G6oxFVTtQdVtA
      3m53i/3Y+QIDAQABo4HSMIHPMIHMBgNVHREEgcQwgcGCFndlYmhvb2stc2VydmVy
      LXNlcnZpY2WCL3dlYmhvb2stc2VydmVyLXNlcnZpY2Uua3ViZXNwaGVyZS1kZXZv
      cHMtc3lzdGVtgjN3ZWJob29rLXNlcnZlci1zZXJ2aWNlLmt1YmVzcGhlcmUtZGV2
      b3BzLXN5c3RlbS5zdmOCQXdlYmhvb2stc2VydmVyLXNlcnZpY2Uua3ViZXNwaGVy
      ZS1kZXZvcHMtc3lzdGVtLnN2Yy5jbHVzdGVyLmxvY2FsMA0GCSqGSIb3DQEBCwUA
      A4ICAQAG9tdFrUxR02kgd/qSG/p+sRQDOYpG5qqZgERhxXE32Gb4o7rJbtZ2Zvcb
      SWiF1PP4QnMevycXD1dYsCSdVzGFsDA0fcyuF1sKc32ljhfTTDmymzmEJQNYXPx2
      rzqf9u+483n/+gFgLDexukXKJ5+p9gzXLePSZwE+HEgZdNplS5kfMR+Uvpo+eMhc
      6yn5aBJWLsgvKTx7Gar27PdM297vhpPFcxSbDykHJNDw2U+uxwwIR5SM1PmWhuoj
      oz1UO3xeLKPPluUH/gJKGRt7rv3WDVR1u0yFFFGLumd2SAKjayTROq9nRzONjeGH
      JeC7drnKcnvunaZW27NiCzfhaq0neXhaGEOpcdaYBVs0MZfnb2uaAQFy0P3HZ6UI
      QISOpQ/6Prv6dgheU0hHsbjhHX8Y1Z/EpNs6nS6i2UCde+RaEgK1xxnLtBL7r76d
      EBvpC49ChRZ0r7U6m8LJ6yjbLTMEPVqODcxZKn9aoXI1TCNgzW7QUv5b5qMB2oOp
      q1lPSxxEQboelsczSxWK6U4uwcyGuVNymBgfPNuc7wwcPBLbuahUo6YtFNky2OKz
      p2hvkjDixDbGS3Svi45eEpBnIrcma+fanPKJCYUZbiRIoD+kA8Ss5mZgtah3LcrQ
      U8UUR60N6LJ52m2ik/zHh+p31ihhCz7F7JWq7itNpbjFcb9T6g==
      -----END CERTIFICATE-----
```

通过 openssl 进行解析，我们发现 ca 根证书过期时间为 2024-02-14

```bash
$ openssl x509 -in ca.crt -text
Certificate:
    Data:
        Version: 3 (0x2)
        Serial Number:
            96:f1:e6:1b:01:8b:76:5d
        Signature Algorithm: sha256WithRSAEncryption
        Issuer: C = AU, ST = Some-State, O = Internet Widgits Pty Ltd, CN = KUBESPHERE
        Validity
            Not Before: Apr 26 06:08:48 2021 GMT
            Not After : Feb 14 06:08:48 2024 GMT
... ...
```

## 解决方案

替换证书、并同步替换 MutatingWebhookConfiguration、ValidatingWebhookConfiguration 内的 ca 证书内容即可解决。

具体流程如下：

> 可以直接使用下面 yaml 内容，其中证书的到期日期为 2051 年 7 月 7 日。如需自行生成证书并替换 yaml 中内容，可参考下面 `证书生成方式` 章节。

```bash
$ echo "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURjekNDQWx1Z0F3SUJBZ0lVT0lyK2FFaFhyVEI3Z01UK1RZTFRjMS9rdkowd0RRWUpLb1pJaHZjTkFRRUwKQlFBd1NERUxNQWtHQTFVRUJoTUNRMDR4Q3pBSkJnTlZCQWdNQWtoQ01Rc3dDUVlEVlFRS0RBSlJRekVmTUIwRwpBMVVFQXd3V2QyVmlhRzl2YXkxelpYSjJaWEl0YzJWeWRtbGpaVEFnRncweU5EQXlNVGt3TlRReU1qZGFHQTh5Ck1EVXhNRGN3TnpBMU5ESXlOMW93U0RFTE1Ba0dBMVVFQmhNQ1EwNHhDekFKQmdOVkJBZ01Ba2hDTVFzd0NRWUQKVlFRS0RBSlJRekVmTUIwR0ExVUVBd3dXZDJWaWFHOXZheTF6WlhKMlpYSXRjMlZ5ZG1salpUQ0NBU0l3RFFZSgpLb1pJaHZjTkFRRUJCUUFEZ2dFUEFEQ0NBUW9DZ2dFQkFLRkVpSk9NZlF6ZnJwRE1aOHNNMmxoaFZUVnVGOFU5CjJTYXFCYTNUSU1rc0gvZmlwai8rVjZmaUhLYnh4ZGlrclIxaFZJajFrMkt0aVJRL1ZPbG1pSHdGakVyYUNtNGUKMGhsdzl5Mmt0akF0bzlXYlRaQVV0SFJhK0Q2TUlmajNjUG9QVnV0ZjYyRklYZTNNYmJSaU1SWjNEN2c2RE52SQplUGcydjJyQjZva3g0MDM0L0gxdkk2dTNGaHkvNXRQeklGYmFxU1Z1bHhZck5CUUV1MGhzanVKZVhtK0drWnlTClVuSkpMUkcza1p3Wk1CTitGWDlhRzdvMkJrdVVXT3doMnhUeGp6TFppSEJobUJHbnU1WEVKR0J1a2xaT0tIeE0KQ0lPSGtNVWo4VllIcU5RV3VLaFRvcncraFl1UU9aU2VMaGE1ZFRZczRkdlU1cTdJMjA4VXJBRUNBd0VBQWFOVApNRkV3SFFZRFZSME9CQllFRkRSVXRvYWRlUnYvYWYxamtJT0hXU3dNT3ppVk1COEdBMVVkSXdRWU1CYUFGRFJVCnRvYWRlUnYvYWYxamtJT0hXU3dNT3ppVk1BOEdBMVVkRXdFQi93UUZNQU1CQWY4d0RRWUpLb1pJaHZjTkFRRUwKQlFBRGdnRUJBRnByajJrZFRoQk93bEtiQ1VNNVpMTDBzbi8rSmI2WXZtSXRFNkpiemRUc3RyaTdsWHk2NlJPNwpTaHF2aURrQVhUYTVWWTc1UFdWNjRMRXlJTW9JYyt2NkdXVSsveWtGTnZTMHJCbm9yczlzdDFyMFllRXhHM0pyCnhHNFhzUzJIbmJ5Yk5oelg3Q3pWRnFGYWh2WEJ0SkZoTGY1TVVUTkFWem0reTgxTlZBcG83bWNmL3ZZKzlmcSsKYjNpVTYvQTluby9JSlZYbWt6V1o2SUQvb0pxQTE1Y0hJaVYrZ05pbDE1dEZKVUtRTkVuMlZWVisveFo3VXJmWgpMTWhtRmZFTGdPUnIvei8vNUx1bXlCeFdOelFCUWhRbVJNSlgzM2IrR1lBbFYvTS85cEZLMHV0NGtaMjZVbkdjCk5TSFJ0VHdseldXNTk4SU40QmUxTjNDU0tEZWwvNGc9Ci0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0K" | base64 -d > output.crt
$ openssl x509 -in output.crt -text
Certificate:
    Data:
        Version: 3 (0x2)
        Serial Number:
            38:8a:fe:68:48:57:ad:30:7b:80:c4:fe:4d:82:d3:73:5f:e4:bc:9d
        Signature Algorithm: sha256WithRSAEncryption
        Issuer: C = CN, ST = HB, O = QC, CN = webhook-server-service
        Validity
            Not Before: Feb 19 05:42:27 2024 GMT
            Not After : Jul  7 05:42:27 2051 GMT
...
```

### 1. 替换 secret

保存 `s2i-webhook-server-cert.yaml`：

```yaml
apiVersion: v1
data:
  caBundle: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURjekNDQWx1Z0F3SUJBZ0lVT0lyK2FFaFhyVEI3Z01UK1RZTFRjMS9rdkowd0RRWUpLb1pJaHZjTkFRRUwKQlFBd1NERUxNQWtHQTFVRUJoTUNRMDR4Q3pBSkJnTlZCQWdNQWtoQ01Rc3dDUVlEVlFRS0RBSlJRekVmTUIwRwpBMVVFQXd3V2QyVmlhRzl2YXkxelpYSjJaWEl0YzJWeWRtbGpaVEFnRncweU5EQXlNVGt3TlRReU1qZGFHQTh5Ck1EVXhNRGN3TnpBMU5ESXlOMW93U0RFTE1Ba0dBMVVFQmhNQ1EwNHhDekFKQmdOVkJBZ01Ba2hDTVFzd0NRWUQKVlFRS0RBSlJRekVmTUIwR0ExVUVBd3dXZDJWaWFHOXZheTF6WlhKMlpYSXRjMlZ5ZG1salpUQ0NBU0l3RFFZSgpLb1pJaHZjTkFRRUJCUUFEZ2dFUEFEQ0NBUW9DZ2dFQkFLRkVpSk9NZlF6ZnJwRE1aOHNNMmxoaFZUVnVGOFU5CjJTYXFCYTNUSU1rc0gvZmlwai8rVjZmaUhLYnh4ZGlrclIxaFZJajFrMkt0aVJRL1ZPbG1pSHdGakVyYUNtNGUKMGhsdzl5Mmt0akF0bzlXYlRaQVV0SFJhK0Q2TUlmajNjUG9QVnV0ZjYyRklYZTNNYmJSaU1SWjNEN2c2RE52SQplUGcydjJyQjZva3g0MDM0L0gxdkk2dTNGaHkvNXRQeklGYmFxU1Z1bHhZck5CUUV1MGhzanVKZVhtK0drWnlTClVuSkpMUkcza1p3Wk1CTitGWDlhRzdvMkJrdVVXT3doMnhUeGp6TFppSEJobUJHbnU1WEVKR0J1a2xaT0tIeE0KQ0lPSGtNVWo4VllIcU5RV3VLaFRvcncraFl1UU9aU2VMaGE1ZFRZczRkdlU1cTdJMjA4VXJBRUNBd0VBQWFOVApNRkV3SFFZRFZSME9CQllFRkRSVXRvYWRlUnYvYWYxamtJT0hXU3dNT3ppVk1COEdBMVVkSXdRWU1CYUFGRFJVCnRvYWRlUnYvYWYxamtJT0hXU3dNT3ppVk1BOEdBMVVkRXdFQi93UUZNQU1CQWY4d0RRWUpLb1pJaHZjTkFRRUwKQlFBRGdnRUJBRnByajJrZFRoQk93bEtiQ1VNNVpMTDBzbi8rSmI2WXZtSXRFNkpiemRUc3RyaTdsWHk2NlJPNwpTaHF2aURrQVhUYTVWWTc1UFdWNjRMRXlJTW9JYyt2NkdXVSsveWtGTnZTMHJCbm9yczlzdDFyMFllRXhHM0pyCnhHNFhzUzJIbmJ5Yk5oelg3Q3pWRnFGYWh2WEJ0SkZoTGY1TVVUTkFWem0reTgxTlZBcG83bWNmL3ZZKzlmcSsKYjNpVTYvQTluby9JSlZYbWt6V1o2SUQvb0pxQTE1Y0hJaVYrZ05pbDE1dEZKVUtRTkVuMlZWVisveFo3VXJmWgpMTWhtRmZFTGdPUnIvei8vNUx1bXlCeFdOelFCUWhRbVJNSlgzM2IrR1lBbFYvTS85cEZLMHV0NGtaMjZVbkdjCk5TSFJ0VHdseldXNTk4SU40QmUxTjNDU0tEZWwvNGc9Ci0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0K
  tls.crt: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUQyVENDQXNHZ0F3SUJBZ0lVUkthdTNvN1Z0OTZIcDl6aUZoQkd2eFVPbmFBd0RRWUpLb1pJaHZjTkFRRUwKQlFBd1NERUxNQWtHQTFVRUJoTUNRMDR4Q3pBSkJnTlZCQWdNQWtoQ01Rc3dDUVlEVlFRS0RBSlJRekVmTUIwRwpBMVVFQXd3V2QyVmlhRzl2YXkxelpYSjJaWEl0YzJWeWRtbGpaVEFnRncweU5EQXlNVGt3TlRReU1qZGFHQTh5Ck1EVXhNRGN3TnpBMU5ESXlOMW93WlRFTE1Ba0dBMVVFQmhNQ1EwNHhDekFKQmdOVkJBZ01Ba2hDTVFzd0NRWUQKVlFRS0RBSlJRekU4TURvR0ExVUVBd3d6ZDJWaWFHOXZheTF6WlhKMlpYSXRjMlZ5ZG1salpTNXJkV0psYzNCbwpaWEpsTFdSbGRtOXdjeTF6ZVhOMFpXMHVjM1pqTUlJQklqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0FROEFNSUlCCkNnS0NBUUVBcjFIR3BQZlVSdFFjZFdzcjcvc3ZKMWNpdGFpOEpZemVPeXg4WjZ4VXFNR0FXWGpZWkJ1ZmFFbHYKdktQSUtaaWxTK2tnOXFiRi8vMzZtOHVmcnlxMVlvQVNNbkZmZFBQNHBYNkVKbWwzdEdqbytnVlk4NVNLcWxVcwp2c0lBM25pN080U0pLZVRZQ2R1a09qaDdZcFozRkNhdGVGbDJ1TVNXOVQvTjJocHAwdElRTFJwcjBoank4NEhoCkxOQ3B2Y0dLelp3OU5mK08wc2E5S2JYTFdJbmNBNGVLc0FnOUQwc2RMd3Q4QldGbVY3L3VoVDl6Q2xoSW9yd1kKNnRwVGpSOTdTTVJhdHQzNVpxcDdWMWxFUndNd3RmeGx2N2xBOHJtVEJZSlc0alljM2FTVm1BdDRHd0ZOeGZWeApLM2xQNERRSHlCdjdDaVBHaFh6MmdTelFqTFlDNFFJREFRQUJvNEdiTUlHWU1COEdBMVVkSXdRWU1CYUFGRFJVCnRvYWRlUnYvYWYxamtJT0hXU3dNT3ppVk1Ba0dBMVVkRXdRQ01BQXdDd1lEVlIwUEJBUURBZ1R3TUJNR0ExVWQKSlFRTU1Bb0dDQ3NHQVFVRkJ3TUJNRWdHQTFVZEVRUkJNRCtDTTNkbFltaHZiMnN0YzJWeWRtVnlMWE5sY25acApZMlV1YTNWaVpYTndhR1Z5WlMxa1pYWnZjSE10YzNsemRHVnRMbk4yWTRJSWFHOXpkRzVoYldVd0RRWUpLb1pJCmh2Y05BUUVMQlFBRGdnRUJBSm9CWll6TkxzNXVDUlYyNk1VOWtZNVh3cFUzZkhXTUZBenFjbWYrZEtNVVNscEYKcS9Zb2JxOHVmMS9Gbys2bzF3bDJrWklmR1grakUrR1JqQ0kvaXVJUHhhaHZzME8wNkFKWWpTSWhWVkVFNkRqbQpvWW1XTkhpdzRkQXM1aCt6ajNJNmY0bDJscWgxaFVVUnR3anlCL0ZXclRBVFJVOUhrcGtQb0pSL3BEM0Nzd1I1Ckl2OXR1TmpBenNsbzlWZU1vK3JPZWEwS3hhT3RMU1NsWCs5N09iTC9ycXBFZml2L0ZoQ3FMWTcrQW9jcGdSdEsKTzdSYUd3bWMyWlM3aEgzOTRiVjBHVTB6NkpqVHlvdk9HUnZndGxaajVuVmVoK3pkWlNlZVdSbFFpZk5uZ3d0ZQpsMlNDMXJYUDJBblRMNUtLMWZUWjN2UU5NMlljNm1SNWVBK3VKWVk9Ci0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0K
  tls.key: LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpNSUlFcFFJQkFBS0NBUUVBcjFIR3BQZlVSdFFjZFdzcjcvc3ZKMWNpdGFpOEpZemVPeXg4WjZ4VXFNR0FXWGpZClpCdWZhRWx2dktQSUtaaWxTK2tnOXFiRi8vMzZtOHVmcnlxMVlvQVNNbkZmZFBQNHBYNkVKbWwzdEdqbytnVlkKODVTS3FsVXN2c0lBM25pN080U0pLZVRZQ2R1a09qaDdZcFozRkNhdGVGbDJ1TVNXOVQvTjJocHAwdElRTFJwcgowaGp5ODRIaExOQ3B2Y0dLelp3OU5mK08wc2E5S2JYTFdJbmNBNGVLc0FnOUQwc2RMd3Q4QldGbVY3L3VoVDl6CkNsaElvcndZNnRwVGpSOTdTTVJhdHQzNVpxcDdWMWxFUndNd3RmeGx2N2xBOHJtVEJZSlc0alljM2FTVm1BdDQKR3dGTnhmVnhLM2xQNERRSHlCdjdDaVBHaFh6MmdTelFqTFlDNFFJREFRQUJBb0lCQUczYjlYa3NYeFdmRnRJeApQUkFkTzFnUWp3eDhWcUhGR3dERGlKVkNkSzVteXJIR092cklJR1N1RjltQ1hBeE12Yy9LbjBCUUV5U3RseHVIClJtSHloa1RaOGcwdjQ5d2FnVVhhK0o1RldxQnZXUVpLMFltWkhDZE9Sa0ttdVBxdmRzdjk2aUdaYUJNTlVtUzEKUGdQeU8xNGlPbk4reEJsVi95NWhNL0ltdVFkRVZ3VVBCZ0hvSC9na3huSGQ1RUI0ZmFacm0xQURMaDQydFlodQphNUVZdTkzL0RjWm5JMmFvVThCUXNjR09FZXZwMkR3U1NuYTBPWXYrRHFKWkw2OHVyZE5DRzFWU2NBSUowVjJuCjUxM0VKQWowSzVKbXhCbCtvZEZPWVBmbUcwS1BWdUlZREpNd2ZKQkZEVjB5SmJOVFoxOXFncjlueFdsMjR3UkcKaWhVTTZOMENnWUVBMmk0bm9PZzFsczR3TURBd2k2MDA2RlZDWno4NXFHNUNza2JsUUdaNUR3T3FPTlBVTTAvZQpESXJGUFEya1I3N25KemM2eURkVFVkRkJBKzRYdkk2VHl1Lzloa0RKVENWQTRjWkVVT3dVTVBKK1hzaXFWeG9ZCkJPQUtPOEIvZkhDNm9iTUQ2NTdNMnB3V2FLUFJkY2dNMVFtdTBQYUFNdTZEbXdyQVdJbHhIV01DZ1lFQXpiV20KOEx2b1REM3MyRWxSRjRYeHZSQlBBTlhwZk1qcExnNUZLQ216SFU5amR1cXc0MTQ0RzJjLzhYZjNwUmlHOTJFegp6QXpPMFFjMGxsUUR1Y2hLbHhISUJGSXdQeGNmd2swVk1ZNnAvanJFVllHZWdwMUFHR3hMb0hBZTMwSFVOTzJsCkdIU2VPWjhrYkUrNjFaRFRJZGhxWHVJUEdsK3BFZndhTG5oT28rc0NnWUVBb3labWJkV1cxU2xrTVhTbnFKc2gKK0NaaFhIR1QvUlpPZTUrMktMMDRBM2s3SGZtUk1ibWtrdjVtVmF4UXozRzZ5c0ZyREhNS3RDRGxIRG83dDcxcQpXUk96SW1ScDRxM3M0YWZ3U0E3eFhsVEhHTHUzWFNEZkd5NHBtTnJ1dWpCVjd6cTlVTUZUOEpsTnpIdkwwdWFBCmFnSXVub1htQWJBSDY3VlRkaUY0MjM4Q2dZRUF0VEJrTzdSM052aHdiazJkeEtkeE5zTnZvdC9IeWVhNUpKemoKSXk0Zm14aDdGcG8vZGZWZVhCekVnSzdYalM2ZWFyVE9SOU9jTXhjeXBacVlzWUlPMlNPTFZ1c0JuZ0NETThScgpmM3dXbFZ3ejVOREh5bW94czVGbng0Z2FXVEdGZFoxQWh0cnBKdjNhdWlBOEE3S05sVWttNEM0amVXcDY0K0YzCk9pa3pzME1DZ1lFQXdMWjhkcDQySHBaVEg5bnUzNXh3K0FFbVZaUEtDdEFZQ00xdEc4c2p6VVM2bE9GWU4vbTkKZDdFN3VNbzYxNHRkUkNOcEJRTE1EdDBUWTlEb3ZFY1NiNWNqVDFmM0NObEFrY1QyMlEyM2dVSTIyam4wSzgzMgpIU21VTmtXK0RFZkI5OXhTRkhYNXZ6ZWFxVWxQRWN6RzVMSitYa1owd0p3WndKdkpnU0FFNFVnPQotLS0tLUVORCBSU0EgUFJJVkFURSBLRVktLS0tLQo=
kind: Secret
metadata:
  annotations:
    meta.helm.sh/release-name: devops
    meta.helm.sh/release-namespace: kubesphere-devops-system
  labels:
    app.kubernetes.io/managed-by: Helm
  name: s2i-webhook-server-cert
  namespace: kubesphere-devops-system
type: Opaque
```

```bash
kubectl apply -f s2i-webhook-server-cert.yaml
```

### 2. 替换 validating-webhook-configuration

保存 `validating-webhook-configuration.yaml`：

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  annotations:
    meta.helm.sh/release-name: devops
    meta.helm.sh/release-namespace: kubesphere-devops-system
  generation: 3
  labels:
    app.kubernetes.io/managed-by: Helm
  name: validating-webhook-configuration
webhooks:
- admissionReviewVersions:
  - v1
  - v1beta1
  clientConfig:
    caBundle: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURjekNDQWx1Z0F3SUJBZ0lVT0lyK2FFaFhyVEI3Z01UK1RZTFRjMS9rdkowd0RRWUpLb1pJaHZjTkFRRUwKQlFBd1NERUxNQWtHQTFVRUJoTUNRMDR4Q3pBSkJnTlZCQWdNQWtoQ01Rc3dDUVlEVlFRS0RBSlJRekVmTUIwRwpBMVVFQXd3V2QyVmlhRzl2YXkxelpYSjJaWEl0YzJWeWRtbGpaVEFnRncweU5EQXlNVGt3TlRReU1qZGFHQTh5Ck1EVXhNRGN3TnpBMU5ESXlOMW93U0RFTE1Ba0dBMVVFQmhNQ1EwNHhDekFKQmdOVkJBZ01Ba2hDTVFzd0NRWUQKVlFRS0RBSlJRekVmTUIwR0ExVUVBd3dXZDJWaWFHOXZheTF6WlhKMlpYSXRjMlZ5ZG1salpUQ0NBU0l3RFFZSgpLb1pJaHZjTkFRRUJCUUFEZ2dFUEFEQ0NBUW9DZ2dFQkFLRkVpSk9NZlF6ZnJwRE1aOHNNMmxoaFZUVnVGOFU5CjJTYXFCYTNUSU1rc0gvZmlwai8rVjZmaUhLYnh4ZGlrclIxaFZJajFrMkt0aVJRL1ZPbG1pSHdGakVyYUNtNGUKMGhsdzl5Mmt0akF0bzlXYlRaQVV0SFJhK0Q2TUlmajNjUG9QVnV0ZjYyRklYZTNNYmJSaU1SWjNEN2c2RE52SQplUGcydjJyQjZva3g0MDM0L0gxdkk2dTNGaHkvNXRQeklGYmFxU1Z1bHhZck5CUUV1MGhzanVKZVhtK0drWnlTClVuSkpMUkcza1p3Wk1CTitGWDlhRzdvMkJrdVVXT3doMnhUeGp6TFppSEJobUJHbnU1WEVKR0J1a2xaT0tIeE0KQ0lPSGtNVWo4VllIcU5RV3VLaFRvcncraFl1UU9aU2VMaGE1ZFRZczRkdlU1cTdJMjA4VXJBRUNBd0VBQWFOVApNRkV3SFFZRFZSME9CQllFRkRSVXRvYWRlUnYvYWYxamtJT0hXU3dNT3ppVk1COEdBMVVkSXdRWU1CYUFGRFJVCnRvYWRlUnYvYWYxamtJT0hXU3dNT3ppVk1BOEdBMVVkRXdFQi93UUZNQU1CQWY4d0RRWUpLb1pJaHZjTkFRRUwKQlFBRGdnRUJBRnByajJrZFRoQk93bEtiQ1VNNVpMTDBzbi8rSmI2WXZtSXRFNkpiemRUc3RyaTdsWHk2NlJPNwpTaHF2aURrQVhUYTVWWTc1UFdWNjRMRXlJTW9JYyt2NkdXVSsveWtGTnZTMHJCbm9yczlzdDFyMFllRXhHM0pyCnhHNFhzUzJIbmJ5Yk5oelg3Q3pWRnFGYWh2WEJ0SkZoTGY1TVVUTkFWem0reTgxTlZBcG83bWNmL3ZZKzlmcSsKYjNpVTYvQTluby9JSlZYbWt6V1o2SUQvb0pxQTE1Y0hJaVYrZ05pbDE1dEZKVUtRTkVuMlZWVisveFo3VXJmWgpMTWhtRmZFTGdPUnIvei8vNUx1bXlCeFdOelFCUWhRbVJNSlgzM2IrR1lBbFYvTS85cEZLMHV0NGtaMjZVbkdjCk5TSFJ0VHdseldXNTk4SU40QmUxTjNDU0tEZWwvNGc9Ci0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0K
    service:
      name: webhook-server-service
      namespace: kubesphere-devops-system
      path: /validate-devops-kubesphere-io-v1alpha1-s2ibuilder
      port: 443
  failurePolicy: Fail
  matchPolicy: Equivalent
  name: vs2ibuilder.kb.io
  namespaceSelector: {}
  objectSelector: {}
  rules:
  - apiGroups:
    - devops.kubesphere.io
    apiVersions:
    - v1alpha1
    operations:
    - CREATE
    - UPDATE
    resources:
    - s2ibuilders
    scope: '*'
  sideEffects: None
  timeoutSeconds: 10
- admissionReviewVersions:
  - v1
  - v1beta1
  clientConfig:
    caBundle: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURjekNDQWx1Z0F3SUJBZ0lVT0lyK2FFaFhyVEI3Z01UK1RZTFRjMS9rdkowd0RRWUpLb1pJaHZjTkFRRUwKQlFBd1NERUxNQWtHQTFVRUJoTUNRMDR4Q3pBSkJnTlZCQWdNQWtoQ01Rc3dDUVlEVlFRS0RBSlJRekVmTUIwRwpBMVVFQXd3V2QyVmlhRzl2YXkxelpYSjJaWEl0YzJWeWRtbGpaVEFnRncweU5EQXlNVGt3TlRReU1qZGFHQTh5Ck1EVXhNRGN3TnpBMU5ESXlOMW93U0RFTE1Ba0dBMVVFQmhNQ1EwNHhDekFKQmdOVkJBZ01Ba2hDTVFzd0NRWUQKVlFRS0RBSlJRekVmTUIwR0ExVUVBd3dXZDJWaWFHOXZheTF6WlhKMlpYSXRjMlZ5ZG1salpUQ0NBU0l3RFFZSgpLb1pJaHZjTkFRRUJCUUFEZ2dFUEFEQ0NBUW9DZ2dFQkFLRkVpSk9NZlF6ZnJwRE1aOHNNMmxoaFZUVnVGOFU5CjJTYXFCYTNUSU1rc0gvZmlwai8rVjZmaUhLYnh4ZGlrclIxaFZJajFrMkt0aVJRL1ZPbG1pSHdGakVyYUNtNGUKMGhsdzl5Mmt0akF0bzlXYlRaQVV0SFJhK0Q2TUlmajNjUG9QVnV0ZjYyRklYZTNNYmJSaU1SWjNEN2c2RE52SQplUGcydjJyQjZva3g0MDM0L0gxdkk2dTNGaHkvNXRQeklGYmFxU1Z1bHhZck5CUUV1MGhzanVKZVhtK0drWnlTClVuSkpMUkcza1p3Wk1CTitGWDlhRzdvMkJrdVVXT3doMnhUeGp6TFppSEJobUJHbnU1WEVKR0J1a2xaT0tIeE0KQ0lPSGtNVWo4VllIcU5RV3VLaFRvcncraFl1UU9aU2VMaGE1ZFRZczRkdlU1cTdJMjA4VXJBRUNBd0VBQWFOVApNRkV3SFFZRFZSME9CQllFRkRSVXRvYWRlUnYvYWYxamtJT0hXU3dNT3ppVk1COEdBMVVkSXdRWU1CYUFGRFJVCnRvYWRlUnYvYWYxamtJT0hXU3dNT3ppVk1BOEdBMVVkRXdFQi93UUZNQU1CQWY4d0RRWUpLb1pJaHZjTkFRRUwKQlFBRGdnRUJBRnByajJrZFRoQk93bEtiQ1VNNVpMTDBzbi8rSmI2WXZtSXRFNkpiemRUc3RyaTdsWHk2NlJPNwpTaHF2aURrQVhUYTVWWTc1UFdWNjRMRXlJTW9JYyt2NkdXVSsveWtGTnZTMHJCbm9yczlzdDFyMFllRXhHM0pyCnhHNFhzUzJIbmJ5Yk5oelg3Q3pWRnFGYWh2WEJ0SkZoTGY1TVVUTkFWem0reTgxTlZBcG83bWNmL3ZZKzlmcSsKYjNpVTYvQTluby9JSlZYbWt6V1o2SUQvb0pxQTE1Y0hJaVYrZ05pbDE1dEZKVUtRTkVuMlZWVisveFo3VXJmWgpMTWhtRmZFTGdPUnIvei8vNUx1bXlCeFdOelFCUWhRbVJNSlgzM2IrR1lBbFYvTS85cEZLMHV0NGtaMjZVbkdjCk5TSFJ0VHdseldXNTk4SU40QmUxTjNDU0tEZWwvNGc9Ci0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0K
    service:
      name: webhook-server-service
      namespace: kubesphere-devops-system
      path: /validate-devops-kubesphere-io-v1alpha1-s2ibuildertemplate
      port: 443
  failurePolicy: Fail
  matchPolicy: Equivalent
  name: s2ibuildertemplate.kb.io
  namespaceSelector: {}
  objectSelector: {}
  rules:
  - apiGroups:
    - devops.kubesphere.io
    apiVersions:
    - v1alpha1
    operations:
    - CREATE
    - UPDATE
    resources:
    - s2ibuildertemplates
    scope: '*'
  sideEffects: None
  timeoutSeconds: 10
- admissionReviewVersions:
  - v1
  - v1beta1
  clientConfig:
    caBundle: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURjekNDQWx1Z0F3SUJBZ0lVT0lyK2FFaFhyVEI3Z01UK1RZTFRjMS9rdkowd0RRWUpLb1pJaHZjTkFRRUwKQlFBd1NERUxNQWtHQTFVRUJoTUNRMDR4Q3pBSkJnTlZCQWdNQWtoQ01Rc3dDUVlEVlFRS0RBSlJRekVmTUIwRwpBMVVFQXd3V2QyVmlhRzl2YXkxelpYSjJaWEl0YzJWeWRtbGpaVEFnRncweU5EQXlNVGt3TlRReU1qZGFHQTh5Ck1EVXhNRGN3TnpBMU5ESXlOMW93U0RFTE1Ba0dBMVVFQmhNQ1EwNHhDekFKQmdOVkJBZ01Ba2hDTVFzd0NRWUQKVlFRS0RBSlJRekVmTUIwR0ExVUVBd3dXZDJWaWFHOXZheTF6WlhKMlpYSXRjMlZ5ZG1salpUQ0NBU0l3RFFZSgpLb1pJaHZjTkFRRUJCUUFEZ2dFUEFEQ0NBUW9DZ2dFQkFLRkVpSk9NZlF6ZnJwRE1aOHNNMmxoaFZUVnVGOFU5CjJTYXFCYTNUSU1rc0gvZmlwai8rVjZmaUhLYnh4ZGlrclIxaFZJajFrMkt0aVJRL1ZPbG1pSHdGakVyYUNtNGUKMGhsdzl5Mmt0akF0bzlXYlRaQVV0SFJhK0Q2TUlmajNjUG9QVnV0ZjYyRklYZTNNYmJSaU1SWjNEN2c2RE52SQplUGcydjJyQjZva3g0MDM0L0gxdkk2dTNGaHkvNXRQeklGYmFxU1Z1bHhZck5CUUV1MGhzanVKZVhtK0drWnlTClVuSkpMUkcza1p3Wk1CTitGWDlhRzdvMkJrdVVXT3doMnhUeGp6TFppSEJobUJHbnU1WEVKR0J1a2xaT0tIeE0KQ0lPSGtNVWo4VllIcU5RV3VLaFRvcncraFl1UU9aU2VMaGE1ZFRZczRkdlU1cTdJMjA4VXJBRUNBd0VBQWFOVApNRkV3SFFZRFZSME9CQllFRkRSVXRvYWRlUnYvYWYxamtJT0hXU3dNT3ppVk1COEdBMVVkSXdRWU1CYUFGRFJVCnRvYWRlUnYvYWYxamtJT0hXU3dNT3ppVk1BOEdBMVVkRXdFQi93UUZNQU1CQWY4d0RRWUpLb1pJaHZjTkFRRUwKQlFBRGdnRUJBRnByajJrZFRoQk93bEtiQ1VNNVpMTDBzbi8rSmI2WXZtSXRFNkpiemRUc3RyaTdsWHk2NlJPNwpTaHF2aURrQVhUYTVWWTc1UFdWNjRMRXlJTW9JYyt2NkdXVSsveWtGTnZTMHJCbm9yczlzdDFyMFllRXhHM0pyCnhHNFhzUzJIbmJ5Yk5oelg3Q3pWRnFGYWh2WEJ0SkZoTGY1TVVUTkFWem0reTgxTlZBcG83bWNmL3ZZKzlmcSsKYjNpVTYvQTluby9JSlZYbWt6V1o2SUQvb0pxQTE1Y0hJaVYrZ05pbDE1dEZKVUtRTkVuMlZWVisveFo3VXJmWgpMTWhtRmZFTGdPUnIvei8vNUx1bXlCeFdOelFCUWhRbVJNSlgzM2IrR1lBbFYvTS85cEZLMHV0NGtaMjZVbkdjCk5TSFJ0VHdseldXNTk4SU40QmUxTjNDU0tEZWwvNGc9Ci0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0K
    service:
      name: webhook-server-service
      namespace: kubesphere-devops-system
      path: /validate-devops-kubesphere-io-v1alpha1-s2irun
      port: 443
  failurePolicy: Fail
  matchPolicy: Equivalent
  name: vs2irun.kb.io
  namespaceSelector: {}
  objectSelector: {}
  rules:
  - apiGroups:
    - devops.kubesphere.io
    apiVersions:
    - v1alpha1
    operations:
    - CREATE
    - UPDATE
    resources:
    - s2iruns
    scope: '*'
  sideEffects: None
  timeoutSeconds: 10
```

```bash
kubectl apply -f validating-webhook-configuration.yaml
```

### 3. 替换 mutating-webhook-configuration

保存 `mutating-webhook-configuration.yaml`：

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: MutatingWebhookConfiguration
metadata:
  annotations:
    meta.helm.sh/release-name: devops
    meta.helm.sh/release-namespace: kubesphere-devops-system
  generation: 2
  labels:
    app.kubernetes.io/managed-by: Helm
  name: mutating-webhook-configuration
webhooks:
- admissionReviewVersions:
  - v1
  - v1beta1
  clientConfig:
    caBundle: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURjekNDQWx1Z0F3SUJBZ0lVT0lyK2FFaFhyVEI3Z01UK1RZTFRjMS9rdkowd0RRWUpLb1pJaHZjTkFRRUwKQlFBd1NERUxNQWtHQTFVRUJoTUNRMDR4Q3pBSkJnTlZCQWdNQWtoQ01Rc3dDUVlEVlFRS0RBSlJRekVmTUIwRwpBMVVFQXd3V2QyVmlhRzl2YXkxelpYSjJaWEl0YzJWeWRtbGpaVEFnRncweU5EQXlNVGt3TlRReU1qZGFHQTh5Ck1EVXhNRGN3TnpBMU5ESXlOMW93U0RFTE1Ba0dBMVVFQmhNQ1EwNHhDekFKQmdOVkJBZ01Ba2hDTVFzd0NRWUQKVlFRS0RBSlJRekVmTUIwR0ExVUVBd3dXZDJWaWFHOXZheTF6WlhKMlpYSXRjMlZ5ZG1salpUQ0NBU0l3RFFZSgpLb1pJaHZjTkFRRUJCUUFEZ2dFUEFEQ0NBUW9DZ2dFQkFLRkVpSk9NZlF6ZnJwRE1aOHNNMmxoaFZUVnVGOFU5CjJTYXFCYTNUSU1rc0gvZmlwai8rVjZmaUhLYnh4ZGlrclIxaFZJajFrMkt0aVJRL1ZPbG1pSHdGakVyYUNtNGUKMGhsdzl5Mmt0akF0bzlXYlRaQVV0SFJhK0Q2TUlmajNjUG9QVnV0ZjYyRklYZTNNYmJSaU1SWjNEN2c2RE52SQplUGcydjJyQjZva3g0MDM0L0gxdkk2dTNGaHkvNXRQeklGYmFxU1Z1bHhZck5CUUV1MGhzanVKZVhtK0drWnlTClVuSkpMUkcza1p3Wk1CTitGWDlhRzdvMkJrdVVXT3doMnhUeGp6TFppSEJobUJHbnU1WEVKR0J1a2xaT0tIeE0KQ0lPSGtNVWo4VllIcU5RV3VLaFRvcncraFl1UU9aU2VMaGE1ZFRZczRkdlU1cTdJMjA4VXJBRUNBd0VBQWFOVApNRkV3SFFZRFZSME9CQllFRkRSVXRvYWRlUnYvYWYxamtJT0hXU3dNT3ppVk1COEdBMVVkSXdRWU1CYUFGRFJVCnRvYWRlUnYvYWYxamtJT0hXU3dNT3ppVk1BOEdBMVVkRXdFQi93UUZNQU1CQWY4d0RRWUpLb1pJaHZjTkFRRUwKQlFBRGdnRUJBRnByajJrZFRoQk93bEtiQ1VNNVpMTDBzbi8rSmI2WXZtSXRFNkpiemRUc3RyaTdsWHk2NlJPNwpTaHF2aURrQVhUYTVWWTc1UFdWNjRMRXlJTW9JYyt2NkdXVSsveWtGTnZTMHJCbm9yczlzdDFyMFllRXhHM0pyCnhHNFhzUzJIbmJ5Yk5oelg3Q3pWRnFGYWh2WEJ0SkZoTGY1TVVUTkFWem0reTgxTlZBcG83bWNmL3ZZKzlmcSsKYjNpVTYvQTluby9JSlZYbWt6V1o2SUQvb0pxQTE1Y0hJaVYrZ05pbDE1dEZKVUtRTkVuMlZWVisveFo3VXJmWgpMTWhtRmZFTGdPUnIvei8vNUx1bXlCeFdOelFCUWhRbVJNSlgzM2IrR1lBbFYvTS85cEZLMHV0NGtaMjZVbkdjCk5TSFJ0VHdseldXNTk4SU40QmUxTjNDU0tEZWwvNGc9Ci0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0K
    service:
      name: webhook-server-service
      namespace: kubesphere-devops-system
      path: /mutate-devops-kubesphere-io-v1alpha1-s2ibuilder
      port: 443
  failurePolicy: Fail
  matchPolicy: Equivalent
  name: s2ibuilder.kb.io
  namespaceSelector: {}
  objectSelector: {}
  reinvocationPolicy: Never
  rules:
  - apiGroups:
    - devops.kubesphere.io
    apiVersions:
    - v1alpha1
    operations:
    - CREATE
    - UPDATE
    resources:
    - s2ibuilders
    scope: '*'
  sideEffects: None
  timeoutSeconds: 10
```

```bash
kubectl apply -f mutating-webhook-configuration.yaml
```

### 4. 重启 s2ioperator

```bash
kubectl -n kubesphere-devops-system rollout restart sts s2ioperator
```

## 证书生成方式

上述的 `caBundle`、`tls.crt`、`tls.key` 先由以下脚本生成证书文件，再通过 `base64 -w 0 [ca.crt/server.crt/server.key]` 转换得到：

```bash
#!/bin/bash

set -e

usage() {
    cat <<EOF
Generate certificate suitable for use with an sidecar-injector webhook service.
This script uses k8s' CertificateSigningRequest API to a generate a
certificate signed by k8s CA suitable for use with sidecar-injector webhook
services. This requires permissions to create and approve CSR. See
https://kubernetes.io/docs/tasks/tls/managing-tls-in-a-cluster for
detailed explantion and additional instructions.
The server key/cert k8s CA cert are stored in a k8s secret.
usage: ${0} [OPTIONS]
The following flags are required.
       --service          Service name of webhook.
       --namespace        Namespace where webhook service and secret reside.
EOF
    exit 1
}

while [[ $# -gt 0 ]]; do
    case ${1} in
        --service)
            service="$2"
            shift
            ;;
        --namespace)
            namespace="$2"
            shift
            ;;
        *)
            usage
            ;;
    esac
    shift
done

[ -z ${service} ] && service=webhook-service
[ -z ${namespace} ] && namespace=default

if [ ! -x "$(command -v openssl)" ]; then
    echo "openssl not found"
    exit 1
fi

csrName=${service}.${namespace}
CERTSDIR="config/certs"

if [ ! -d ${CERTSDIR} ]; then
  mkdir -p ${CERTSDIR}
fi

cat > v3.ext <<-EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names
[alt_names]
DNS.1=${service}.${namespace}.svc
DNS.2=hostname
EOF

echo "creating certs in certsdir ${CERTSDIR} "

# create cakey
openssl genrsa -out ${CERTSDIR}/ca.key 2048

# create ca.crt
openssl req -x509 -new -nodes -key ${CERTSDIR}/ca.key -subj "/C=CN/ST=HB/O=QC/CN=${service}" -sha256 -days 10000 -out ${CERTSDIR}/ca.crt

# create server.key
openssl genrsa -out ${CERTSDIR}/server.key 2048

# create server.crt
openssl req -new -sha256 -key ${CERTSDIR}/server.key -subj "/C=CN/ST=HB/O=QC/CN=${service}.${namespace}.svc" -out ${CERTSDIR}/server.csr
openssl x509 -req -in ${CERTSDIR}/server.csr -extfile v3.ext -CA ${CERTSDIR}/ca.crt -CAkey ${CERTSDIR}/ca.key -CAcreateserial -out ${CERTSDIR}/server.crt -days 10000 -sha256
```

`cert.sh` 由 [s2ioperator/hack/certs.sh](https://github.com/kubesphere/s2ioperator/blob/master/hack/certs.sh) 微调而得

生成证书文件方式

```bash
./cert.sh --service webhook-server-service --namespace kubesphere-devops-system
```

执行完毕后，会生成如下文件

```bash
$ tree config/certs
config/certs
├── ca.crt
├── ca.key
├── ca.srl
├── server.crt
├── server.csr
└── server.key
```

文件对应关系如下：

`ca.crt` -> `caBundle`<br>
`server.key` -> `tls.key`<br>
`server.crt` -> `tls.crt`

> 注意：三个 yaml 文件中的 `caBundle` 需要使用相同的值。

## 参考资料

- [kubesphere3.4 S2i证书过期修复记录](https://www.jianshu.com/p/a573e9893577)
- [s2i服务不可用提示证书失效](https://ask.kubesphere.com.cn/forum/d/23227-s2ifu-wu-bu-ke-yong-ti-shi-zheng-shu-shi-xiao)
