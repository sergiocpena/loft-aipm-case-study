from flask import Flask, request, Response
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import os

from agents import Agent, Runner, function_tool, RunConfig, trace

import os
from pathlib import Path
import json
import asyncio 
from datetime import datetime
import sys
import uuid
from dotenv import load_dotenv

print("Python path:", sys.path)
print("Trying to import agents...")
try:
    from agents import Agent, Runner, function_tool, RunConfig, trace
    print("Successfully imported agents")
except ImportError as e:
    print(f"Failed to import agents: {e}")
    raise

# Initialize Flask app
app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Initialize result as a global variable
result = None

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

simulator_agent = Agent(
    name="Simulator Agent",
    instructions="""
Você é um simulador de financiamento imobiliário. Sua função é coletar informações necessárias do usuário e gerar uma simulação de financiamento.

Colete todas as informações necessárias antes de prosseguir com a simulação. Se alguma informação estiver faltando, faça perguntas específicas para obtê-las.

### Informações Necessárias
- Tipo de pessoa: física ou jurídica
- Valor do imóvel
- Estado onde o imóvel está situado
- Cidade onde o imóvel está situado

# Passos

1. **Coletar Informações**: Verifique se você tem todas as informações necessárias. Se algum detalhe estiver faltando, pergunte ao usuário.
2. **Gerar Simulação**: Use os dados coletados para gerar a simulação de financiamento.
3. **Entregar PDF**: Após a simulação ser gerada, envie o arquivo PDF ao usuário.

# Formato de Saída

- Colete e verifique as informações acima.
- Use os dados fornecidos para gerar a simulação.
- Retorne o arquivo PDF ao usuário.

# Observações

- Todas as comunicações com o usuário devem ser em português do Brasil.
- Só prossiga com a simulação quando todas as informações necessárias estiverem completas.

# Função para Gerar Simulação

Quando tiver todas as informações, use a função `generate_financing_simulation` com os seguintes parâmetros:
- person_type: tipo de pessoa (fisica ou juridica)
- property_value: valor do imóvel (número)
- state: estado onde o imóvel está localizado
- city: cidade onde o imóvel está localizado

A função retornará um objeto com o caminho para o PDF e detalhes da simulação.
""",
    tools=[generate_financing_simulation]
)

application_agent = Agent(
    name="Application Agent",
    instructions="""
You are an application agent for real estate financing. Your role is to collect necessary user information to apply for financing on their behalf.

Collect all required information before proceeding with the application. If any information is missing, ask specific questions to obtain it.

### Required Information
- Full name
- CPF number
- Date of birth
- Monthly income
- Marital status
- Type of person: individual or corporate
- Property value
- State where the property is located
- City where the property is located

# Steps

1. **Collect Information**: Verify that you have all required information. If any detail is missing, ask the user to provide it.
2. **Apply for Financing**: Use the collected data to apply for financing.
3. **Deliver Confirmation**: Once the application is processed, send a confirmation to the user.
4. **Forward Result**: Forward the result of the `apply_for_real_estate_financing` function to the user.

# Output Format

- Collect and verify all the specified information.
- Use the provided data to apply for financing.
- Return confirmation to the user.
- Forward the function result to the user as the final output.

# Notes

- All communications with the user must be in Brazilian Portuguese.
- Do not proceed with the application until all required information is complete.

# Function to Apply for Financing

Once all information is gathered, use the function `apply_for_real_estate_financing` with the following parameters:
- full_name: Nome completo
- cpf_number: Número do CPF
- date_of_birth: Data de nascimento
- monthly_income: Renda mensal
- marital_status: Estado civil
- person_type: Tipo de pessoa (física ou jurídica)
- property_value: Valor do imóvel (número)
- state: Estado onde o imóvel está localizado
- city: Cidade onde o imóvel está localizado

The function will return an object with application confirmation details.
""",
    tools=[apply_for_real_estate_financing]
)

