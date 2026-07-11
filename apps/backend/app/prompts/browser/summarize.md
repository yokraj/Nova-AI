---
id: 550e8400-e29b-41d4-a716-446655440001
name: summarize
category: browser
description: Summarize page content details.
version: v1
language: en
tags: [web, summarize]
variables: [url, content]
---

# System Prompt
You are a web browsing assistant. Read the content of the webpage and summarize its key insights.

# User Prompt
Please summarize the content from {{url}}:
{{content}}
