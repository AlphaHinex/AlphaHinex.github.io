---
id: dify-in-arm
title: "ARM 环境中部署 Dify"
description: "本文整理了在 ARM 环境部署 Dify 遇到的问题和解决方案"
date: 2024.11.24 10:26
categories:
    - AI
tags: [AI, Dify, Arm]
keywords: Dify, ARM, Docker, Docker Compose, pypdfium2
cover: /contents/covers/dify-in-arm.png
---

# 准备 arm 版镜像

将下面内容保存为 `arm-images.yaml`，执行 `docker compose -f arm-images.yaml pull` 拉取所需镜像：

```yaml
services:
  # The nginx reverse proxy.
  # used for reverse proxying the API service and Web service.
  nginx:
    image: nginx:1.27.2
    platform: arm64

  # API service
  api:
    image: langgenius/dify-api:0.11.1
    platform: arm64

  # worker service
  # The Celery worker for processing the queue.
  worker:
    image: langgenius/dify-api:0.11.1
    platform: arm64

  # Frontend web application.
  web:
    image: langgenius/dify-web:0.11.1
    platform: arm64

  # The postgres database.
  db:
    image: postgres:15-alpine
    platform: arm64

  # The redis cache.
  redis:
    image: redis:6-alpine
    platform: arm64

  # The DifySandbox
  sandbox:
    image: langgenius/dify-sandbox:0.2.10
    platform: arm64

  # The Weaviate vector store.
  weaviate:
    image: semitechnologies/weaviate:1.19.0
    platform: arm64
```

# 调整镜像

从 https://pypi.org/project/pypdfium2/#files 下载 [pypdfium2-4.30.0-py3-none-manylinux_2_17_aarch64.manylinux2014_aarch64.whl](https://files.pythonhosted.org/packages/11/63/28a73ca17c24b41a205d658e177d68e198d7dde65a8c99c821d231b6ee3d/pypdfium2-4.30.0-py3-none-manylinux_2_17_aarch64.manylinux2014_aarch64.whl) ，之后使用下面 Dockerfile 重新构建一个镜像：   

```Dockerfile
FROM langgenius/dify-api:0.11.1
COPY pypdfium2-4.30.0-py3-none-manylinux_2_17_aarch64.manylinux2014_aarch64.whl /tmp
RUN pip install /tmp/pypdfium2-4.30.0-py3-none-manylinux_2_17_aarch64.manylinux2014_aarch64.whl
docker build -t langgenius/dify-api:0.11.1-arm .
```

> - https://github.com/langgenius/dify/discussions/10580
> - https://github.com/langgenius/dify/discussions/10580#discussioncomment-11333977
> - https://github.com/langgenius/dify/pull/10942

# 调整 docker-compose.yaml

