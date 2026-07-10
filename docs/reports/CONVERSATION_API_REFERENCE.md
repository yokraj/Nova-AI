# Nova AI Conversation Platform - REST API Reference

This document describes the HTTP REST endpoints exposed by the Nova AI Conversation Platform context.

---

## 1. Conversation Endpoints

### POST `/api/v1/conversations`
Initializes a new chat conversation thread.

- **Headers**:
  - `Authorization: Bearer <JWT_ACCESS_TOKEN>`
- **Request Body**:
  ```json
  {
    "title": "New Chat Thread"
  }
  ```
- **Responses**:
  - `201 Created`:
    ```json
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "user_id": "85715b56-f933-4de0-8e2f-72533b715ccc",
      "title": "New Chat Thread",
      "status": "active",
      "created_at": "2026-07-10T09:00:00Z",
      "updated_at": "2026-07-10T09:00:00Z"
    }
    ```
  - `401 Unauthorized`: Token missing or invalid.
  - `400 Bad Request`: Empty/whitespace title.

---

### GET `/api/v1/conversations`
Retrieves paginated user conversation history summary listings.

- **Headers**:
  - `Authorization: Bearer <JWT_ACCESS_TOKEN>`
- **Query Parameters**:
  - `limit`: Pagination limit (default: `20`, range: `1` to `100`).
  - `offset`: Pagination offset index (default: `0`, >= `0`).
- **Responses**:
  - `200 OK`:
    ```json
    [
      {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "title": "New Chat Thread",
        "status": "active",
        "last_message_at": "2026-07-10T09:05:00Z",
        "created_at": "2026-07-10T09:00:00Z"
      }
    ]
    ```
  - `401 Unauthorized`: Token invalid.

---

### GET `/api/v1/conversations/{id}`
Retrieves metadata properties for a specific conversation thread.

- **Headers**:
  - `Authorization: Bearer <JWT_ACCESS_TOKEN>`
- **Responses**:
  - `200 OK`:
    ```json
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "user_id": "85715b56-f933-4de0-8e2f-72533b715ccc",
      "title": "New Chat Thread",
      "status": "active",
      "created_at": "2026-07-10T09:00:00Z",
      "updated_at": "2026-07-10T09:00:00Z"
    }
    ```
  - `404 Not Found`: Thread not found or soft-deleted.
  - `403 Forbidden`: Thread belongs to another user.

---

### PATCH `/api/v1/conversations/{id}`
Renames a conversation thread's title description.

- **Headers**:
  - `Authorization: Bearer <JWT_ACCESS_TOKEN>`
- **Request Body**:
  ```json
  {
    "title": "Renamed Chat Thread"
  }
  ```
- **Responses**:
  - `200 OK`:
    ```json
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "user_id": "85715b56-f933-4de0-8e2f-72533b715ccc",
      "title": "Renamed Chat Thread",
      "status": "active",
      "created_at": "2026-07-10T09:00:00Z",
      "updated_at": "2026-07-10T09:10:00Z"
    }
    ```
  - `404 Not Found`, `403 Forbidden`, `400 Bad Request` (Empty title).

---

### DELETE `/api/v1/conversations/{id}`
Soft-deletes a conversation thread.

- **Headers**:
  - `Authorization: Bearer <JWT_ACCESS_TOKEN>`
- **Responses**:
  - `204 No Content`: Successful soft-delete.
  - `404 Not Found`, `403 Forbidden`.

---

## 2. Conversation Messages Endpoints

### POST `/api/v1/conversations/{id}/messages`
Appends a new chat message content inside thread.

- **Headers**:
  - `Authorization: Bearer <JWT_ACCESS_TOKEN>`
- **Request Body**:
  ```json
  {
    "role": "user",
    "content": "What is the token limit?"
  }
  ```
- **Responses**:
  - `201 Created`:
    ```json
    {
      "id": "7fa85f64-5717-4562-b3fc-2c963f66afa6",
      "conversation_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "role": "user",
      "content": "What is the token limit?",
      "token_count": 5,
      "created_at": "2026-07-10T09:05:00Z",
      "attachments": []
    }
    ```
  - `404 Not Found`, `403 Forbidden`.
  - `400 Bad Request`: If empty content or conversation is archived.

---

### GET `/api/v1/conversations/{id}/messages`
Retrieves paginated messages and file attachments associated inside thread.

- **Headers**:
  - `Authorization: Bearer <JWT_ACCESS_TOKEN>`
- **Query Parameters**:
  - `limit`: Pagination limit (default: `50`, range: `1` to `100`).
  - `offset`: Pagination offset index (default: `0`, >= `0`).
- **Responses**:
  - `200 OK`:
    ```json
    [
      {
        "id": "7fa85f64-5717-4562-b3fc-2c963f66afa6",
        "conversation_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "role": "user",
        "content": "What is the token limit?",
        "token_count": 5,
        "created_at": "2026-07-10T09:05:00Z",
        "attachments": []
      }
    ]
    ```
  - `404 Not Found`, `403 Forbidden`.
