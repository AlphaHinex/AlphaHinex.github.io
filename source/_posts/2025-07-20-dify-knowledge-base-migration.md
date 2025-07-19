---
id: dify-knowledge-base-migration
title: "Dify 知识库迁移"
description: "迁移单个知识库的参考方案，不同 Dify 版本表结构可能略有差异"
date: 2025.07.20 10:26
categories:
    - AI
    - Database
tags: [Dify, Database]
keywords: Dify, Knowledge Base, migration, postgre, pg, PostgreSQL, SQL, weaviate, vector, Vector DB
cover: /contents/covers/dify-knowledge-base-migration.png
---

# Dify 知识库迁移

迁移 Dify 中单个知识库的参考方案，不同 Dify 版本表结构可能略有差异。

## 从源数据库中获取知识库及租户 ID

```python
# 待迁移的知识库 id
dataset_id = 'xxxxxx'

# 源数据库租户
# select tenant_id, created_by, embedding_model_provider, embedding_model from datasets where id='{dataset_id}';
source_tenant_id = 'xxxxxx'
```

## 源数据库需导出的数据

通过 sql 生成 insert 语句，在目标数据库中执行。

```python
source_data_sql = f'''
-- 知识库
select * from datasets where id='{dataset_id}';
-- select tenant_id, created_by, embedding_model_provider, embedding_model from datasets where id='{dataset_id}';

select * from dataset_permissions where id='{dataset_id}';

select * from external_knowledge_bindings where id='{dataset_id}';

select * from external_knowledge_apis where id=(select external_knowledge_api_id from external_knowledge_bindings where dataset_id='{dataset_id}');

select * from dataset_collection_bindings where id=(select collection_binding_id from datasets where id='{dataset_id}');

-- 文档
select * from documents where dataset_id='{dataset_id}';

select * from dataset_process_rules where dataset_id='{dataset_id}';

-- 文件路径带租户信息
select * from upload_files where id::text=(select data_source_info::json->>'upload_file_id' from documents where dataset_id='{dataset_id}');

-- 文档分段
select * from document_segments where dataset_id='{dataset_id}';

select * from embeddings where hash in (select index_node_hash from document_segments where dataset_id='{dataset_id}');

select * from dataset_keyword_tables where dataset_id='{dataset_id}';

select * from child_chunks where dataset_id='{dataset_id}';

-- select * from dataset_auto_disable_logs where dataset_id='{dataset_id}';
-- select * from dataset_queries where dataset_id='{dataset_id}';
-- select * form dataset_retriever_resources where dataset_id='{dataset_id}';
-- select * from dataset_metadatas where dataset_id='{dataset_id}';
-- select * form dataset_metadata_bindings where dataset_id='{dataset_id}';
'''
print(source_data_sql)
```

## 导入后根据目标库中租户、嵌入模型等更新数据

```python
# 目标数据库租户
# select tenant_id, created_by, embedding_model_provider, embedding_model from datasets;
target_tenant_id = 'xxxxxx'

# 目标数据库创建人
target_created_by = 'xxxxxx'

# 目标数据库嵌入模型
target_embedding_model_provider = 'xxxxxx'
target_embedding_model_name = 'xxxxxx'
```

```python
target_update_sql = f'''
update datasets set tenant_id='{target_tenant_id}', created_by='{target_created_by}', embedding_model='{target_embedding_model_name}', embedding_model_provider='{target_embedding_model_provider}' where id='{dataset_id}';

update dataset_permissions set tenant_id='{target_tenant_id}' where id='{dataset_id}';

update external_knowledge_bindings set tenant_id='{target_tenant_id}', created_by='{target_created_by}' where id='{dataset_id}';

update external_knowledge_apis set tenant_id='{target_tenant_id}', created_by='{target_created_by}', updated_by='{target_created_by}' where id=(select external_knowledge_api_id from external_knowledge_bindings where dataset_id='{dataset_id}');

update dataset_collection_bindings set model_name='{target_embedding_model_name}', provider_name='{target_embedding_model_provider}' where id=(select collection_binding_id from datasets where id='{dataset_id}');

update documents set tenant_id='{target_tenant_id}', created_by='{target_created_by}' where dataset_id='{dataset_id}';

update dataset_process_rules set created_by='{target_created_by}' where dataset_id='{dataset_id}';

update upload_files set tenant_id='{target_tenant_id}', created_by='{target_created_by}', key=REPLACE(key, '{source_tenant_id}', '{target_tenant_id}') where id::text=(select data_source_info::json->>'upload_file_id' from documents where dataset_id='{dataset_id}');

update document_segments set tenant_id='{target_tenant_id}', created_by='{target_created_by}' where dataset_id='{dataset_id}';

update embeddings set model_name='{target_embedding_model_name}', provider_name='{target_embedding_model_provider}' where hash in (select index_node_hash from document_segments where dataset_id='{dataset_id}');

update child_chunks set tenant_id='{target_tenant_id}', created_by='{target_created_by}' where dataset_id='{dataset_id}';

-- update dataset_auto_disable_logs set tenant_id='{target_tenant_id}' where dataset_id='{dataset_id}';
-- update dataset_queries set created_by='{target_created_by}' where dataset_id='{dataset_id}';
-- update dataset_retriever_resources set created_by='{target_created_by}' where dataset_id='{dataset_id}';
-- update dataset_metadatas set tenant_id='{target_tenant_id}',  created_by='{target_created_by}' where dataset_id='{dataset_id}';
-- update dataset_metadata_bindings set tenant_id='{target_tenant_id}',  created_by='{target_created_by}' where dataset_id='{dataset_id}';
'''
print(target_update_sql)
```

## 文档迁移

将上传到知识库中的源文件，从源环境的文件系统迁移至目标环境的文件系统。源文件和目标文件路径可从下面 SQL 中获得。

源文件也可通过 Dify 知识库接口获取：

```bash
curl --request GET \
  --url http://host:port/v1/datasets/{dataset_id}/documents/{document_id}/upload-file \
  --header 'authorization: Bearer {dataset-api-key}'
```

```python
file_sql = f'''
-- 分别在源环境和目标环境库中执行，获得源文件路径和目标文件路径
select '/app/api/storage/' || key from upload_files where id::text=(select data_source_info::json->>'upload_file_id' from documents where dataset_id='{dataset_id}');
'''
print(file_sql)
```

## 更新向量库

因 Dify 可使用不同类型的向量库，且向量库迁移方式不同，可在完成数据迁移后，在 Dify 知识库界面中，将新迁移的知识库中文档进行禁用后再启用操作，使 Dify 自动完成向量库的同步更新（分段和嵌入向量均存储在数据库中）。等待所有文档及分段的状态恢复可用后，可通过召回测试验证迁移效果。

## 附：PostgreSQL 命令行操作

- 连接到 PostgreSQL 数据库：`psql -U <user> -d <database> -h <host> -p <port>`
- 列出所有数据库：`\l`
- 连接到指定数据库：`\c 数据库名`
- 列出当前库中所有表：`\d`