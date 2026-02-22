import argparse
import sys
from src.reasoning.orchestrator import ReasoningOrchestrator
from src.reasoning.strategy import StrategyInput
from src.output.generator import ReportGenerator

def main():
    parser = argparse.ArgumentParser(description="AI-Powered M&A Analysis Platform")
    parser.add_argument("--query", type=str, required=True, help="Analyst query")
    parser.add_argument("--objective", type=str, default="Acquisition", help="Strategic objective")
    parser.add_argument("--horizon", type=int, default=12, help="Time horizon in months")
    parser.add_argument("--risk", type=str, default="medium", choices=["low", "medium", "high"], help="Risk tolerance")
    
    args = parser.parse_args()

    # 1. Setup Strategy
    strategy = StrategyInput(
        objective=args.objective,
        time_horizon_months=args.horizon,
        risk_tolerance=args.risk
    )
    
    print(f"Initializing Analysis for: {strategy.objective}")
    
    # 2. Initialize Orchestrator
    orchestrator = ReasoningOrchestrator()
    
    try:
        # 3. Generate content
        print("Running reasoning engine...")
        content = orchestrator.generate_report(strategy, args.query)
        
        # 4. Format Output
        generator = ReportGenerator()
        is_valid = "Validation Failed" not in content
        final_report = generator.format_to_markdown(content, strategy, is_valid)
        
        # 5. Save/Print
        output_file = "analysis_report.md"
        generator.save_report(final_report, output_file)
        print(f"Report generated: {output_file}")
        print("-" * 40)
        print(final_report)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        orchestrator.close()

if __name__ == "__main__":
    main()
