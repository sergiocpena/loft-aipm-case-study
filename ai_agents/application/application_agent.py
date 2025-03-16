from ai_agents import Agent, function_tool
from datetime import datetime
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

if __name__ == "__main__":
    print("Application Agent loaded successfully")