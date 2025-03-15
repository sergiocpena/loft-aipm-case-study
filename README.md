# Real Estate Financing Assistant

An Agentic Workflow for Real Estate Financing.

## Features

- Q&A for Real Estate Financing
- Fake simulation of a real estate financing
- Fake application for a real estate financing

## Setup

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with:
   ```
   OPENAI_API_KEY=your_openai_api_key
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_WHATSAPP_NUMBER=your_twilio_whatsapp_number
   ```
4. Run the application: `python test-wpp.py`
5. Use ngrok to expose your local server: `ngrok http 5000`
6. Configure your Twilio webhook URL to point to your ngrok URL + `/receive_whatsapp`

## Usage

- To send a message: Use the `send_whatsapp_message(to_number, message_body)` function
- To receive messages: Messages will be processed by the webhook endpoint

## License

[Your chosen license]