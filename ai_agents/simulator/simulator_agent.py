from ai_agents import Agent, function_tool
from pathlib import Path
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

if __name__ == "__main__":
    print("Simulator Agent loaded successfully")