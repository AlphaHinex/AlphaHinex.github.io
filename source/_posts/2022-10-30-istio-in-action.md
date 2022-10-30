---
id: istio-in-action
title: "《Istio in Action》书摘"
description: "深入浅出的讲解了 Istio 的原理、用法等，并配有实际例子，可作为快速了解 Istio 的读物"
date: 2022.10.30 10:34
categories:
    - Book
    - Cloud Native
tags: [Kubernetes, Istio]
keywords: Kubernetes, Istio, Serivce Mesh, Envoy
cover: /contents/istio-in-action/cover.jpg
---

# Chapter 1. Introducing Istio Service Mesh

## 1.4 Pushing these concerns to the infrastructure

### 1.4.3 Meet Envoy proxy

* Envoy gives us networking capabilities like retries, timeouts, circuit breaking, client-side load balancing, service discovery, security, and metrics-collection without any explicit language or framework dependencies.
* The power of Envoy is not limited to these application-level resilience aspects. Envoy also captures many application-networking metrics like requests per second, number of failures, circuit-breaking events, and more.
* This proxy+application combination forms the foundation of a communication bus known as a service mesh.

## 1.5 What’s a service mesh?

* A `service mesh` is a distributed application infrastructure that is responsible for handling network traffic on behalf of the application in a transparent, out of process manner.
* Service mesh architecture with co-located application-level proxies (data plane) and management components (control plane)
![](/contents/istio-in-action/figure-1.14.png)

## 1.6 Introducing Istio service mesh

* Istio’s data plane uses Envoy proxy by default out of the box and helps you configure your applications to have an instance of the service proxy (Envoy) deployed alongside it. Istio’s control plane is made up of a few components that provide APIs for end users/operators, configuration APIs for the proxies, security settings, policy declarations, and more. 
* Istio is an implementation of a service mesh with a data plane based on Envoy and a control plane
![](/contents/istio-in-action/figure-1.15.png)
1. Traffic comes into the cluster (ie, a client issues a POST "/checkout" request to our shopping cart service)
2. Traffic goes to the shopping-cart service but goes to the Istio service proxy (Envoy). Note, this traffic (and all inter-service communication in the mesh) is secured with mutual TLS by default. The certificates for establishing mTLS are provided by (7).
3. Istio determines (by looking at the request headers) that this request was initiated by a customer in the North America region, and for those customers, we want to route some of those requests to v1.1 of the Tax service which has a fix for certain tax calculations; Istio routes the traffic to the v1.1 Tax service
4. Istio Pilot is used to configure the istio proxies which handle routing, security, and resilience
5. Request metrics are periodically sent back to the Istio Mixer which stores them to back end adapters (to be discussed later)
6. Distributed tracing spans (like Jaeger or Zipkin) are sent back to an tracing store which can be used to later track the path and latency of a request through the system
7. Istio Auth which manages certificates (expiry, rotation, etc) for each of the istio proxies so mTLS can be enabled transparently


# Chapter 2. First steps with Istio

## 2.2 Getting to know the Istio control plane

### 2.2.1 Istiod

* Istio’s control plane responsibilities are implemented in the istiod component.
* Envoy’s "discovery APIs" ... like those for service discovery (Listener Discovery Service - LDS), endpoints (Endpoint Discovery Service - EDS), or routing rules (Route Discovery Service - RDS) are known as the `xDS` APIs.
* SPIFFE (Secure Production Identity Framework For Everyone - spiffe.io) which gives the ability to provide strong mutual authentication (mTLS) without the applications having to be aware of certificates, public/private keys, etc.

## 2.3 Deploy your first application in the service mesh

```bash
$ istioctl kube-inject -f services/catalog/kubernetes/catalog.yaml
```
* The `istioctl kube-inject` command takes a Kubernetes resource file and enriches it with the sidecar deployment of the Istio service proxy.
* When we ran `kube-inject`, we add another container named 'istio-proxy' to the Pod declaration, though we’ve not actually deployed anything yet. We can take the yaml file created by the `kube-inject` command and deploy that directly. 

```bash
$ istioctl kube-inject -f services/catalog/kubernetes/catalog.yaml \ 
| kubectl apply -f -

serviceaccount/catalog created 
service/catalog created 
deployment.extensions/catalog created
```

* All the user has to do is label their namespace with `istio-injection=enabled` and when they deploy their application, Istio’s sidecar will automatically be injected.


# Chapter 3. Istio’s data plane: Envoy Proxy

## 3.4 How Envoy fits with Istio

