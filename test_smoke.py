from content_quality_judge import ContentQualityJudge

j = ContentQualityJudge(
    api_key="sk-151412e08bf5446fb0afbd15aa6a78b3",
    base_url="https://api.deepseek.com",
    model="deepseek-chat",
)

r = j.evaluate(
    claim="China 2024 GDP grew 5%",
    title="China GDP 2024 Statistics",
    snippet="GDP grew 5% in 2024 according to NBS",
    domain="stats.gov.cn",
)

print(f"Score: {r['content_quality_score']}")
print(f"Type: {r['domain_type']}")
print(f"Reasoning: {r['reasoning']}")
print("PASS")