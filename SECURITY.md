# Security Policy

## Reporting Security Issues

Idea Tracker is a local-first application designed to run on a user's machine. However, security remains essential.

If you discover a security vulnerability:

1. **Do NOT open a public issue.**
2. Report the vulnerability directly via private email to the project maintainers or via GitHub Security Advisories.
3. Include detailed steps to reproduce the issue.

We will acknowledge receipt of your report within 48 hours and provide updates on resolution.

## Local Security Guarantees

- **No telemetry / phone-home**: Idea Tracker does not send usage metrics, telemetry, or tracking to any remote server.
- **Secrets protection**: API keys for external LLM providers (OpenAI, Anthropic) are loaded strictly from local environment variables and are never logged or exported.
- **SQL Injection protection**: All database queries are executed using SQLAlchemy ORM / parametrized statements.