* Envoy forms the data plane of a service mesh. The supporting components, which Istio provides, creates the control plane.
* Istio implements these XDS APIs in Istio Pilot.
* Istio abstracts away service registry and provides an implementation of Envoy’s xDS API
![](/contents/istio-in-action/figure-3.5.png)
* Envoy can terminate and originate TLS traffic to services in our mesh. To do this, you need supporting infrastructure to create, sign and rotate certificates. Istio provides this with the Istio Citadel component.
* Istio Citadel delivers application-specific certificates which can be used to establish mutual TLS to secure the traffic between services
![](/contents/istio-in-action/figure-3.7.png)


# Chapter 4. Istio Gateway: getting traffic into your cluster

## 4.1 Traffic ingress concepts

### 4.1.2 Virtual Hosting: multiple services from a single access point

* We can also represent multiple different services using a single virtual IP.
* If the reverse proxy was smart enough, it could use the Host HTTP header to further delineate which requests should go to which group of services.
* Virtual hosting lets us map multiple services to a single Virtual IP
![](/contents/istio-in-action/figure-4.4.png)
* Hosting multiple different services at a single entry point is known as `virtual hosting`. We need some way to decide to which virtual-host group a particular request should be routed. With HTTP/1.1, we can use the Host header, with HTTP/2 we can use the `:authority` header, and with TCP connections we can rely on Server Name Indication (SNI) with TLS.

## 4.2 Istio Gateway

### 4.2.2 Gateway routing with Virtual Services

* In Istio, a `VirtualService` resource defines how a client talks to a specific service through its fully qualified domain name, which versions of a service are available, and other routing properties (like retries and request timeouts).

### 4.2.4 Istio Gateway vs Kubernetes Ingress

* Istio Gateway handles the L4 and L5 concerns while `VirtualService` handles the L7 concerns.

## 4.3 Securing Gateway traffic

### 4.3.1 HTTP traffic with TLS

* Basic model of how TLS is established between a client and server
![](/contents/istio-in-action/figure-4.8.png)
* We can use a `curl` parameter called `--resolve` that lets us call the service as though it was at `apiserver.istioinaction.io` but then tell curl to use localhost:

```bash
$ curl -H "Host: apiserver.istioinaction.io" \ 
https://apiserver.istioinaction.io:443/api/catalog \ 
--cacert certs/2_intermediate/certs/ca-chain.cert.pem \ 
--resolve apiserver.istioinaction.io:443:127.0.0.1
```

### 4.3.3 HTTP traffic with mutual TLS

* When the client and server each verify the other’s certificates and use these to encrypt traffic, we call this mutual TLS (mTLS).


# Chapter 5. Traffic control: fine-grained traffic routing

## 5.3 Traffic shifting

* Let’s route 10% of the traffic to the v2 of catalog service:
```yaml
apiVersion: networking.istio.io/v1alpha3 
kind: VirtualService
metadata:
  name: catalog
spec:
  hosts:
  - catalog
  gateways:
    - mesh 
  http:
  - route:
    - destination:
        host: catalog
        subset: version-v1 
      weight: 90
    - destination: 
        host: catalog
        subset: version-v2 
      weight: 10
```
> most traffic to v1, some traffic to v2

## 5.4 Lowering risk even further: Traffic mirroring

```yaml
apiVersion: networking.istio.io/v1alpha3 
kind: VirtualService
metadata:
  name: catalog
spec:
  hosts:
  - catalog 
  gateways:
    - mesh 
  http:
  - route:
    - destination:
        host: catalog
        subset: version-v1
      weight: 100
    mirror:
      host: catalog 
      subset: version-v2
```
* This mirrored request cannot affect the real request because the Istio proxy that does the mirroring will ignore any responses (success/failure) from the mirrored cluster.
* ... when the mirrored traffic makes it to `catalog` v2 service, the `Host` header has been modified to indicate it is mirrored/shadowed traffic. Instead of `Host: 10.12.1.178:8080` for the Host header, we see `Host: 10.12.1.178-shadow:8080`. A service that receives a request with the `-shadow` postfix can identify that request as a mirrored request and take that into consideration when processing it (for example, that the response will be discarded, so either roll back a transaction or don’t make any calls that are resource intensive).

## 5.5 Routing to services outside your cluster by using Istio’s service discovery

* The Istio `ServiceEntry` encapsulates registry metadata that we can use to insert an entry into Istio’s service registry.


# Chapter 6. Resilience: solving application-networking challenges

## 6.2 Client-side load balancing

* Service operators and developers can configure what load-balancing algorithm a client uses by defining a `DestinationRule`.

### 6.2.1 Getting started with client-side load balancing

