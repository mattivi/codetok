from codetok.analyzer import CodeAnalyzer
from codetok.config import Config

if __name__ == "__main__":
    print("Analyzing the current directory with codetok...")
    config = Config(
        path=".", output_file="examples/sample_report.json", json_only=True
    )
    analyzer = CodeAnalyzer(config)
    analyzer.analyze()
    print("Analysis complete! See examples/sample_report.json for the report.")
