import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from stockiv.crews.sentiment_analyst.sentiment_analyst import SentimentAnalystCrew


def test_sentiment_yaml_paths():
    print("Testing Sentiment Analyst tasks variables...")
    try:
        sentiment_inst = SentimentAnalystCrew()

        expected_macro = "{report_md_path}"
        expected_overall = "{overall_report_md_path}"

        actual_macro = sentiment_inst.tasks_config["summarize_current_week_macro"][
            "output_file"
        ]
        actual_overall = sentiment_inst.tasks_config["synthesize_recent_trends"][
            "output_file"
        ]

        print(f"macro path template: {actual_macro}")
        print(f"overall path template: {actual_overall}")

        assert actual_macro == expected_macro, (
            f"Expected {expected_macro}, got {actual_macro}"
        )
        assert actual_overall == expected_overall, (
            f"Expected {expected_overall}, got {actual_overall}"
        )

        print("YAML mappings are correctly updated.")

    except Exception as e:
        print(f"Error during validation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    test_sentiment_yaml_paths()
