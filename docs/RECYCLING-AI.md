# Recycling AI — design & notes

This document describes the AI-powered recycling recommendation feature (MVP-level).

Features
- POST /api/recycle/recommend — accepts items and returns per-item recommendations.
- POST /api/recycle/feedback — accepts feedback to store for later model tuning.

Privacy
- Profiles are opt-in and stored as JSON in `data/profiles/`.
- Feedback is stored in `data/feedback/` and should be purged or aggregated before any external uploads.

LLM Integration
- Controlled by `OPENAI_API_KEY` env var. If absent, the system falls back to deterministic heuristics.
- Responses from the model are parsed for JSON; if parsing fails, we fall back to heuristics.

Next steps
- Add a small retriever or local knowledge base for municipality-specific rules.
- Implement fine-tuning / prompt engineering pipeline using the feedback dataset.