* A DestinationRule specifies policies for clients in the mesh calling the specific destination.
```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: simple-backend-dr
spec:
  host: simple-backend.istioinaction.svc.cluster.local
  trafficPolicy:
    loadBalancer:
      simple: ROUND_ROBIN
```

### 6.2.4 Understanding the different load balancing algorithms

* Envoy least request load balancing: Even though the Istio configuration refers to the least-request load balancing as `LEAST_CONN`, Envoy is in fact tracking request depths for endpoints, not connections. The load balancer will pick two random endpoints and check which has the fewest active requests. The load balancer will pick the one with the fewest active requests and do the same thing for successive load-balancing tries. This is known as the "power of two choices" and has been shown to be a good tradeoff (vs a full scan) when implementing a load balancer like this and achieving good results. See the Envoy documentation for more on this load balancer.

## 6.3 Locality aware load balancing

### 6.3.1 Hands on with locality load balancing

* When deploying in Kubernetes, region and zone information can be added to labels on the Kubernetes nodes. For example labels `failure-domain.beta.kubernetes.io/region` and `failure-domain.beta.kubernetes.io/zone` allow to specify region and zone respectively. Often these labels are automatically added by cloud providers like Google Cloud or AWS. Istio will pick up these node labels and enrich the Envoy load-balancing endpoints with this locality information.
* Kubernetes failure domain labels: In previous versions of Kubernetes' API, `failure-domain.beta.kubernetes.io/region` and `failure-domain.beta.kubernetes.io/zone` where the labels used to identify region and zone. In GA versions of the Kubernetes API, those labels have been replaced with `topology.kubernetes.io/region` and `topology.kubernetes.io/zone`. Just be aware, cloud vendors still use the older `failure-domain` labels. Istio looks for both.
* Istio gives an approach to explicitly set the locality of our workloads. We can label our pods with `istio-locality` and give it an explicit region/zone.
* Istio’s locality-aware load balancing is enabled by default. If you wish to disable it, you can configure the `meshConfig.localityLbSetting.enabled` setting to be false.
* Without health checking, Istio does not know which endpoints in the load balancing pool are unhealthy and what heuristics to use to spill over into the next locality.

