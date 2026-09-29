# MongoDB Schema

## users

```json
{
  "_id": "ObjectId",
  "name": "string",
  "email": "string",
  "password": "bcrypt hash",
  "created_at": "datetime"
}
```

Indexes:

- Unique `email`

## documents

```json
{
  "_id": "ObjectId",
  "user_id": "string",
  "filename": "string",
  "storage_path": "string",
  "upload_time": "datetime",
  "chunks_count": "number",
  "status": "processing | ready | failed",
  "error": "string optional"
}
```

Indexes:

- `user_id`, `upload_time desc`

## chat_history

```json
{
  "_id": "ObjectId",
  "user_id": "string",
  "question": "string",
  "answer": "markdown string",
  "sources": [
    {
      "source_id": "string",
      "filename": "string",
      "page": "number | null",
      "snippet": "string",
      "score": "number | null"
    }
  ],
  "rewritten_query": "string | null",
  "retrieval_score": "number",
  "web_search_used": "boolean",
  "logs": [
    {
      "step": "string",
      "status": "pending | running | completed | warning | error",
      "message": "string",
      "timestamp": "datetime"
    }
  ],
  "favorite": "boolean optional",
  "timestamp": "datetime"
}
```

Indexes:

- `user_id`, `timestamp desc`

## interaction_logs

```json
{
  "_id": "ObjectId",
  "user_id": "string",
  "question": "string",
  "rewritten_query": "string | null",
  "retrieval_score": "number",
  "web_search_used": "boolean",
  "time_taken": "number",
  "timestamp": "datetime"
}
```

Indexes:

- `user_id`, `timestamp desc`

## ChromaDB Collection

Collection: `docutrust_chunks`

Metadata per vector:

```json
{
  "user_id": "string",
  "document_id": "string",
  "filename": "string",
  "page": "number | null",
  "chunk_index": "number",
  "source_type": "pdf | web optional"
}
```
