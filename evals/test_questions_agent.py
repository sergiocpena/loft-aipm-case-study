import json
import sys
import os
import re
from openai import OpenAI

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_agents.questions.questions_agent import questions_agent
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

def contains_emoji(text):
    """Check if text contains at least one emoji"""
    # This is a simplified emoji detection - a more comprehensive solution would use a library
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F700-\U0001F77F"  # alchemical symbols
                               u"\U0001F780-\U0001F7FF"  # Geometric Shapes
                               u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
                               u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                               u"\U0001FA00-\U0001FA6F"  # Chess Symbols
                               u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
                               u"\U00002702-\U000027B0"  # Dingbats
                               u"\U000024C2-\U0001F251" 
                               "]+", flags=re.UNICODE)
    return bool(emoji_pattern.search(text))

def is_portuguese(text):
    """Check if text is likely in Portuguese"""
    # Common Portuguese words and patterns
    pt_indicators = [
        'é', 'são', 'está', 'estão', 'você', 'para', 'como', 'mas', 'ou', 'porque',
        'em', 'no', 'na', 'nos', 'nas', 'do', 'da', 'dos', 'das', 'um', 'uma', 'uns', 'umas',
        'muito', 'muita', 'muitos', 'muitas', 'pouco', 'pouca', 'poucos', 'poucas',
        'obrigado', 'obrigada', 'sim', 'não', 'talvez', 'sempre', 'nunca',
        'imóvel', 'imóveis', 'financiamento', 'comprar', 'vender', 'alugar'
    ]
    
    # Convert to lowercase for comparison
    text_lower = text.lower()
    
    # Check for Portuguese indicators
    for word in pt_indicators:
        if f" {word} " in f" {text_lower} " or text_lower.startswith(f"{word} ") or text_lower.endswith(f" {word}"):
            return True
    
    return False

def llm_judge_answers(expected_answer, actual_answer, question):
    """
    Use an LLM to judge if the actual answer is semantically equivalent to the expected answer
    Returns: (is_correct, explanation)
    """
    try:
        # Initialize the OpenAI client
        client = OpenAI()
        
        # Use OpenAI API to judge the answer
        prompt = f"""
        You are an expert judge evaluating answers to real estate questions in Portuguese.
        
        Question: {question}
        
        Expected Answer: {expected_answer}
        
        Actual Answer: {actual_answer}
        
        Is the actual answer semantically equivalent to the expected answer? 
        Consider that the answers don't need to be identical, but should convey the same key information.
        
        First, analyze both answers and identify their key points.
        Then, determine if the actual answer provides the same essential information as the expected answer.
        
        Respond with only "YES" or "NO" followed by a brief explanation.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert judge evaluating answers to real estate questions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=150
        )
        
        result = response.choices[0].message.content.strip()
        
        # Parse the result
        is_correct = result.upper().startswith("YES")
        explanation = result[3:] if result.upper().startswith("YES") else result[2:]
        
        return is_correct, explanation.strip()
    
    except Exception as e:
        print(colored(f"Error using LLM judge: {str(e)}", "red"))
        # Fallback to simple substring check
        return expected_answer.lower() in actual_answer.lower(), "Fallback to substring check due to LLM API error"

def test_questions_agent():
    # Load test cases
    with open('evals/questions_agent_test_dataset.json', 'r') as f:
        test_data = json.load(f)
    
    total_tests = len(test_data['test_cases'])
    passed_tests = 0
    failed_tests = []
    
    print(colored("\n===== STARTING QUESTIONS AGENT TESTS =====", "blue"))
    
    for test_case in test_data['test_cases']:
        test_name = test_case['name']
        print(colored(f"\nRunning test: {test_name}", "cyan"))
        
        try:
            # Test single input
            result = Runner.run_sync(
                starting_agent=questions_agent,
                run_config=RunConfig(workflow_name="test"),
                input=test_case['input']
            )
            
            # Check if the answer is semantically correct using LLM judge
            if 'expected_answer' in test_case:
                is_correct, explanation = llm_judge_answers(
                    test_case['expected_answer'], 
                    result.final_output,
                    test_case['input']
                )
                
                assert is_correct, f"Answer is not semantically equivalent: {explanation}"
                print(colored(f"  ✓ Answer evaluation: {explanation}", "green"))
            
            # Check if response is in Portuguese
            if test_case.get('expected_language') == 'pt-br':
                assert is_portuguese(result.final_output), "Response is not in Brazilian Portuguese"
                print(colored(f"  ✓ Language check: Response is in Portuguese", "green"))
            
            # Check if response contains an emoji
            if test_case.get('expected_emoji', False):
                assert contains_emoji(result.final_output), "Response doesn't contain any emoji"
                print(colored(f"  ✓ Emoji check: Response contains emoji", "green"))
            
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
    # Check if OpenAI API key is set
    if not os.environ.get("OPENAI_API_KEY"):
        print(colored("Warning: OPENAI_API_KEY environment variable not set. LLM judge will not work.", "yellow"))
        print(colored("Set it with: export OPENAI_API_KEY=your_api_key", "yellow"))
    
    results = test_questions_agent()
    
    # Exit with appropriate code (0 for success, 1 for failure)
    sys.exit(0 if results["failed"] == 0 else 1) 