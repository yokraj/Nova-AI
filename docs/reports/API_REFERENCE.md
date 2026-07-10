# Nova AI Identity Platform - REST API Reference

This document describes the HTTP REST endpoints exposed by the Nova AI Identity & Security Platform.

---

## 1. Authentication Endpoints

### POST `/api/v1/auth/register`
Registers a new user account profile.

- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "username": "username123",
    "password": "secure_password_123",
    "display_name": "Display Name"
  }
  ```
- **Responses**:
  - `201 Created`:
    ```json
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "email": "user@example.com",
      "username": "username123",
      "display_name": "Display Name",
      "role": "user",
      "status": "active",
      "created_at": "2026-07-09T06:00:00Z"
    }
    ```
  - `409 Conflict`: If the email address or username is already registered.

---

### POST `/api/v1/auth/login`
Authenticates user credentials and generates access and refresh tokens.

- **Request Body**:
  ```json
  {
    "username_or_email": "user@example.com",
    "password": "secure_password_123"
  }
  ```
- **Responses**:
  - `200 OK`:
    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
      "refresh_token": "2e0b5d95d1dac456d10098e9834...",
      "token_type": "bearer"
    }
    ```
  - `401 Unauthorized`: For invalid credentials or suspended user accounts.

---

### POST `/api/v1/auth/refresh`
Rotates the refresh token family and issues a new access token.

- **Request Body**:
  ```json
  {
    "refresh_token": "2e0b5d95d1dac456d10098e9834..."
  }
  ```
- **Responses**:
  - `200 OK`:
    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
      "refresh_token": "3f6a2b0e9dac456d10098e98345...",
      "token_type": "bearer"
    }
    ```
  - `401 Unauthorized`: For expired or invalid refresh tokens.
  - `403 Forbidden`: Token reuse breach detected (invalidates entire token family).

---

### POST `/api/v1/auth/logout`
Revokes the refresh token to terminate the session.

- **Request Body**:
  ```json
  {
    "refresh_token": "3f6a2b0e9dac456d10098e98345..."
  }
  ```
- **Responses**:
  - `204 No Content`: Successful logout.
  - `401 Unauthorized`: If the refresh token is invalid.

---

## 2. User Profile Endpoints

### GET `/api/v1/profile`
Fetches the profile details of the authenticated user session.

- **Headers**:
  - `Authorization: Bearer <JWT_ACCESS_TOKEN>`
- **Responses**:
  - `200 OK`:
    ```json
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "email": "user@example.com",
      "username": "username123",
      "display_name": "Display Name",
      "avatar_url": "https://example.com/avatar.png",
      "role": "user",
      "status": "active",
      "created_at": "2026-07-09T06:00:00Z",
      "updated_at": "2026-07-09T06:10:00Z"
    }
    ```
  - `401 Unauthorized`: If token is missing, invalid, or expired.

---

### PATCH `/api/v1/profile`
Updates optional display name and/or avatar properties.

- **Headers**:
  - `Authorization: Bearer <JWT_ACCESS_TOKEN>`
- **Request Body**:
  ```json
  {
    "display_name": "New Display Name",
    "avatar_url": "https://example.com/new_avatar.png"
  }
  ```
- **Responses**:
  - `200 OK`:
    ```json
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "email": "user@example.com",
      "username": "username123",
      "display_name": "New Display Name",
      "avatar_url": "https://example.com/new_avatar.png",
      "role": "user",
      "status": "active",
      "created_at": "2026-07-09T06:00:00Z",
      "updated_at": "2026-07-09T06:20:00Z"
    }
    ```
  - `401 Unauthorized`: If token is missing or expired.
