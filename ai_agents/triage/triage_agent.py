from ai_agents import Agent

# Update imports to match your directory structure
from ai_agents.simulator.simulator_agent import simulator_agent
from ai_agents.application.application_agent import application_agent
from ai_agents.questions.questions_agent import questions_agent

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
    # Access the agent instances from their modules
    handoffs=[simulator_agent, application_agent, questions_agent],
)

if __name__ == "__main__":
    print("Triage Agent loaded successfully")