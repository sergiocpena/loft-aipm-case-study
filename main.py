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

# Import agents from their modules
from ai_agents.simulator.simulator_agent import simulator_agent
from ai_agents.application.application_agent import application_agent
from ai_agents.questions.questions_agent import questions_agent
from ai_agents.triage.triage_agent import triage_agent

# Add these imports at the top of your file
from utils.ping_service import init_ping_service
from routes.health import health_bp

def create_app():
    app = Flask(__name__)
    
    # Register the health check blueprint
    app.register_blueprint(health_bp)
    
    return app

# Create the app
app = create_app()

# Load environment variables from .env file
load_dotenv()

# Initialize the ping service directly
# This will run when the module is loaded by Gunicorn
try:
    init_ping_service(interval_minutes=15)
    print("Ping service initialized")
except Exception as e:
    print(f"Error initializing ping service: {str(e)}")

# Initialize result as a global variable
result = None

# Store the API key to ensure it's available throughout the session
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

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

# Run the app if this file is executed directly
if __name__ == '__main__':
    app.run(debug=True)
