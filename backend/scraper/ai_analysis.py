from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def get_ai_summary(domain: str, page_title: str, meta_description: str, performance_score: float, seo_score: float, accessibility_score: float) -> str:
    try:
        prompt = f"""
        You are analyzing a Nigerian website. Based on the information below, write a 2-sentence summary about the website and how well it is optimized.

        Domain: {domain}
        Page Title: {page_title}
        Meta Description: {meta_description}
        Performance Score: {performance_score}/100
        SEO Score: {seo_score}/100
        Accessibility Score: {accessibility_score}/100

        Keep it concise and professional.
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"AI summary error for {domain}: {e}")
        return None