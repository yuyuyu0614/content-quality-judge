"""
content_quality_judge.py
Estimate V5.1 — L2 内容级质量评估
用 GPT-5.4-Mini 评估搜索结果的 content_quality_score，替代纯域名白名单打分。
"""

import json
import os
from openai import OpenAI

# 使用兼容的 OpenAI-compatible client
# 支持: GPT-5.4-Mini (通过 Azure/OpenAI API), DeepSeek (通过 deepseek API)

QUALITY_EVAL_SYSTEM_PROMPT = """你是一个信息质量评估员。你的任务是仅根据搜索引擎返回的内容本身（标题+摘要+域名），对搜索结果的信息质量进行评估。

**重要原则：**
1. 你看到的仅是搜索结果的标题和摘要（snippet），不是完整的网页内容。所以你的质量判断需要基于这些有限的信号。
2. 域名的权威性仅为参考信号之一，不应该是决定性因素。一个个人博客如果摘要中引用了具体数据和来源，也可能得分很高。
3. 对于无法从标题和摘要中判断的信息，请诚实标记为 null 或 false，不要猜测。
4. 中文和英文来源一视同仁，不因语言偏好而加减分。

**输出格式：** 只输出 JSON，不要任何其他文字。

JSON 字段说明：
- domain_type: 根据域名和内容综合判断来源类型
- content_quality_signals: 从标题和摘要中可识别的质量信号
- content_quality_score: 0.0-1.0 的综合质量分
  0.8-1.0: 官方一手信源、学术论文、权威媒体原创报道
  0.5-0.8: 知名商业媒体、数据平台、Wikipedia（英文）
  0.3-0.5: 普通科技博客、论坛高质量回答、Wikipedia（中文）
  0.0-0.3: 内容农场、无署名转载、无法判断来源
- is_likely_accurate: 仅凭内容本身是否看起来准确（null=无法判断）
- reasoning: 一句话简述判断依据（中文）
"""

QUALITY_EVAL_USER_TEMPLATE = """请评估以下搜索结果的质量。

Claim（待验证的主张）: {claim}
搜索结果标题: {title}
搜索结果摘要: {snippet}
搜索结果显示域名: {domain}

请输出 JSON："""


class ContentQualityJudge:
    """内容质量评估器。使用 LLM 评估搜索结果的 quality_score。"""

    def __init__(
        self,
        api_key: str = None,
        base_url: str = None,
        model: str = "deepseek-chat",
    ):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.base_url = base_url or os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        self.model = model

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY 环境变量未设置")

        client_kwargs = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url
        self.client = OpenAI(**client_kwargs)

    def evaluate(self, claim: str, title: str, snippet: str, domain: str) -> dict:
        """
        对单条搜索结果进行内容质量评估。

        Args:
            claim: 待验证的主张文本
            title: 搜索结果标题
            snippet: 搜索结果摘要
            domain: 搜索结果显示域名

        Returns:
            dict 包含 domain_type, content_quality_signals,
                 content_quality_score, is_likely_accurate, reasoning
        """
        user_prompt = QUALITY_EVAL_USER_TEMPLATE.format(
            claim=claim,
            title=title or "(无标题)",
            snippet=snippet or "(无摘要)",
            domain=domain or "(未知域名)",
        )

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": QUALITY_EVAL_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
                max_tokens=300,
                response_format={"type": "json_object"},
            )
            raw = resp.choices[0].message.content
            result = json.loads(raw)

            # 确保必需字段存在
            result.setdefault("domain_type", "无法判断")
            result.setdefault("content_quality_signals", {})
            result.setdefault("content_quality_score", 0.0)
            result.setdefault("is_likely_accurate", None)
            result.setdefault("reasoning", "")

            return {
                "domain_type": result.get("domain_type", "无法判断"),
                "content_quality_signals": result.get("content_quality_signals", {}),
                "content_quality_score": float(result.get("content_quality_score", 0.0)),
                "is_likely_accurate": result.get("is_likely_accurate"),
                "reasoning": result.get("reasoning", ""),
                "raw_response": raw,
            }
        except Exception as e:
            return {
                "domain_type": "评估失败",
                "content_quality_signals": {},
                "content_quality_score": 0.0,
                "is_likely_accurate": None,
                "reasoning": f"评估错误: {str(e)}",
                "raw_response": None,
                "error": str(e),
            }

    def evaluate_batch(self, evaluations: list[dict]) -> list[dict]:
        """批量评估多条搜索结果。"""
        results = []
        for ev in evaluations:
            result = self.evaluate(
                claim=ev.get("claim", ""),
                title=ev.get("title", ""),
                snippet=ev.get("snippet", ""),
                domain=ev.get("domain", ""),
            )
            result["_source"] = ev
            results.append(result)
        return results