基于官方 [docker-compose.yaml](https://github.com/langgenius/dify/blob/main/docker/docker-compose.yaml)，精简掉暂不使用的向量库等配置，并修改如下内容：

- 将 `dify-api` 镜像调整为上面重新构建的版本，以解决 ARM 环境启动报错问题；
- 为 `dify-api` 和 `dify-sandbox` 服务添加 `privileged: true` 配置，以解决 https://github.com/langgenius/dify/issues/886 中描述的 `OpenBLAS blas_thread_init: pthread_create failed for thread 5 of 6: Operation not permitted` 问题；
- 修改环境变量参数中的 `LOG_FILE: ${LOG_FILE:-}` 为 `LOG_FILE: ${LOG_FILE:-/var/log/dify_server.log}` 以解决 https://github.com/langgenius/dify/issues/10555#issuecomment-2470651673 中描述的 `IsADirectoryError: [Errno 21] Is a directory: '/app/api'` 报错。

附调整后的 `streamline.yaml`：

```yaml
x-shared-env: &shared-api-worker-env
  WORKFLOW_FILE_UPLOAD_LIMIT: ${WORKFLOW_FILE_UPLOAD_LIMIT:-10}
  LOG_LEVEL: ${LOG_LEVEL:-INFO}
  LOG_FILE: ${LOG_FILE:-/var/log/dify_server.log}
  LOG_FILE_MAX_SIZE: ${LOG_FILE_MAX_SIZE:-20}
  LOG_FILE_BACKUP_COUNT: ${LOG_FILE_BACKUP_COUNT:-5}
  # Log dateformat
  LOG_DATEFORMAT: ${LOG_DATEFORMAT:-%Y-%m-%d %H:%M:%S}
  # Log Timezone
  LOG_TZ: ${LOG_TZ:-UTC}
  DEBUG: ${DEBUG:-false}
  FLASK_DEBUG: ${FLASK_DEBUG:-false}
  SECRET_KEY: ${SECRET_KEY:-sk-9f73s3ljTXVcMT3Blb3ljTqtsKiGHXVcMT3BlbkFJLK7U}
  INIT_PASSWORD: ${INIT_PASSWORD:-}
  CONSOLE_WEB_URL: ${CONSOLE_WEB_URL:-}
  CONSOLE_API_URL: ${CONSOLE_API_URL:-}
  SERVICE_API_URL: ${SERVICE_API_URL:-}
  APP_WEB_URL: ${APP_WEB_URL:-}
  CHECK_UPDATE_URL: ${CHECK_UPDATE_URL:-https://updates.dify.ai}
  OPENAI_API_BASE: ${OPENAI_API_BASE:-https://api.openai.com/v1}
  FILES_URL: ${FILES_URL:-}
  FILES_ACCESS_TIMEOUT: ${FILES_ACCESS_TIMEOUT:-300}
  APP_MAX_ACTIVE_REQUESTS: ${APP_MAX_ACTIVE_REQUESTS:-0}
  MIGRATION_ENABLED: ${MIGRATION_ENABLED:-true}
  DEPLOY_ENV: ${DEPLOY_ENV:-PRODUCTION}
  DIFY_BIND_ADDRESS: ${DIFY_BIND_ADDRESS:-0.0.0.0}
  DIFY_PORT: ${DIFY_PORT:-5001}
  SERVER_WORKER_AMOUNT: ${SERVER_WORKER_AMOUNT:-}
  SERVER_WORKER_CLASS: ${SERVER_WORKER_CLASS:-}
  CELERY_WORKER_CLASS: ${CELERY_WORKER_CLASS:-}
  GUNICORN_TIMEOUT: ${GUNICORN_TIMEOUT:-360}
  CELERY_WORKER_AMOUNT: ${CELERY_WORKER_AMOUNT:-}
  CELERY_AUTO_SCALE: ${CELERY_AUTO_SCALE:-false}
  CELERY_MAX_WORKERS: ${CELERY_MAX_WORKERS:-}
  CELERY_MIN_WORKERS: ${CELERY_MIN_WORKERS:-}
  API_TOOL_DEFAULT_CONNECT_TIMEOUT: ${API_TOOL_DEFAULT_CONNECT_TIMEOUT:-10}
  API_TOOL_DEFAULT_READ_TIMEOUT: ${API_TOOL_DEFAULT_READ_TIMEOUT:-60}
  DB_USERNAME: ${DB_USERNAME:-postgres}
  DB_PASSWORD: ${DB_PASSWORD:-difyai123456}
  DB_HOST: ${DB_HOST:-db}
  DB_PORT: ${DB_PORT:-5432}
  DB_DATABASE: ${DB_DATABASE:-dify}
  SQLALCHEMY_POOL_SIZE: ${SQLALCHEMY_POOL_SIZE:-30}
  SQLALCHEMY_POOL_RECYCLE: ${SQLALCHEMY_POOL_RECYCLE:-3600}
  SQLALCHEMY_ECHO: ${SQLALCHEMY_ECHO:-false}
  REDIS_HOST: ${REDIS_HOST:-redis}
  REDIS_PORT: ${REDIS_PORT:-6379}
  REDIS_USERNAME: ${REDIS_USERNAME:-}
  REDIS_PASSWORD: ${REDIS_PASSWORD:-difyai123456}
  REDIS_USE_SSL: ${REDIS_USE_SSL:-false}
  REDIS_DB: ${REDIS_DB:-0}
  REDIS_USE_SENTINEL: ${REDIS_USE_SENTINEL:-false}
  REDIS_SENTINELS: ${REDIS_SENTINELS:-}
  REDIS_SENTINEL_SERVICE_NAME: ${REDIS_SENTINEL_SERVICE_NAME:-}
  REDIS_SENTINEL_USERNAME: ${REDIS_SENTINEL_USERNAME:-}
  REDIS_SENTINEL_PASSWORD: ${REDIS_SENTINEL_PASSWORD:-}
  REDIS_SENTINEL_SOCKET_TIMEOUT: ${REDIS_SENTINEL_SOCKET_TIMEOUT:-0.1}
  ACCESS_TOKEN_EXPIRE_MINUTES: ${ACCESS_TOKEN_EXPIRE_MINUTES:-60}
  CELERY_BROKER_URL: ${CELERY_BROKER_URL:-redis://:difyai123456@redis:6379/1}
  BROKER_USE_SSL: ${BROKER_USE_SSL:-false}
  CELERY_USE_SENTINEL: ${CELERY_USE_SENTINEL:-false}
  CELERY_SENTINEL_MASTER_NAME: ${CELERY_SENTINEL_MASTER_NAME:-}
  CELERY_SENTINEL_SOCKET_TIMEOUT: ${CELERY_SENTINEL_SOCKET_TIMEOUT:-0.1}
  WEB_API_CORS_ALLOW_ORIGINS: ${WEB_API_CORS_ALLOW_ORIGINS:-*}
  CONSOLE_CORS_ALLOW_ORIGINS: ${CONSOLE_CORS_ALLOW_ORIGINS:-*}
  STORAGE_TYPE: ${STORAGE_TYPE:-local}
  STORAGE_LOCAL_PATH: ${STORAGE_LOCAL_PATH:-storage}
  S3_USE_AWS_MANAGED_IAM: ${S3_USE_AWS_MANAGED_IAM:-false}
  S3_ENDPOINT: ${S3_ENDPOINT:-}
  S3_BUCKET_NAME: ${S3_BUCKET_NAME:-}
  S3_ACCESS_KEY: ${S3_ACCESS_KEY:-}
  S3_SECRET_KEY: ${S3_SECRET_KEY:-}
  S3_REGION: ${S3_REGION:-us-east-1}
  AZURE_BLOB_ACCOUNT_NAME: ${AZURE_BLOB_ACCOUNT_NAME:-}
  AZURE_BLOB_ACCOUNT_KEY: ${AZURE_BLOB_ACCOUNT_KEY:-}
  AZURE_BLOB_CONTAINER_NAME: ${AZURE_BLOB_CONTAINER_NAME:-}
  AZURE_BLOB_ACCOUNT_URL: ${AZURE_BLOB_ACCOUNT_URL:-}
  GOOGLE_STORAGE_BUCKET_NAME: ${GOOGLE_STORAGE_BUCKET_NAME:-}
  GOOGLE_STORAGE_SERVICE_ACCOUNT_JSON_BASE64: ${GOOGLE_STORAGE_SERVICE_ACCOUNT_JSON_BASE64:-}
  ALIYUN_OSS_BUCKET_NAME: ${ALIYUN_OSS_BUCKET_NAME:-}
  ALIYUN_OSS_ACCESS_KEY: ${ALIYUN_OSS_ACCESS_KEY:-}
  ALIYUN_OSS_SECRET_KEY: ${ALIYUN_OSS_SECRET_KEY:-}
  ALIYUN_OSS_ENDPOINT: ${ALIYUN_OSS_ENDPOINT:-}
  ALIYUN_OSS_REGION: ${ALIYUN_OSS_REGION:-}
  ALIYUN_OSS_AUTH_VERSION: ${ALIYUN_OSS_AUTH_VERSION:-v4}
  ALIYUN_OSS_PATH: ${ALIYUN_OSS_PATH:-}
  TENCENT_COS_BUCKET_NAME: ${TENCENT_COS_BUCKET_NAME:-}
  TENCENT_COS_SECRET_KEY: ${TENCENT_COS_SECRET_KEY:-}
  TENCENT_COS_SECRET_ID: ${TENCENT_COS_SECRET_ID:-}
  TENCENT_COS_REGION: ${TENCENT_COS_REGION:-}
  TENCENT_COS_SCHEME: ${TENCENT_COS_SCHEME:-}
  HUAWEI_OBS_BUCKET_NAME: ${HUAWEI_OBS_BUCKET_NAME:-}
  HUAWEI_OBS_SECRET_KEY: ${HUAWEI_OBS_SECRET_KEY:-}
  HUAWEI_OBS_ACCESS_KEY: ${HUAWEI_OBS_ACCESS_KEY:-}
  HUAWEI_OBS_SERVER: ${HUAWEI_OBS_SERVER:-}
  OCI_ENDPOINT: ${OCI_ENDPOINT:-}
  OCI_BUCKET_NAME: ${OCI_BUCKET_NAME:-}
  OCI_ACCESS_KEY: ${OCI_ACCESS_KEY:-}
  OCI_SECRET_KEY: ${OCI_SECRET_KEY:-}
  OCI_REGION: ${OCI_REGION:-}
  VOLCENGINE_TOS_BUCKET_NAME: ${VOLCENGINE_TOS_BUCKET_NAME:-}
  VOLCENGINE_TOS_SECRET_KEY: ${VOLCENGINE_TOS_SECRET_KEY:-}
  VOLCENGINE_TOS_ACCESS_KEY: ${VOLCENGINE_TOS_ACCESS_KEY:-}
  VOLCENGINE_TOS_ENDPOINT: ${VOLCENGINE_TOS_ENDPOINT:-}
  VOLCENGINE_TOS_REGION: ${VOLCENGINE_TOS_REGION:-}
  BAIDU_OBS_BUCKET_NAME: ${BAIDU_OBS_BUCKET_NAME:-}
  BAIDU_OBS_SECRET_KEY: ${BAIDU_OBS_SECRET_KEY:-}
  BAIDU_OBS_ACCESS_KEY: ${BAIDU_OBS_ACCESS_KEY:-}
  BAIDU_OBS_ENDPOINT: ${BAIDU_OBS_ENDPOINT:-}
  VECTOR_STORE: ${VECTOR_STORE:-weaviate}
  WEAVIATE_ENDPOINT: ${WEAVIATE_ENDPOINT:-http://weaviate:8080}
  WEAVIATE_API_KEY: ${WEAVIATE_API_KEY:-WVF5YThaHlkYwhGUSmCRgsX3tD5ngdN8pkih}
  QDRANT_URL: ${QDRANT_URL:-http://qdrant:6333}
  QDRANT_API_KEY: ${QDRANT_API_KEY:-difyai123456}
  QDRANT_CLIENT_TIMEOUT: ${QDRANT_CLIENT_TIMEOUT:-20}
  QDRANT_GRPC_ENABLED: ${QDRANT_GRPC_ENABLED:-false}
  QDRANT_GRPC_PORT: ${QDRANT_GRPC_PORT:-6334}
  COUCHBASE_CONNECTION_STRING: ${COUCHBASE_CONNECTION_STRING:-'couchbase-server'}
  COUCHBASE_USER: ${COUCHBASE_USER:-Administrator}
  COUCHBASE_PASSWORD: ${COUCHBASE_PASSWORD:-password}
  COUCHBASE_BUCKET_NAME: ${COUCHBASE_BUCKET_NAME:-Embeddings}
  COUCHBASE_SCOPE_NAME: ${COUCHBASE_SCOPE_NAME:-_default}
  MILVUS_URI: ${MILVUS_URI:-http://127.0.0.1:19530}
  MILVUS_TOKEN: ${MILVUS_TOKEN:-}
  MILVUS_USER: ${MILVUS_USER:-root}
  MILVUS_PASSWORD: ${MILVUS_PASSWORD:-Milvus}
  MYSCALE_HOST: ${MYSCALE_HOST:-myscale}
  MYSCALE_PORT: ${MYSCALE_PORT:-8123}
  MYSCALE_USER: ${MYSCALE_USER:-default}
  MYSCALE_PASSWORD: ${MYSCALE_PASSWORD:-}
  MYSCALE_DATABASE: ${MYSCALE_DATABASE:-dify}
  MYSCALE_FTS_PARAMS: ${MYSCALE_FTS_PARAMS:-}
  RELYT_HOST: ${RELYT_HOST:-db}
  RELYT_PORT: ${RELYT_PORT:-5432}
  RELYT_USER: ${RELYT_USER:-postgres}
  RELYT_PASSWORD: ${RELYT_PASSWORD:-difyai123456}
  RELYT_DATABASE: ${RELYT_DATABASE:-postgres}
  PGVECTOR_HOST: ${PGVECTOR_HOST:-pgvector}
  PGVECTOR_PORT: ${PGVECTOR_PORT:-5432}
  PGVECTOR_USER: ${PGVECTOR_USER:-postgres}
  PGVECTOR_PASSWORD: ${PGVECTOR_PASSWORD:-difyai123456}
  PGVECTOR_DATABASE: ${PGVECTOR_DATABASE:-dify}
  TIDB_VECTOR_HOST: ${TIDB_VECTOR_HOST:-tidb}
  TIDB_VECTOR_PORT: ${TIDB_VECTOR_PORT:-4000}
  TIDB_VECTOR_USER: ${TIDB_VECTOR_USER:-}
  TIDB_VECTOR_PASSWORD: ${TIDB_VECTOR_PASSWORD:-}
  TIDB_VECTOR_DATABASE: ${TIDB_VECTOR_DATABASE:-dify}
  TIDB_ON_QDRANT_URL: ${TIDB_ON_QDRANT_URL:-http://127.0.0.1}
  TIDB_ON_QDRANT_API_KEY: ${TIDB_ON_QDRANT_API_KEY:-dify}
  TIDB_ON_QDRANT_CLIENT_TIMEOUT: ${TIDB_ON_QDRANT_CLIENT_TIMEOUT:-20}
  TIDB_ON_QDRANT_GRPC_ENABLED: ${TIDB_ON_QDRANT_GRPC_ENABLED:-false}
  TIDB_ON_QDRANT_GRPC_PORT: ${TIDB_ON_QDRANT_GRPC_PORT:-6334}
  TIDB_PUBLIC_KEY: ${TIDB_PUBLIC_KEY:-dify}
  TIDB_PRIVATE_KEY: ${TIDB_PRIVATE_KEY:-dify}
  TIDB_API_URL: ${TIDB_API_URL:-http://127.0.0.1}
  TIDB_IAM_API_URL: ${TIDB_IAM_API_URL:-http://127.0.0.1}
  TIDB_REGION: ${TIDB_REGION:-regions/aws-us-east-1}
  TIDB_PROJECT_ID: ${TIDB_PROJECT_ID:-dify}
  TIDB_SPEND_LIMIT: ${TIDB_SPEND_LIMIT:-100}
  ORACLE_HOST: ${ORACLE_HOST:-oracle}
  ORACLE_PORT: ${ORACLE_PORT:-1521}
  ORACLE_USER: ${ORACLE_USER:-dify}
  ORACLE_PASSWORD: ${ORACLE_PASSWORD:-dify}
  ORACLE_DATABASE: ${ORACLE_DATABASE:-FREEPDB1}
  CHROMA_HOST: ${CHROMA_HOST:-127.0.0.1}
  CHROMA_PORT: ${CHROMA_PORT:-8000}
  CHROMA_TENANT: ${CHROMA_TENANT:-default_tenant}
  CHROMA_DATABASE: ${CHROMA_DATABASE:-default_database}
  CHROMA_AUTH_PROVIDER: ${CHROMA_AUTH_PROVIDER:-chromadb.auth.token_authn.TokenAuthClientProvider}
  CHROMA_AUTH_CREDENTIALS: ${CHROMA_AUTH_CREDENTIALS:-}
  ELASTICSEARCH_HOST: ${ELASTICSEARCH_HOST:-0.0.0.0}
  ELASTICSEARCH_PORT: ${ELASTICSEARCH_PORT:-9200}
  ELASTICSEARCH_USERNAME: ${ELASTICSEARCH_USERNAME:-elastic}
  ELASTICSEARCH_PASSWORD: ${ELASTICSEARCH_PASSWORD:-elastic}
  LINDORM_URL: ${LINDORM_URL:-http://lindorm:30070}
  LINDORM_USERNAME: ${LINDORM_USERNAME:-lindorm}
  LINDORM_PASSWORD: ${LINDORM_USERNAME:-lindorm }
  KIBANA_PORT: ${KIBANA_PORT:-5601}
  # AnalyticDB configuration
  ANALYTICDB_KEY_ID: ${ANALYTICDB_KEY_ID:-}
  ANALYTICDB_KEY_SECRET: ${ANALYTICDB_KEY_SECRET:-}
  ANALYTICDB_REGION_ID: ${ANALYTICDB_REGION_ID:-}
  ANALYTICDB_INSTANCE_ID: ${ANALYTICDB_INSTANCE_ID:-}
  ANALYTICDB_ACCOUNT: ${ANALYTICDB_ACCOUNT:-}
  ANALYTICDB_PASSWORD: ${ANALYTICDB_PASSWORD:-}
  ANALYTICDB_NAMESPACE: ${ANALYTICDB_NAMESPACE:-dify}
  ANALYTICDB_NAMESPACE_PASSWORD: ${ANALYTICDB_NAMESPACE_PASSWORD:-}
  OPENSEARCH_HOST: ${OPENSEARCH_HOST:-opensearch}
  OPENSEARCH_PORT: ${OPENSEARCH_PORT:-9200}
  OPENSEARCH_USER: ${OPENSEARCH_USER:-admin}
  OPENSEARCH_PASSWORD: ${OPENSEARCH_PASSWORD:-admin}
  OPENSEARCH_SECURE: ${OPENSEARCH_SECURE:-true}
  TENCENT_VECTOR_DB_URL: ${TENCENT_VECTOR_DB_URL:-http://127.0.0.1}
  TENCENT_VECTOR_DB_API_KEY: ${TENCENT_VECTOR_DB_API_KEY:-dify}
  TENCENT_VECTOR_DB_TIMEOUT: ${TENCENT_VECTOR_DB_TIMEOUT:-30}
  TENCENT_VECTOR_DB_USERNAME: ${TENCENT_VECTOR_DB_USERNAME:-dify}
  TENCENT_VECTOR_DB_DATABASE: ${TENCENT_VECTOR_DB_DATABASE:-dify}
  TENCENT_VECTOR_DB_SHARD: ${TENCENT_VECTOR_DB_SHARD:-1}
  TENCENT_VECTOR_DB_REPLICAS: ${TENCENT_VECTOR_DB_REPLICAS:-2}
  BAIDU_VECTOR_DB_ENDPOINT: ${BAIDU_VECTOR_DB_ENDPOINT:-http://127.0.0.1:5287}
  BAIDU_VECTOR_DB_CONNECTION_TIMEOUT_MS: ${BAIDU_VECTOR_DB_CONNECTION_TIMEOUT_MS:-30000}
  BAIDU_VECTOR_DB_ACCOUNT: ${BAIDU_VECTOR_DB_ACCOUNT:-root}
  BAIDU_VECTOR_DB_API_KEY: ${BAIDU_VECTOR_DB_API_KEY:-dify}
  BAIDU_VECTOR_DB_DATABASE: ${BAIDU_VECTOR_DB_DATABASE:-dify}
  BAIDU_VECTOR_DB_SHARD: ${BAIDU_VECTOR_DB_SHARD:-1}
  BAIDU_VECTOR_DB_REPLICAS: ${BAIDU_VECTOR_DB_REPLICAS:-3}
  VIKINGDB_ACCESS_KEY: ${VIKINGDB_ACCESS_KEY:-dify}
  VIKINGDB_SECRET_KEY: ${VIKINGDB_SECRET_KEY:-dify}
  VIKINGDB_REGION: ${VIKINGDB_REGION:-cn-shanghai}
  VIKINGDB_HOST: ${VIKINGDB_HOST:-api-vikingdb.xxx.volces.com}
  VIKINGDB_SCHEMA: ${VIKINGDB_SCHEMA:-http}
  UPSTASH_VECTOR_URL: ${UPSTASH_VECTOR_URL:-https://xxx-vector.upstash.io}
  UPSTASH_VECTOR_TOKEN: ${UPSTASH_VECTOR_TOKEN:-dify}
  UPLOAD_FILE_SIZE_LIMIT: ${UPLOAD_FILE_SIZE_LIMIT:-15}
  UPLOAD_FILE_BATCH_LIMIT: ${UPLOAD_FILE_BATCH_LIMIT:-5}
  ETL_TYPE: ${ETL_TYPE:-dify}
  UNSTRUCTURED_API_URL: ${UNSTRUCTURED_API_URL:-}
  PROMPT_GENERATION_MAX_TOKENS: ${PROMPT_GENERATION_MAX_TOKENS:-512}
  CODE_GENERATION_MAX_TOKENS: ${CODE_GENERATION_MAX_TOKENS:-1024}
  MULTIMODAL_SEND_IMAGE_FORMAT: ${MULTIMODAL_SEND_IMAGE_FORMAT:-base64}
  MULTIMODAL_SEND_VIDEO_FORMAT: ${MULTIMODAL_SEND_VIDEO_FORMAT:-base64}
  UPLOAD_IMAGE_FILE_SIZE_LIMIT: ${UPLOAD_IMAGE_FILE_SIZE_LIMIT:-10}
  UPLOAD_VIDEO_FILE_SIZE_LIMIT: ${UPLOAD_VIDEO_FILE_SIZE_LIMIT:-100}
  UPLOAD_AUDIO_FILE_SIZE_LIMIT: ${UPLOAD_AUDIO_FILE_SIZE_LIMIT:-50}
  SENTRY_DSN: ${API_SENTRY_DSN:-}
  SENTRY_TRACES_SAMPLE_RATE: ${API_SENTRY_TRACES_SAMPLE_RATE:-1.0}
  SENTRY_PROFILES_SAMPLE_RATE: ${API_SENTRY_PROFILES_SAMPLE_RATE:-1.0}
  NOTION_INTEGRATION_TYPE: ${NOTION_INTEGRATION_TYPE:-public}
  NOTION_CLIENT_SECRET: ${NOTION_CLIENT_SECRET:-}
  NOTION_CLIENT_ID: ${NOTION_CLIENT_ID:-}
  NOTION_INTERNAL_SECRET: ${NOTION_INTERNAL_SECRET:-}
  MAIL_TYPE: ${MAIL_TYPE:-resend}
  MAIL_DEFAULT_SEND_FROM: ${MAIL_DEFAULT_SEND_FROM:-}
  SMTP_SERVER: ${SMTP_SERVER:-}
  SMTP_PORT: ${SMTP_PORT:-465}
  SMTP_USERNAME: ${SMTP_USERNAME:-}
  SMTP_PASSWORD: ${SMTP_PASSWORD:-}
  SMTP_USE_TLS: ${SMTP_USE_TLS:-true}
  SMTP_OPPORTUNISTIC_TLS: ${SMTP_OPPORTUNISTIC_TLS:-false}
  RESEND_API_KEY: ${RESEND_API_KEY:-your-resend-api-key}
  RESEND_API_URL: ${RESEND_API_URL:-https://api.resend.com}
  INDEXING_MAX_SEGMENTATION_TOKENS_LENGTH: ${INDEXING_MAX_SEGMENTATION_TOKENS_LENGTH:-1000}
  INVITE_EXPIRY_HOURS: ${INVITE_EXPIRY_HOURS:-72}
  RESET_PASSWORD_TOKEN_EXPIRY_MINUTES: ${RESET_PASSWORD_TOKEN_EXPIRY_MINUTES:-5}
  CODE_EXECUTION_ENDPOINT: ${CODE_EXECUTION_ENDPOINT:-http://sandbox:8194}
  CODE_EXECUTION_API_KEY: ${SANDBOX_API_KEY:-dify-sandbox}
  CODE_MAX_NUMBER: ${CODE_MAX_NUMBER:-9223372036854775807}
  CODE_MIN_NUMBER: ${CODE_MIN_NUMBER:--9223372036854775808}
  CODE_MAX_DEPTH: ${CODE_MAX_DEPTH:-5}
  CODE_MAX_PRECISION: ${CODE_MAX_PRECISION:-20}
  CODE_MAX_STRING_LENGTH: ${CODE_MAX_STRING_LENGTH:-80000}
  TEMPLATE_TRANSFORM_MAX_LENGTH: ${TEMPLATE_TRANSFORM_MAX_LENGTH:-80000}
  CODE_MAX_STRING_ARRAY_LENGTH: ${CODE_MAX_STRING_ARRAY_LENGTH:-30}
  CODE_MAX_OBJECT_ARRAY_LENGTH: ${CODE_MAX_OBJECT_ARRAY_LENGTH:-30}
  CODE_MAX_NUMBER_ARRAY_LENGTH: ${CODE_MAX_NUMBER_ARRAY_LENGTH:-1000}
  WORKFLOW_MAX_EXECUTION_STEPS: ${WORKFLOW_MAX_EXECUTION_STEPS:-500}
  WORKFLOW_MAX_EXECUTION_TIME: ${WORKFLOW_MAX_EXECUTION_TIME:-1200}
  WORKFLOW_CALL_MAX_DEPTH: ${WORKFLOW_CALL_MAX_DEPTH:-5}
  SSRF_PROXY_HTTP_URL: ${SSRF_PROXY_HTTP_URL:-http://ssrf_proxy:3128}
  SSRF_PROXY_HTTPS_URL: ${SSRF_PROXY_HTTPS_URL:-http://ssrf_proxy:3128}
  HTTP_REQUEST_NODE_MAX_BINARY_SIZE: ${HTTP_REQUEST_NODE_MAX_BINARY_SIZE:-10485760}
  HTTP_REQUEST_NODE_MAX_TEXT_SIZE: ${HTTP_REQUEST_NODE_MAX_TEXT_SIZE:-1048576}
  APP_MAX_EXECUTION_TIME: ${APP_MAX_EXECUTION_TIME:-12000}
  POSITION_TOOL_PINS: ${POSITION_TOOL_PINS:-}
  POSITION_TOOL_INCLUDES: ${POSITION_TOOL_INCLUDES:-}
  POSITION_TOOL_EXCLUDES: ${POSITION_TOOL_EXCLUDES:-}
  POSITION_PROVIDER_PINS: ${POSITION_PROVIDER_PINS:-}
  POSITION_PROVIDER_INCLUDES: ${POSITION_PROVIDER_INCLUDES:-}
  POSITION_PROVIDER_EXCLUDES: ${POSITION_PROVIDER_EXCLUDES:-}
  MAX_VARIABLE_SIZE: ${MAX_VARIABLE_SIZE:-204800}
  OCEANBASE_VECTOR_HOST: ${OCEANBASE_VECTOR_HOST:-http://oceanbase-vector}
  OCEANBASE_VECTOR_PORT: ${OCEANBASE_VECTOR_PORT:-2881}
  OCEANBASE_VECTOR_USER: ${OCEANBASE_VECTOR_USER:-root@test}
  OCEANBASE_VECTOR_PASSWORD: ${OCEANBASE_VECTOR_PASSWORD:-difyai123456}
  OCEANBASE_VECTOR_DATABASE: ${OCEANBASE_VECTOR_DATABASE:-test}
  OCEANBASE_CLUSTER_NAME: ${OCEANBASE_CLUSTER_NAME:-difyai}
  OCEANBASE_MEMORY_LIMIT: ${OCEANBASE_MEMORY_LIMIT:-6G}
  CREATE_TIDB_SERVICE_JOB_ENABLED: ${CREATE_TIDB_SERVICE_JOB_ENABLED:-false}

services:
  # API service
  api:
    image: langgenius/dify-api:0.11.1-arm
    restart: always
    privileged: true
    environment:
      # Use the shared environment variables.
      <<: *shared-api-worker-env
      # Startup mode, 'api' starts the API server.
      MODE: api
    depends_on:
      - db
      - redis
    volumes:
      # Mount the storage directory to the container, for storing user files.
      - ./volumes/app/storage:/app/api/storage
    networks:
      - default
      - ssrf_proxy_network

  # worker service
  # The Celery worker for processing the queue.
  worker:
    image: langgenius/dify-api:0.11.1-arm
    restart: always
    privileged: true
    environment:
      # Use the shared environment variables.
      <<: *shared-api-worker-env
      # Startup mode, 'worker' starts the Celery worker for processing the queue.
      MODE: worker
    depends_on:
      - db
      - redis
    volumes:
      # Mount the storage directory to the container, for storing user files.
      - ./volumes/app/storage:/app/api/storage
    networks:
      - default

  # Frontend web application.
  web:
    image: langgenius/dify-web:0.11.1
    restart: always
    environment:
      CONSOLE_API_URL: ${CONSOLE_API_URL:-}
      APP_API_URL: ${APP_API_URL:-}
      SENTRY_DSN: ${WEB_SENTRY_DSN:-}
      NEXT_TELEMETRY_DISABLED: ${NEXT_TELEMETRY_DISABLED:-0}
      TEXT_GENERATION_TIMEOUT_MS: ${TEXT_GENERATION_TIMEOUT_MS:-60000}
      CSP_WHITELIST: ${CSP_WHITELIST:-}

  # The postgres database.
  db:
    image: postgres:15-alpine
    restart: always
    environment:
      PGUSER: ${PGUSER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-difyai123456}
      POSTGRES_DB: ${POSTGRES_DB:-dify}
      PGDATA: ${PGDATA:-/var/lib/postgresql/data/pgdata}
    command: >
      postgres -c 'max_connections=${POSTGRES_MAX_CONNECTIONS:-100}'
               -c 'shared_buffers=${POSTGRES_SHARED_BUFFERS:-128MB}'
               -c 'work_mem=${POSTGRES_WORK_MEM:-4MB}'
               -c 'maintenance_work_mem=${POSTGRES_MAINTENANCE_WORK_MEM:-64MB}'
               -c 'effective_cache_size=${POSTGRES_EFFECTIVE_CACHE_SIZE:-4096MB}'
    volumes:
      - ./volumes/db/data:/var/lib/postgresql/data
    healthcheck:
      test: ['CMD', 'pg_isready']
      interval: 1s
      timeout: 3s
      retries: 30

  # The redis cache.
  redis:
    image: redis:6-alpine
    restart: always
    volumes:
      # Mount the redis data directory to the container.
      - ./volumes/redis/data:/data
    # Set the redis password when startup redis server.
    command: redis-server --requirepass ${REDIS_PASSWORD:-difyai123456}
    healthcheck:
      test: ['CMD', 'redis-cli', 'ping']

  # The DifySandbox
  sandbox:
    image: langgenius/dify-sandbox:0.2.10
    restart: always
    privileged: true
    environment:
      # The DifySandbox configurations
      # Make sure you are changing this key for your deployment with a strong key.
      # You can generate a strong key using `openssl rand -base64 42`.
      API_KEY: ${SANDBOX_API_KEY:-dify-sandbox}
      GIN_MODE: ${SANDBOX_GIN_MODE:-release}
      WORKER_TIMEOUT: ${SANDBOX_WORKER_TIMEOUT:-15}
      ENABLE_NETWORK: ${SANDBOX_ENABLE_NETWORK:-true}
      HTTP_PROXY: ${SANDBOX_HTTP_PROXY:-http://ssrf_proxy:3128}
      HTTPS_PROXY: ${SANDBOX_HTTPS_PROXY:-http://ssrf_proxy:3128}
      SANDBOX_PORT: ${SANDBOX_PORT:-8194}
    volumes:
      - ./volumes/sandbox/dependencies:/dependencies
    healthcheck:
      test: ['CMD', 'curl', '-f', 'http://localhost:8194/health']
    networks:
      - ssrf_proxy_network

  # The nginx reverse proxy.
  # used for reverse proxying the API service and Web service.
  nginx:
    image: nginx:1.27.2
    restart: always
    volumes:
      - ./nginx/nginx.conf.template:/etc/nginx/nginx.conf.template
      - ./nginx/proxy.conf.template:/etc/nginx/proxy.conf.template
      - ./nginx/https.conf.template:/etc/nginx/https.conf.template
      - ./nginx/conf.d:/etc/nginx/conf.d
      - ./nginx/docker-entrypoint.sh:/docker-entrypoint-mount.sh
      - ./nginx/ssl:/etc/ssl # cert dir (legacy)
      - ./volumes/certbot/conf/live:/etc/letsencrypt/live # cert dir (with certbot container)
      - ./volumes/certbot/conf:/etc/letsencrypt
      - ./volumes/certbot/www:/var/www/html
    entrypoint:
      [
        'sh',
        '-c',
        "cp /docker-entrypoint-mount.sh /docker-entrypoint.sh && sed -i 's/\r$$//' /docker-entrypoint.sh && chmod +x /docker-entrypoint.sh && /docker-entrypoint.sh",
      ]
    environment:
      NGINX_SERVER_NAME: ${NGINX_SERVER_NAME:-_}
      NGINX_HTTPS_ENABLED: ${NGINX_HTTPS_ENABLED:-false}
      NGINX_SSL_PORT: ${NGINX_SSL_PORT:-443}
      NGINX_PORT: ${NGINX_PORT:-80}
      # You're required to add your own SSL certificates/keys to the `./nginx/ssl` directory
      # and modify the env vars below in .env if HTTPS_ENABLED is true.
      NGINX_SSL_CERT_FILENAME: ${NGINX_SSL_CERT_FILENAME:-dify.crt}
      NGINX_SSL_CERT_KEY_FILENAME: ${NGINX_SSL_CERT_KEY_FILENAME:-dify.key}
      NGINX_SSL_PROTOCOLS: ${NGINX_SSL_PROTOCOLS:-TLSv1.1 TLSv1.2 TLSv1.3}
      NGINX_WORKER_PROCESSES: ${NGINX_WORKER_PROCESSES:-auto}
      NGINX_CLIENT_MAX_BODY_SIZE: ${NGINX_CLIENT_MAX_BODY_SIZE:-15M}
      NGINX_KEEPALIVE_TIMEOUT: ${NGINX_KEEPALIVE_TIMEOUT:-65}
      NGINX_PROXY_READ_TIMEOUT: ${NGINX_PROXY_READ_TIMEOUT:-3600s}
      NGINX_PROXY_SEND_TIMEOUT: ${NGINX_PROXY_SEND_TIMEOUT:-3600s}
      NGINX_ENABLE_CERTBOT_CHALLENGE: ${NGINX_ENABLE_CERTBOT_CHALLENGE:-false}
      CERTBOT_DOMAIN: ${CERTBOT_DOMAIN:-}
    depends_on:
      - api
      - web
    ports:
      - '${EXPOSE_NGINX_PORT:-80}:${NGINX_PORT:-80}'
      - '${EXPOSE_NGINX_SSL_PORT:-443}:${NGINX_SSL_PORT:-443}'

  # The Weaviate vector store.
  weaviate:
    image: semitechnologies/weaviate:1.19.0
    profiles:
      - ''
      - weaviate
    restart: always
    volumes:
      # Mount the Weaviate data directory to the con tainer.
      - ./volumes/weaviate:/var/lib/weaviate
    environment:
      # The Weaviate configurations
      # You can refer to the [Weaviate](https://weaviate.io/developers/weaviate/config-refs/env-vars) documentation for more information.
      PERSISTENCE_DATA_PATH: ${WEAVIATE_PERSISTENCE_DATA_PATH:-/var/lib/weaviate}
      QUERY_DEFAULTS_LIMIT: ${WEAVIATE_QUERY_DEFAULTS_LIMIT:-25}
      AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: ${WEAVIATE_AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED:-false}
      DEFAULT_VECTORIZER_MODULE: ${WEAVIATE_DEFAULT_VECTORIZER_MODULE:-none}
      CLUSTER_HOSTNAME: ${WEAVIATE_CLUSTER_HOSTNAME:-node1}
      AUTHENTICATION_APIKEY_ENABLED: ${WEAVIATE_AUTHENTICATION_APIKEY_ENABLED:-true}
      AUTHENTICATION_APIKEY_ALLOWED_KEYS: ${WEAVIATE_AUTHENTICATION_APIKEY_ALLOWED_KEYS:-WVF5YThaHlkYwhGUSmCRgsX3tD5ngdN8pkih}
      AUTHENTICATION_APIKEY_USERS: ${WEAVIATE_AUTHENTICATION_APIKEY_USERS:-hello@dify.ai}
      AUTHORIZATION_ADMINLIST_ENABLED: ${WEAVIATE_AUTHORIZATION_ADMINLIST_ENABLED:-true}
      AUTHORIZATION_ADMINLIST_USERS: ${WEAVIATE_AUTHORIZATION_ADMINLIST_USERS:-hello@dify.ai}

networks:
  # create a network between sandbox, api and ssrf_proxy, and can not access outside.
  ssrf_proxy_network:
    driver: bridge
    internal: true
```

# 启动服务

启动时，将上面精简过的 `streamline.yaml` 放在 https://github.com/langgenius/dify/tree/main/docker 目录中，并在此目录执行 `docker compose -f streamline.yaml up -d`。

等待并检查容器是否均正常启动。

# 验证对话

访问 http://localhost 登录 Dify 并配置模型后，可创建一个聊天助手，验证基本对话功能：

![](/contents/covers/dify-in-arm.png)