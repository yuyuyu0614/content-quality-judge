# content-quality-judge

**AI 驱动的内容质量评估。** 输入文本（待验证声明 + 搜索结果），输出 0-1 质量评分和评估理由——不依赖域名白名单，基于内容本身判断。

---

## 它能做什么

用大语言模型（LLM）评估搜索结果片段的信息质量，通过内容信号（署名、引用、具体性）判断可靠性，而不是脆弱的域名白名单匹配。

| 输入 | 输出 |
| --- | --- |
| `claim` + `title` + `snippet` + `domain` | `{ content_quality_score, domain_type, reasoning, ... }` |

**示例：** “阿里巴巴FY2024营收9000亿人民币” + `alibabagroup.com` IR页面 → **评分: 0.95**（企业官方，包含具体数字）

**反例：** 内容农场文章 → **评分: 0.10**（无署名、无来源、低质量）

---

## 安装

```bash
pip install content-quality-judge
```

**唯一依赖：** `openai` (>=1.0.0)。

---

## 快速开始

```python
from content_quality_judge import ContentQualityJudge

judge = ContentQualityJudge(api_key="sk-xxx")

result = judge.evaluate(
    claim="阿里巴巴FY2024营收超过9000亿人民币",
    title="阿里巴巴集团 — 投资者关系",
    snippet="2024财年年报。营收：9412亿人民币。",
    domain="alibabagroup.com",
)

print(result["content_quality_score"])  # 0.95
print(result["domain_type"])            # corporate_official
print(result["reasoning"])              # 官方财报，具体数据
```

**3 行代码。** 这就是全部公开 API。

---

## API 参数

### `ContentQualityJudge(api_key, base_url, model)`

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `api_key` | str | 必填 | LLM API 密钥 |
| `base_url` | str | `None` | API 端点地址 |
| `model` | str | `"deepseek-chat"` | 模型名称 |

### `evaluate(claim, title, snippet, domain)`

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `claim` | str | 待验证的主张文本 |
| `title` | str | 搜索结果标题 |
| `snippet` | str | 搜索结果摘要 |
| `domain` | str | 搜索结果显示域名 |

**返回值：** `dict`，包含：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `content_quality_score` | float | 0.0-1.0 综合质量分 |
| `domain_type` | str | 来源类型分类 |
| `content_quality_signals` | dict | 质量信号（署名、日期、数据引用等） |
| `is_likely_accurate` | bool/null | 仅凭内容本身判断是否准确 |
| `reasoning` | str | 中文判断依据 |

---

## 评分标准

| 分数区间 | 含义 |
| --- | --- |
| 0.8-1.0 | 官方一手信源、学术论文、权威媒体原创报道 |
| 0.5-0.8 | 知名商业媒体、数据平台、Wikipedia（英文） |
| 0.3-0.5 | 普通科技博客、论坛高质量回答、Wikipedia（中文） |
| 0.0-0.3 | 内容农场、无署名转载、无法判断来源 |

---

## 设计理念

**“看内容，不看域名。”** 一个个人博客如果摘要中引用了具体数据和来源，也可以得高分。阿里官网不会被白名单遗漏而错误扣分。域名只是参考信号之一，不是决定性因素。

---

## 支持的模型

| 模型 | 说明 |
| --- | --- |
| **DeepSeek V4 Pro** | ✅ 已验证，推荐 |
| **GPT-5.4-Mini** | ✅ 已验证 |
| **Ollama 本地模型** | ✅ 兼容 |

---

## 许可

MIT