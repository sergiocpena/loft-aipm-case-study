import json
import sys
import os
from termcolor import colored  # For colored terminal output

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_agents.application.application_agent import application_agent
from agents import Runner, RunConfig

def test_application_agent():
    # Load test cases
    with open('evals/application_agent_test_dataset.json', 'r') as f:
        test_data = json.load(f)
    
    total_tests = len(test_data['test_cases'])
    passed_tests = 0
    failed_tests = []
    
    print(colored("\n===== STARTING APPLICATION AGENT TESTS =====", "blue"))
    
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
                                starting_agent=application_agent,
                                run_config=RunConfig(workflow_name="test"),
                                input=message['content']
                            )
                        else:
                            new_input = result.to_input_list() + [{"role": "user", "content": message['content']}]
                            result = Runner.run_sync(
                                starting_agent=application_agent,
                                run_config=RunConfig(workflow_name="test"),
                                input=new_input
                            )
                        
                        if i+1 < len(test_case['conversation']) and test_case['conversation'][i+1]['role'] == 'assistant':
                            expected = test_case['conversation'][i+1]['content']
                            # Flexible comparison since exact wording may vary
                            assert any(keyword in result.final_output.lower() for keyword in expected.lower().split())
            else:
                # Test single input
                result = Runner.run_sync(
                    starting_agent=application_agent,
                    run_config=RunConfig(workflow_name="test"),
                    input=test_case['input']
                )
                
                # Check if agent asks for missing fields
                if 'missing_fields' in test_case:
                    for field in test_case['missing_fields']:
                        field_keywords = {
                            'full_name': ['nome', 'completo'],
                            'cpf_number': ['cpf', 'documento'],
                            'date_of_birth': ['nascimento', 'data'],
                            'monthly_income': ['renda', 'salário', 'ganho'],
                            'marital_status': ['civil', 'casado', 'solteiro'],
                            'person_type': ['física', 'jurídica', 'pessoa'],
                            'property_value': ['valor', 'imóvel', 'custa'],
                            'state': ['estado', 'uf'],
                            'city': ['cidade', 'município']
                        }
                        
                        # Check if agent asks for this missing field
                        assert any(keyword in result.final_output.lower() for keyword in field_keywords[field])
            
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
    results = test_application_agent()
    
    # Exit with appropriate code (0 for success, 1 for failure)
    sys.exit(0 if results["failed"] == 0 else 1) 