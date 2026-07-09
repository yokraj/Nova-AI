# Database Schema Documentation - Nova AI

This document defines columns, types, indexes, and constraints for the **Nova AI Database Foundation (Milestone M2.1)**.

---

## 1. Tables Overview

| Table Name | Description | Primary Key | Foreign Keys | Indices |
| :--- | :--- | :--- | :--- | :--- |
| **users** | Tracks accounts credential and status details | `id` (UUID) | None | `ix_users_email`, `ix_users_username` |
| **conversations** | Manages user chat threads | `id` (UUID) | `user_id` -> `users.id` | `ix_conversations_user_id` |
| **messages** | Records chat prompts and responses content | `id` (UUID) | `conversation_id` -> `conversations.id` | `ix_messages_conversation_id` |
| **sessions** | Maps validation keys for logged-in sessions | `id` (UUID) | `user_id` -> `users.id` | `ix_sessions_token`, `ix_sessions_user_id` |
| **refresh_tokens**| Handles rotation tokens families session security | `id` (UUID) | `user_id` -> `users.id` | `ix_refresh_tokens_token`, `ix_refresh_tokens_user_id` |
| **user_preferences**| Registers client GUI/system configuration choices | `id` (UUID) | `user_id` -> `users.id` | `ix_user_preferences_user_id` |
| **ai_provider_configurations**| Maps credentials configurations for custom LLMs | `id` (UUID) | `user_id` -> `users.id` | `ix_ai_provider_configurations_user_id` |

---

## 2. Structural Column Definitions

### users Table
- `id` (UUID, Primary Key, indexed)
- `email` (VARCHAR(255), Not Null, Unique, indexed)
- `username` (VARCHAR(50), Not Null, Unique, indexed)
- `password_hash` (VARCHAR(255), Not Null)
- `display_name` (VARCHAR(100), Nullable)
- `avatar_url` (VARCHAR(255), Nullable)
- `status` (VARCHAR(20), Not Null, default 'active')
- `role` (VARCHAR(20), Not Null, default 'user')
- `created_at` (TIMESTAMP WITH TIME ZONE, Not Null)
- `updated_at` (TIMESTAMP WITH TIME ZONE, Not Null)

### conversations Table
- `id` (UUID, Primary Key, indexed)
- `user_id` (UUID, ForeignKey users.id, Cascade delete, indexed)
- `title` (VARCHAR(255), Not Null)
- `status` (VARCHAR(20), Not Null, default 'active')
- `created_at` (TIMESTAMP WITH TIME ZONE, Not Null)
- `updated_at` (TIMESTAMP WITH TIME ZONE, Not Null)

### messages Table
- `id` (UUID, Primary Key, indexed)
- `conversation_id` (UUID, ForeignKey conversations.id, Cascade delete, indexed)
- `role` (VARCHAR(20), Not Null)
- `content` (TEXT, Not Null)
- `token_count` (INTEGER, Not Null, default 0)
- `created_at` (TIMESTAMP WITH TIME ZONE, Not Null)
- `updated_at` (TIMESTAMP WITH TIME ZONE, Not Null)

### sessions Table
- `id` (UUID, Primary Key, indexed)
- `user_id` (UUID, ForeignKey users.id, Cascade delete, indexed)
- `token` (VARCHAR(255), Not Null, Unique, indexed)
- `expires_at` (TIMESTAMP WITH TIME ZONE, Not Null)
- `created_at` (TIMESTAMP WITH TIME ZONE, Not Null)
- `updated_at` (TIMESTAMP WITH TIME ZONE, Not Null)

### refresh_tokens Table
- `id` (UUID, Primary Key, indexed)
- `user_id` (UUID, ForeignKey users.id, Cascade delete, indexed)
- `token` (VARCHAR(255), Not Null, Unique, indexed)
- `is_revoked` (BOOLEAN, Not Null, default false)
- `expires_at` (TIMESTAMP WITH TIME ZONE, Not Null)
- `created_at` (TIMESTAMP WITH TIME ZONE, Not Null)
- `updated_at` (TIMESTAMP WITH TIME ZONE, Not Null)

### user_preferences Table
- `id` (UUID, Primary Key, indexed)
- `user_id` (UUID, ForeignKey users.id, Cascade delete, indexed)
- `key` (VARCHAR(100), Not Null)
- `value` (VARCHAR(255), Not Null)
- `created_at` (TIMESTAMP WITH TIME ZONE, Not Null)
- `updated_at` (TIMESTAMP WITH TIME ZONE, Not Null)

### ai_provider_configurations Table
- `id` (UUID, Primary Key, indexed)
- `user_id` (UUID, ForeignKey users.id, Cascade delete, indexed)
- `provider_name` (VARCHAR(100), Not Null)
- `api_key` (VARCHAR(255), Not Null)
- `api_base` (VARCHAR(255), Nullable)
- `model_defaults` (TEXT, Nullable)
- `created_at` (TIMESTAMP WITH TIME ZONE, Not Null)
- `updated_at` (TIMESTAMP WITH TIME ZONE, Not Null)
