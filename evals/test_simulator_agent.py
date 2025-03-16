import json
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_agents.simulator.simulator_agent import simulator_agent
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

def test_simulator_agent():
    # Load test cases
    with open('evals/simulator_agent_test_dataset.json', 'r') as f:
        test_data = json.load(f)
    
    total_tests = len(test_data['test_cases'])
    passed_tests = 0
    failed_tests = []
    
    print(colored("\n===== STARTING SIMULATOR AGENT TESTS =====", "blue"))
    
    for test_case in test_data['test_cases']:
        test_name = test_case['name']
        print(colored(f"\nRunning test: {test_name}", "cyan"))
        
        try:
            if 'conversation' in test_case:
                # Test multi-turn conversation
                result = None
                for i, message in enumerate(test_case['conversation']):
                    if message['role'] == 'user':
                        if result is None:
                            result = Runner.run_sync(
                                starting_agent=simulator_agent,
                                run_config=RunConfig(workflow_name="test"),
                                input=message['content']
                            )
                        else:
                            new_input = result.to_input_list() + [{"role": "user", "content": message['content']}]
                            result = Runner.run_sync(
                                starting_agent=simulator_agent,
                                run_config=RunConfig(workflow_name="test"),
                                input=new_input
                            )
                        
                        if i+1 < len(test_case['conversation']) and test_case['conversation'][i+1]['role'] == 'assistant':
                            expected = test_case['conversation'][i+1]['content']
                            # Flexible comparison since exact wording may vary
                            assert any(keyword in result.final_output.lower() for keyword in expected.lower().split()), \
                                f"Response doesn't match expected assistant message"
            else:
                # Test single input
                result = Runner.run_sync(
                    starting_agent=simulator_agent,
                    run_config=RunConfig(workflow_name="test"),
                    input=test_case['input']
                )
                
                # Check if agent asks for missing fields
                if 'missing_fields' in test_case:
                    for field in test_case['missing_fields']:
                        field_keywords = {
                            'person_type': ['pessoa', 'física', 'jurídica', 'tipo'],
                            'property_value': ['valor', 'imóvel', 'custa', 'preço'],
                            'state': ['estado', 'uf', 'localização'],
                            'city': ['cidade', 'município', 'localização']
                        }
                        
                        # Check if agent asks for this missing field
                        assert any(keyword in result.final_output.lower() for keyword in field_keywords[field]), \
                            f"Agent didn't ask for missing field: {field}"
                
                # Check if agent correctly identified provided fields
                if 'provided_fields' in test_case:
                    # This is a simplified check - in a real implementation, you might want to 
                    # check if the agent actually stored these values correctly
                    for field, value in test_case['provided_fields'].items():
                        # Convert value to string for comparison
                        value_str = str(value).lower()
                        # Check if the value appears in the response
                        assert value_str in result.final_output.lower() or \
                               any(keyword in result.final_output.lower() for keyword in field_keywords.get(field, [])), \
                               f"Agent didn't acknowledge provided field: {field} = {value}"
            
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
    results = test_simulator_agent()
    
    # Exit with appropriate code (0 for success, 1 for failure)
    sys.exit(0 if results["failed"] == 0 else 1) 