import asyncio
import argparse
import os
import json

from triumvirate.orchestrator import TriumvirateOrchestrator
from triumvirate.adapters import FileSystemAdapter
from triumvirate.api_adapters import AnthropicAPIAdapter

async def main():
    """Main function to run the Triumvirate CLI."""
    parser = argparse.ArgumentParser(description="Triumvirate AI Collaboration Framework CLI")
    parser.add_argument("prompt", type=str, help="The user request for the workflow (e.g., 'Create a /users endpoint')")
    parser.add_argument(
        "--adapter", 
        type=str, 
        choices=["filesystem", "anthropic"], 
        default="filesystem", 
        help="The adapter to use for the consultation."
    )
    parser.add_argument(
        "--model",
        type=str,
        default="claude-3-sonnet-20240229",
        help="The model to use for the Anthropic adapter."
    )

    args = parser.parse_args()

    print(f"Using adapter: {args.adapter}")

    if args.adapter == "filesystem":
        adapter = FileSystemAdapter()
    elif args.adapter == "anthropic":
        if not os.environ.get("ANTHROPIC_API_KEY"):
            print("Error: ANTHROPIC_API_KEY environment variable not set.")
            print("Please set the key to use the Anthropic adapter.")
            return
        adapter = AnthropicAPIAdapter(default_model=args.model)
    else:
        # This case should not be reached due to argparse choices
        raise ValueError(f"Unknown adapter: {args.adapter}")

    # For simplicity, we use the same adapter for both roles
    orchestrator = TriumvirateOrchestrator(
        architect_adapter=adapter,
        engineer_adapter=adapter
    )

    print(f"\nStarting workflow for prompt: '{args.prompt}'...")

    try:
        result = await orchestrator.generate_api_endpoint(args.prompt)
        
        print("\n--- Workflow Complete ---")
        print("\nArchitect's Design:")
        print("---------------------")
        print(json.dumps(result.get("design", {}), indent=2))
        
        print("\nEngineer's Code:")
        print("------------------")
        print(result.get("code", ""))

    except Exception as e:
        print(f"\n--- An error occurred ---")
        print(f"{type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
