import os
import re
import argparse
from datetime import datetime

# Optional dotenv for local development (not needed in Streamlit Cloud)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # Running in cloud environment without python-dotenv

from pubmed_client import PubMedClient
from analyzer import TrendAnalyzer

def sanitize_topic(topic: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_\-]', '', topic.replace(" ", "_"))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("topic", nargs="?")
    parser.add_argument("--max", type=int, default=20)
    args = parser.parse_args()
    
    topic_input = args.topic if args.topic else input("Topic: ").strip()
    if not topic_input: return

    safe_topic = sanitize_topic(topic_input)
    client = PubMedClient()
    analyzer = TrendAnalyzer(model_name=os.getenv("OLLAMA_MODEL", "gptoss120b-cloud"))
    
    query = f"{topic_input} AND (pharmacoepidemiology OR 'real world evidence')"
    print(f"Fetching papers for {query}...")
    abstracts = client.fetch_abstracts(query, max_results=args.max)
    
    if not abstracts:
        print("No papers found.")
        return

    print("Analyzing...")
    result = analyzer.analyze_and_hypothesize(abstracts, topic_input)
    
    filename = f"report_{safe_topic}_{datetime.now().strftime('%Y%m%d')}.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# Report: {topic_input}\n\n## Trends\n{result.trend_summary}\n\n## Gaps\n")
        for g in result.identified_gaps: f.write(f"- {g}\n")
        f.write("\n## Hypotheses\n")
        for h in result.hypotheses:
            f.write(f"### {h.title}\n**Rationale:** {h.rationale}\n\n**Method:** {h.methodology}\n\n")
    print(f"Saved to {filename}")

if __name__ == "__main__":
    main()
