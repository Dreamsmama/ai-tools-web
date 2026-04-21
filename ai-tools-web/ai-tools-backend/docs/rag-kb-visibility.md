# RAG 知识库可见性逻辑说明

本文档用于说明当前系统中 `knowledge_bases` 的可见性与发布策略，便于后续运营和维护。

## 1. 关键字段

- `source_type`：知识库来源类型
  - `official`：官方库（可由运营控制是否对前台开放）
  - `user`：用户私有库（当前版本已不作为默认创建类型）
- `is_selectable`：是否可在前端知识库下拉中被选中
  - `true`：前端可选
  - `false`：前端不可选

## 2. 当前默认策略（已实现）

- 用户通过前端创建知识库时，默认写入：
  - `source_type = 'official'`
  - `is_selectable = false`
- 含义：
  - 新建库先作为“待发布库”存在
  - 不会自动对所有用户开放
  - 需后台手工改字段后才可被前端选中

## 3. 前端可见规则

`GET /rag/kbs` 返回满足以下条件的库：

- 当前作用域下所有 `source_type='user'` 的库
- 或 `source_type='official' AND is_selectable=true` 的库

> 由于当前默认创建已改为 `official + is_selectable=false`，因此新建库默认不会显示在前端下拉中。

## 4. 运营发布流程（推荐）

### 发布某个库为可选模板

```sql
UPDATE knowledge_bases
SET source_type = 'official',
    is_selectable = true
WHERE id = '<kb_id>';
```

### 下线某个可选模板

```sql
UPDATE knowledge_bases
SET is_selectable = false
WHERE id = '<kb_id>';
```

## 5. 注意事项

- 当前系统尚未接入真实用户体系，作用域依赖默认 `user_id/workspace_id`。
- 若后续接入 JWT/Session，需要将库归属与发布流程拆分为更细粒度权限模型。
