# content-quality-judge

**AI-powered content quality assessment.** Input text (claim + search result), get a 0-1 quality score with reasoning — no domain whitelist needed.

---

## What it does

A single function that evaluates the information quality of a search result snippet, using an LLM to judge content signals (authorship, citations, specificity) rather than relying on brittle domain whitelist matching.

| Input | Output |
| --- | --- |
| `claim` + `title` + `snippet` + `domain` | `{ content_quality_score, domain_type, reasoning, ... }` |

**Example:** "Alibaba FY2024 revenue 900B RMB" → `alibabagroup.com` IR page → **score: 0.95** (corporate official, specific figures cited)

---

## Installation

```bash
pip install content-quality-judge
# or from source:
pip install -e .
```

**Single dependency:** `openai` (>=1.0.0). No other packages required.

---

## Quick Start

```python
from content_quality_judge import ContentQualityJudge

judge = ContentQualityJudge(api_key="sk-xxx")

result = judge.evaluate(
    claim="Alibaba FY2024 revenue exceeded 900B RMB",
    title="Alibaba Group — Investor Relations",
    snippet="Fiscal Year 2024 Annual Report. Revenue: 941.2 billion RMB.",
    domain="alibabagroup.com",
)

print(result["content_quality_score"])  # 0.95
print(result["domain_type"])            # corporate_official
print(result["reasoning"])              # 官方财报，具体数据
```

**3 lines of code.** That is the entire public API.

---

## API Reference

### `ContentQualityJudge(api_key, base_url=None, model="gpt-4o-mini")`

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `api_key` | `str` | (required) | Your LLM API key |
| `base_url` | `str` | `None` | Custom API endpoint (default: OpenAI) |
| `model` | `str` | `"gpt-4o-mini"` | Model name. Any OpenAI-compatible model. |

### `judge.evaluate(claim, title, snippet, domain)`

| Parameter | Type | Description |
| --- | --- | --- |
| `claim` | `str` | The factual claim to verify |
| `title` | `str` | Search result title |
| `snippet` | `str` | Search result snippet (first 200 chars recommended) |
| `domain` | `str` | Search result domain (for context) |

**Returns:** `dict`

| Field | Type | Description |
| --- | --- | --- |
| `domain_type` | `str` | Classified source type (gov, academic, news, blog, content_farm...) |
| `content_quality_signals` | `dict` | Detected quality signals (has_author, has_date, cites_sources...) |
| `content_quality_score` | `float` | **0.0-1.0** overall quality assessment |
| `is_likely_accurate` | `bool/null` | Whether content appears accurate (null = cannot determine) |
| `reasoning` | `str` | One-sentence explanation (Chinese or English) |

### `judge.evaluate_batch(evaluations)`

Batch version. Takes a list of dicts with same keys as `evaluate()`.

---

## Supported Models

Any OpenAI-compatible model works. Verified:

| Model | Provider | base_url | Notes |
| --- | --- | --- | --- |
| **DeepSeek V4 Pro** | DeepSeek | `https://api.deepseek.com` | ✅ Verified. Chinese-native, 1M context, ~$0.27/M tokens |
| GPT-4o-mini | OpenAI | (default) | Recommended. Fast, cheap, good quality |
| GPT-4o | OpenAI | (default) | Higher quality, higher cost |
| Any OpenAI-compatible | Custom | User-provided | `model="your-model"`, `base_url="https://..."` |

**Switching models:**

```python
# DeepSeek
judge = ContentQualityJudge(
    api_key="sk-deepseek-xxx",
    base_url="https://api.deepseek.com",
    model="deepseek-chat",
)

# Custom MoMA / local model
judge = ContentQualityJudge(
    api_key="not-needed",
    base_url="http://localhost:8000/v1",
    model="llama-3-70b",
)
```

---

## Scoring Guide

| Score Range | Meaning | Example |
| --- | --- | --- |
| 0.8-1.0 | Official first-party, academic, top-tier media | `alibabagroup.com` IR page, `who.int` |
| 0.5-0.8 | Reputable media, data platforms, Wikipedia (EN) | `statista.com`, `macrumors.com`, `36kr.com` |
| 0.3-0.5 | Tech blogs, forums, Wikipedia (ZH) | Niche tech blogs, community wikis |
| 0.0-0.3 | Content farms, no-author reprints, unknown | `articlesfactory.com`, SEO spam |

---

## Use Cases

- **AI fact-checking pipelines:** Add quality scoring before verification
- **Search result ranking:** Re-rank results by content quality, not just relevance
- **RAG quality control:** Filter retrieved documents before feeding to LLM
- **Content moderation:** Detect low-quality / AI-generated spam
- **News aggregators:** Score source credibility programmatically

---

## Pair with fact-atomizer

Combine L0 (atomize) + L2 (score):

```python
from fact_atomizer import FactAtomizer
from content_quality_judge import ContentQualityJudge

atomizer = FactAtomizer(api_key="sk-xxx")
judge = ContentQualityJudge(api_key="sk-xxx")

claims = atomizer.atomize("Some text with claims...")
for claim in claims:
    quality = judge.evaluate(claim["claim_text"], result_title, result_snippet, result_domain)
    print(f"{claim['claim_text']} -> score: {quality['content_quality_score']}")
```

---

## FAQ

**Q: Does it need a domain whitelist?**  
No. The LLM judges content signals directly. Domain is only used as context.

**Q: How much does it cost?**  
~$0.0005 per evaluation with GPT-4o-mini. ~$0.0001 with DeepSeek V3.

**Q: Can I use it without internet?**  
Yes, if you run a local LLM server (Ollama, vLLM) with OpenAI-compatible API.

**Q: Is it production-ready?**  
Alpha. Verified on 20-claim benchmark (7/17 cases improved vs domain-based scoring, 0 regressions).

---

## License

MIT