import os
from crewai import LLM
from dotenv import load_dotenv

load_dotenv()


def test_connection():
    api_key = os.getenv("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_AUTH_TOKEN"))
    base_url = os.getenv(
        "ANTHROPIC_BASE_URL",
        "https://coding-intl.dashscope.aliyuncs.com/apps/anthropic",
    )

    if not api_key:
        print(
            "❌ Error: ANTHROPIC_API_KEY or ANTHROPIC_AUTH_TOKEN not found in environment variables"
        )
        return

    print(f"Testing connection to anthropic/qwen3.5-plus at {base_url}...")

    try:
        # Initialize LLM
        llm = LLM(
            model="qwen3.5-plus",
            api_key=api_key,
            base_url=base_url,
            provider="anthropic",
        )

        # Simple test call
        response = llm.call("Say 'Connection Successful'")
        print(f"✅ Response: {response}")

    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")


if __name__ == "__main__":
    test_connection()