### 6.3.2 More control over locality load balancing

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: simple-backend-dr
spec:
  host: simple-backend.istioinaction.svc.cluster.local
  trafficPolicy:
    loadBalancer:
      localityLbSetting:
        distribute:
        - from: us-west1/us-west1-a/*
          to:
            "us-west1/us-west1-a/*": 70
            "us-west1/us-west1-b/*": 30
    connectionPool:
      http:
        http2MaxRequests: 10
        maxRequestsPerConnection: 10
    outlierDetection:
      consecutive5xxErrors: 1
      interval: 5s
      baseEjectionTime: 30s
      maxEjectionPercent: 100
```
> * `loadBalancer`: Add load balancer config
> * `from`: Set origin zone
> * `to`: Set two dest zones

## 6.4 Transparent timeouts and retries

### 6.4.2 Retries

* By default, Istio will try a call and if it fails, will try 2 more times. This default retry will only apply to certain situations. These default situations are typically safe to retry a request:
1. connect-failure
1. refused-stream
1. unavailable (grpc status code 14)
1. cancelled (grpc status code 1)
1. retriable-status-codes (default to HTTP 503 in istio)
* Each retry will have its own `perTryTimeout`. One thing to note about this setting is that the `perTryTimeout` value multiplied by the attempts must be lower than the overall request timeout (described in previous section). For example, an overall timeout of 1s and retry policy of three attempts with per retry timeout of 500ms won’t work. The overall request timeout will kick in before all of the retries get a chance.
* Between retries, Istio will "backoff" the retry with a base of 25ms. This means for each successive retry, it will backoff (wait) until (25ms x attempt #) so to stagger the retries. At the moment this retry base is fixed, but as we will see in the next section we can make changes to parts of the Envoy API that are not exposed by Istio.
* Request flow on retries when requests fail
![](/contents/istio-in-action/figure-6.13.png)
* Thundering herd effect when retries compound each other
![](/contents/istio-in-action/figure-6.14.png)

### 6.4.3 Advanced retries

* EnvoyFilter API: Just note that the EnvoyFilter API is a "break glass" solution. Istio’s API in general is an abstraction over the underlying dataplane. The underlying Envoy API may change at any time between releases of Istio so be sure to validate any EnvoyFilter you put into production. Do not assume any backward compatibility here.
* When a request reaches its threshold and timesout, we can optionally configure Envoy under the covers to perform what’s called "request hedging". With request hedging, if a request timesout, Envoy can send another request to a different host to "race" the original, timed-out request. In this the case if the "raced" request returns successfully, it’s response is sent to the original downstream caller. If the original request actually returns, but before the raced request returns, it will be returned to the downstream caller.

## 6.5 Circuit breaking with Istio

* In Istio we will use the `connectionPool` settings in a DestinationRule to limit the number of connections and requests that may be piling up when calling a service. If too many requests pile up, we can short-circuit them (fail fast) and return to the client.

### 6.5.1 Guarding against slow services with connection pool control

* When a request fails for tripping a circuit breaking threshold, Istio’s service proxy will add a `X-Envoy-Overloaded` header.


# Chapter 7. Observability with Istio: understanding the behavior of your services

* Mean Time To Recovery (MTTR), an important measure in high-performing teams and their impact on the business.

## 7.1 What is observability?

### 7.1.1 Observability vs Monitoring

* Monitoring is a subset of observability. With monitoring we are specifically collecting and aggregating metrics to watch for known undesirable states and then alert on them. Observability on the other hand supposes up front that our systems are highly unpredictable and we cannot know all of the possible failure modes up front. We need to collect much more data, even high-cardinality data like userIDs, requestIDs, source IPs, etc where the entire set could be exponentially large, and use tools to quickly explore and ask questions about the data.

## 7.2 Collecting metrics from Istio data plane

* StatsD is a metric collection system open-sourced by Etsy to format, collect, and distribute statistics like counters, guages, and timers to backend monitoring, alerting, or visualization tools.

### 7.2.2 Pulling Istio Metrics into Prometheus

* Prometheus is slighly different from other telemetry or metrics collection systems in that it "pulls" metrics from its targets rather than listens for the targets to send their metrics to it.
* ... Prometheus queries the Kubernetes API for Pods and other information related to what’s running in Kubernetes. Therefore, we should configure the correct RBAC permissions so that Prometheus will have the correct permissions to query the Kubernetes API.

## 7.4 Distributed tracing with OpenTracing

### 7.4.1 How does it work

* With distributed tracing, we can collect Spans for each network hop and capture them in an overall Trace and use them to debug issues within our call graph
![](/contents/istio-in-action/figure-7.4.png)
* Istio appends HTTP headers, commonly known as the Zipkin tracing headers, to the request that can be used to correlate subsequent Span objects to the overall `Trace`.
* The following Zipkin tracing headers are used by Istio and the distributed-tracing functionality:
1. x-request-id
1. x-b3-traceid
1. x-b3-spanid
1. x-b3-parentspanid
1. x-b3-sampled
1. x-b3-flags
1. x-ot-span-context

### 7.4.4 Limiting tracing apeture

* Another approach to limit the aperture of distributed tracing is to turn it on for only specific requests. If we change the `PILOT_TRACE_SAMPLING` back down to the default of 1.0 we shouldn’t see traces for every request we send to our sample apps.
* If we would like Istio to record a trace for a specific request, we can add the `x-envoy-force-trace` header to the request.

## 7.5 Visualization with Kiali

* Understanding Kiali workload vs application:
1. A workload is a running binary that can be deployed as a set of identical-running replicas. For example, in Kubernetes this would be the Pods part of a Deployment. If we had a "service A" deployment with 3 replicas, this would be a workload.
1. An application is a grouping of workloads and associated constructs like services and configuration. In Kubernetes this would be a "service A" along with a "service B" and maybe a "database". These would each be their own workload, but they would together make up a Kiali application.


# Chapter 8. Istio Security: Effortlessly secure

## 8.1 Application Security refresher

### 8.1.4 Comparison of security in Monoliths and Microservices

* To resolve the challenges of providing Identity in high dynamic and heterogeneous environments Istio uses the SPIFFE specification.

## 8.2 SPIFFE - Secure Production Identity Framework for Everyone

* SPIFFE is a set of open source-standards for providing identity to workloads in highly dynamic and heterogeneous environments.

### 8.2.1 SPIFFE ID - Workload Identity

* SPIFFE Identity is an RFC 3986 compliant URI composed in the following format `spiffe://trust-domain/path`.

### 8.2.4 SPIFFE Verifiable Identity Document

* By implementing the SPIFFE specification, Istio automatically ensures that all workloads have their identity provisioned and receive certificates as proof of their identity. Those certificates are used for mutual authentication and to encrypt all service-to-service communication. Hence this feature is called Auto mTLS.

### 8.2.5 How Istio implements SPIFFE

* Mapping of Istio components to the Spiffe specification
![](/contents/istio-in-action/figure-8.6.png)
* Mapping the SPIFFE components to Istio’s implementation
1. The Workload Endpoint is implemented by the Pilot-Agent that performs identity bootstrapping
1. The Workload API is implemented by Istio CA that issues certificates
1. The Workload for whom the identity is issued in Istio is the service proxy

### 8.2.6 Step by step bootstrapping of Workload Identity

* Issuing a SVID in Kubernetes with Istio
![](/contents/istio-in-action/figure-8.7.png)
* Elaboration of the points seen in Figure 8.7:
1. Service account token is assigned to the Istio Proxy container
2. The token and a Certificate Signing Request are sent to Istiod
3. Istiod validates the token using the Kubernetes Token Review API
4. On success, it signs the certificate and provides it as a response
5. The Pilot Agent uses the Secrets Discovery Service of Envoy to configure it to use the certificate containing the identity.

## 8.6 What is a request identity anyway?

### 8.6.3 Overview of the flow of one request

* Collection of validated data in Filter Metadata
![](/contents/istio-in-action/figure-8.14.png)

-----

# 本书中涉及的 Istio 中定义的资源

## VirtualService

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: catalog-service
spec:
  hosts:
  - catalog.prod.svc.cluster.local
  http:
  - match:
    - headers:
        x-dark-lauch:
          exact: "v2"
    route:
    - destination:
        host: catalog.prod.svc.cluster.local
        subset: v2
  - route:
    - destination:
        host: catalog.prod.svc.cluster.local
        subset: v1
```

## DestinationRule

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: catalog
spec:
  host: catalog
  subsets:
  - name: version-v1
    labels:
      version: v1
  - name: version-v2
    labels:
      version: v2
```

## Gateway

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: coolstore-gateway
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "apiserver.istioinaction.io"
```

## ServiceEntry

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: ServiceEntry
metadata:
  name: jsonplaceholder
spec:
  hosts:
  - jsonplaceholder.typicode.com
  ports:
  - number: 80
    name: http
    protocol: HTTP
  resolution: DNS
  location: MESH_EXTERNAL
```

## EnvoyFilter

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: EnvoyFilter
metadata:
  name: simple-backend-retry-status-codes
  namespace: istioinaction
spec:
  workloadSelector:
    labels:
      app: simple-web
  configPatches:
  - applyTo: HTTP_ROUTE
    match:
      context: SIDECAR_OUTBOUND
      routeConfiguration:
        vhost:
          name: "simple-backend.istioinaction.svc.cluster.local:80"
    patch:
      operation: MERGE
      value:
        route:
          retry_policy:
            retry_back_off:
              base_interval: 50ms
          retriable_status_codes:
          - 402
          - 403
```

## metric

```yaml
apiVersion: "config.istio.io/v1alpha2"
kind: metric
metadata:
  name: apigatewayrequestcount
  namespace: istio-system
spec:
  value: "1"
  dimensions:
    source: source.workload.name | "unknown"
    destination: destination.workload.name | "unknown"
    destination_ip: destination.ip
  monitored_resource_type: '"UNSPECIFIED"'
```

## prometheus

```yaml
apiVersion: "config.istio.io/v1alpha2"
kind: prometheus
metadata:
  name: apigatewayrequestcounthandler
  namespace: istio-system
spec:
  metrics:
    - name: apigateway_request_count
      instance_name: apigatewayrequestcount.metric.istio-system
      kind: COUNTER
      label_names:
        - source
        - destination
        - destination_ip
```

## PeerAuthentication

```yaml
apiVersion: "security.istio.io/v1beta1"
kind: "PeerAuthentication"
metadata:
  name: "default"
  namespace: "istio-system"
spec:
  mtls:
    mode: STRICT
```

## AuthorizationPolicy

```yaml
apiVersion: "security.istio.io/v1beta1"
kind: "AuthorizationPolicy"
metadata:
  name: "allow-catalog-requests-in-api-gw"
  namespace: istioinaction
spec:
  selector:
    matchLabels:
      app: apigateway
  rules:
  - to:
    - operation:
        paths: ["/api/catalog*"]
  action: ALLOW
```

## RequestAuthentication

```yaml
apiVersion: "security.istio.io/v1beta1"
kind: "RequestAuthentication"
metadata:
  name: "jwt-token-request-authn"
  namespace: istio-system
spec:
  selector:
    matchLabels:
      app: istio-ingressgateway
  jwtRules:
  - issuer: "auth@istioinaction.io"
    jwks: |
     { "keys": [{"e":"AQAB","kid":"##REDACTED##","kty":"RSA","n":"##REDACTED##"}]}
```