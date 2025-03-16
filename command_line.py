from agents import Runner, function_tool, RunConfig, trace
import os
from pathlib import Path
import json
import asyncio 
from datetime import datetime
import sys
import uuid
from dotenv import load_dotenv

# Import agents from their modules
from ai_agents.simulator.simulator_agent import simulator_agent
from ai_agents.application.application_agent import application_agent
from ai_agents.questions.questions_agent import questions_agent
from ai_agents.triage.triage_agent import triage_agent

# Load environment variables from .env file
load_dotenv()

# Store the API key to ensure it's available throughout the session
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

@function_tool
def apply_for_real_estate_financing(full_name:str, cpf_number:str, date_of_birth:str, monthly_income:float, marital_status:str, person_type:str, property_value:float, state:str, city:str):
    """
    Applies for real estate financing based on the provided parameters.
    """
    # Log the simulation parameters (for debugging or record-keeping)
    print(f"Gerando aplicação de financiamento para:")
    print(f"- Nome: {full_name}")
    print(f"- CPF: {cpf_number}")
    print(f"- Data de nascimento: {date_of_birth}")
    print(f"- Renda mensal: {monthly_income}")
    print(f"- Estado civil: {marital_status}")
    print(f"- Tipo de pessoa: {person_type}")
    print(f"- Valor do imóvel: {property_value}")
    print(f"- Localização: {city}, {state}")
    
    # Get current date for submission date
    submission_date = datetime.now().strftime("%d/%m/%Y")
    
    return {
        "success": True,
        "message": "Sua aplicação de financiamento imobiliário foi recebida com sucesso!",
        "confirmation_code": f"FIN-{cpf_number[-4:]}",
        "bank": "CAIXA Econômica Federal",
        "submission_date": submission_date,
        "estimated_response_time": "5 dias úteis"
    }

@function_tool
def generate_financing_simulation(person_type:str, property_value:float, state:str, city:str):
    """
    Generates a real estate financing simulation based on the provided parameters.
    
    Args:
        person_type (str): Type of person ('física' or 'jurídica')
        property_value (float): Value of the property
        state (str): State where the property is located
        city (str): City where the property is located
        
    Returns:
        dict: Response containing the path to the PDF file and simulation details
    """

    # Path to the PDF file in the assets folder
    PDF_PATH = Path("assets/simulacao.pdf")
    # Create assets directory if it doesn't exist
    assets_dir = Path("assets")
    if not assets_dir.exists():
        assets_dir.mkdir(exist_ok=True)
        print(f"Created assets directory at {assets_dir.absolute()}")
    
    # Check if PDF exists
    if not PDF_PATH.exists():
        return {
            "success": False,
            "message": "Desculpe, o PDF de simulação de financiamento não está disponível no momento.",
            "error": "Arquivo PDF não encontrado em: " + str(PDF_PATH.absolute())
        }
    
    # Log the simulation parameters (for debugging or record-keeping)
    print(f"Gerando simulação de financiamento para:")
    print(f"- Tipo de pessoa: {person_type}")
    print(f"- Valor do imóvel: {property_value}")
    print(f"- Localização: {city}, {state}")
    
    # In a real implementation, you might use these parameters to generate a custom PDF
    # For now, we're just returning the existing PDF
    
    return {
        "success": True,
        "message": "Aqui está o seu documento de simulação de financiamento imobiliário:",
        "pdf_path": str(PDF_PATH),
        "simulation_details": {
            "person_type": person_type,
            "property_value": property_value,
            "state": state,
            "city": city
        }
    }

# Add interactive command line chat functionality
def interactive_chat():
    print("Bem-vindo ao chatbot de financiamento imobiliário da Loft!")
    print("Digite 'sair' para encerrar a conversa.")
    print("-------------------------------------------------")
    
    # Generate a unique thread ID for this conversation
    thread_id = str(uuid.uuid4())
    
    # Initialize result for the first turn
    result = None
    
    while True:
        user_input = input("\nVocê: ")
        
        if user_input.lower() == 'sair':
            print("Obrigado por usar nosso chatbot. Até logo!")
            break
        
        try:
            # Ensure API key is set for each request
            os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
            
            # Use trace to maintain conversation context
            with trace(workflow_name="loft-whatsapp-chatbot", group_id=thread_id):
                if result is None:
                    # First turn
                    result = Runner.run_sync(
                        starting_agent=triage_agent,
                        run_config=RunConfig(workflow_name="loft-whatsapp-chatbot"),
                        input=user_input,
                    )
                else:
                    # Subsequent turns - use previous result to maintain context
                    new_input = result.to_input_list() + [{"role": "user", "content": user_input}]
                    result = Runner.run_sync(
                        starting_agent=triage_agent,
                        run_config=RunConfig(workflow_name="loft-whatsapp-chatbot"),
                        input=new_input,
                    )
            
            # Print the agent's response
            print(f"\nAgente: {result.final_output}")
            
        except Exception as e:
            print(f"\nErro: {str(e)}")
            print("Ocorreu um erro ao processar sua mensagem. Por favor, tente novamente.")

# Add command-line execution
if __name__ == "__main__":
    if len(sys.argv) > 1:
        # If command line arguments are provided, use them as input
        try:
            # Ensure API key is set
            os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
            
            user_input = " ".join(sys.argv[1:])
            
            # Generate a unique thread ID for this conversation
            thread_id = str(uuid.uuid4())
            
            with trace(workflow_name="loft-whatsapp-chatbot", group_id=thread_id):
                output = Runner.run_sync(
                    starting_agent=triage_agent,
                    run_config=RunConfig(workflow_name="loft-whatsapp-chatbot"),
                    input=user_input,
                )
            
            print(output.final_output)
        except Exception as e:
            print(f"Erro: {str(e)}")
    else:
        # Otherwise, start interactive chat
        interactive_chat()