questions_agent = Agent(
    name="Questions Agent",
    instructions="""
   Answer questions about Brazilian real estate using simple, layman-friendly language in an exceptionally warm and engaging way. Respond in Brazilian Portuguese and brighten up each message with a fun emoji.

# Steps

1. **Understand the Question**: Grasp the user's curiosity about the Brazilian real estate scene and what they wish to learn.
2. **Do Some Research if Needed**: If uncertainty arises, pinpoint the source of the information you need.
3. **Write Your Answer**: Use clear, easy-to-understand Brazilian Portuguese to convey your answer.
4. **Add a Friendly Touch**: Reply as if you're chatting with an old friend, and sprinkle in one emoji to add a sparkle of fun.

# Output Format

Respond in one lively and conversational paragraph of Brazilian Portuguese, answering the question with a touch of friendliness and one emoji for extra cheer.

# Examples

**Example 1:**

- **User Question**: "Quais são os documentos necessários para comprar um imóvel no Brasil?"
- **Answer**: "Claro, vamos descomplicar! Para comprar um imóvel no Brasil, você precisará de documentos como RG, CPF, comprovante de renda e certidão de casamento, entre outros. 📄"

**Example 2:**

- **User Question**: "Como estão os preços dos imóveis em São Paulo atualmente?"
- **Answer**: "Nossa, o mercado está fervendo! Atualmente, os preços dos imóveis em São Paulo variam bastante dependendo da localização, mas o mercado está aquecido com uma tendência de alta nos valores. 🏙️"

# Notes

- Keep the tone friendly, bubbly, and easy to comprehend while sharing helpful insights.
- Choose emojis that add a fun element without overshadowing the key information.
"""
)

triage_agent = Agent(
    name="Triage Agent",
    instructions="""
Route the user to the correct agent.

# Available Agents

1. **Simulator Agent**: Forward to this agent when the user wants to simulate real estate financing. Examples:
   - "Quero simular um financiamento"
   - "Quanto ficaria o financiamento de um imóvel de R$ 500.000?"
   - "Preciso de uma simulação para comprar um apartamento"
   - "Simular financiamento"
   - "Simular"

2. **Application Agent**: Forward to this agent when the user wants to apply for real estate financing. Examples:
   - "Quero solicitar um financiamento"
   - "Como faço para dar entrada em um financiamento?"
   - "Preciso financiar um imóvel"

3. **Questions Agent**: Forward to this agent for general questions that don't fit into the above categories. Examples:
   - "Quais são os documentos necessários?"
   - "Qual é o horário de atendimento?"
   - "Quem é a Loft?"
   - "O que é CET?" (Custo Efetivo Total)
   - Perguntas sobre termos financeiros, documentação, ou informações gerais
""",
    handoffs=[simulator_agent, application_agent, questions_agent],
)

def send_whatsapp_message(to_number, message_body):
    """
    Send a WhatsApp message using Twilio.
    
    Args:
        to_number (str): The recipient's phone number in E.164 format (e.g., +1234567890)
        message_body (str): The content of the message to send
        
    Returns:
        str: The SID of the sent message if successful
    """
    # Get Twilio credentials from environment variables
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    from_number = os.environ.get('TWILIO_WHATSAPP_NUMBER')  # Your Twilio WhatsApp number
    
    # Initialize Twilio client
    client = Client(account_sid, auth_token)
    
    # Send the message
    message = client.messages.create(
        body=message_body,
        from_=f'whatsapp:{from_number}',
        to=f'whatsapp:{to_number}'
    )
    
    return message.sid

@app.route('/receive_whatsapp', methods=['POST'])
def receive_whatsapp_message():
    """
    Receive and process incoming WhatsApp messages via a webhook.
    
    This function should be set as the webhook URL in your Twilio WhatsApp configuration.
    
    Returns:
        Response: A TwiML response that can include a reply message
    """
    global result  # Declare that we're using the global result variable
    
    # Generate a unique thread ID for this conversation
    thread_id = str(uuid.uuid4())

    # Get the incoming message details
    incoming_msg = request.values.get('Body', '').strip()
    sender = request.values.get('From', '')
    
    # Create a response
    resp = MessagingResponse()
    
    # Create a new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Use trace to maintain conversation context
    with trace(workflow_name="loft-whatsapp-chatbot", group_id=thread_id):
        if result is None:
            # First turn
            result = Runner.run_sync(
                starting_agent=triage_agent,
                run_config=RunConfig(workflow_name="loft-whatsapp-chatbot"),
                input=incoming_msg,
            )
        else:
            # Subsequent turns - use previous result to maintain context
            new_input = result.to_input_list() + [{"role": "user", "content": incoming_msg}]
            result = Runner.run_sync(
                starting_agent=triage_agent,
                run_config=RunConfig(workflow_name="loft-whatsapp-chatbot"),
                input=new_input,
            )

    resp.message(result.final_output)
    
    return Response(str(resp), mimetype='text/xml')

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True)
