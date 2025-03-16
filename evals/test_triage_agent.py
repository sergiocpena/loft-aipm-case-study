import json
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_agents.triage.triage_agent import triage_agent
from agents import Runner, RunConfig

# Simple colored output function
def colored(text, color=None):
    """Simple function to add color to terminal output"""
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        None: '\033[0m'
    }
    
    # If terminal doesn't support colors or we're on Windows without ANSI support
    if not sys.stdout.isatty() or (sys.platform == 'win32' and 'ANSICON' not in os.environ):
        return text
        
    return f"{colors.get(color, '')}{text}{colors.get(None)}"

def test_triage_agent():
    # Load test cases
    with open('evals/triage_agent_test_dataset.json', 'r') as f:
        test_data = json.load(f)
    
    total_tests = len(test_data['test_cases'])
    passed_tests = 0
    failed_tests = []
    
    print(colored("\n===== STARTING TRIAGE AGENT TESTS =====", "blue"))
    
    for test_case in test_data['test_cases']:
        test_name = test_case['name']
        print(colored(f"\nRunning test: {test_name}", "cyan"))
        
        try:
            # Test single input
            result = Runner.run_sync(
                starting_agent=triage_agent,
                run_config=RunConfig(workflow_name="test"),
                input=test_case['input']
            )
            
            # Check if agent is routing to the correct agent using last_agent property
            if 'expected_agent' in test_case:
                # Check the last_agent property
                if hasattr(result, 'last_agent'):
                    last_agent_name = result.last_agent.name.lower()
                    
                    # Convert expected_agent from snake_case to space-separated format
                    expected_agent = test_case['expected_agent'].replace('_', ' ').lower()
                    
                    # Check if the expected agent name matches the last agent name
                    assert expected_agent in last_agent_name, f"Expected agent '{expected_agent}' but got '{last_agent_name}'"
                else:
                    assert False, "Result does not have 'last_agent' property"
            
            passed_tests += 1
            print(colored(f"✓ Test passed: {test_name}", "green"))
            
        except Exception as e:
            failed_tests.append({"name": test_name, "error": str(e)})
            print(colored(f"✗ Test failed: {test_name}", "red"))
            print(colored(f"  Error: {str(e)}", "red"))
    
    # Calculate percentage
    pass_percentage = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    # Print summary
    print(colored("\n===== TEST SUMMARY =====", "blue"))
    print(colored(f"Total tests: {total_tests}", "white"))
    print(colored(f"Passed: {passed_tests} ({pass_percentage:.1f}%)", "green"))
    print(colored(f"Failed: {len(failed_tests)} ({100 - pass_percentage:.1f}%)", "red"))
    
    if failed_tests:
        print(colored("\nFailed tests:", "red"))
        for i, test in enumerate(failed_tests, 1):
            print(colored(f"  {i}. {test['name']}: {test['error']}", "red"))
    
    print(colored("\n===== END OF TESTS =====", "blue"))
    
    return {
        "total": total_tests,
        "passed": passed_tests,
        "failed": len(failed_tests),
        "percentage": pass_percentage,
        "failed_tests": failed_tests
    }

if __name__ == "__main__":
    results = test_triage_agent()
    
    # Exit with appropriate code (0 for success, 1 for failure)
    sys.exit(0 if results["failed"] == 0 else 1) 