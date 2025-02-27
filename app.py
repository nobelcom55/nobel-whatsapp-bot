from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# WhatsApp API Credentials (Move to Environment Variables for Security)
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "EAAN2ch6L1T8BO6nzp5JxCXnvwVnaN3GxLZA0Bbw5G3ZCICE38ezquHrlZC8BL4UUFsyiNpJcmKsZA8dYuYC27bDuX6ZCyGPBghbdCgoVWeV55Ehm8KkcbOAk5oZCLWNHQBdZBq4CX4ZBgsEQOPbp6FRbdEnr1jnYYu3dm7luAAcaZBceP2Oc5y96PDyvZCbbcrZAoZCU0AlPkt1Qc54ZC6xitFpXLrSurAIE0oJeoUNIZD")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "655162247669603")

# Langflow API Credentials
LANGFLOW_API_URL = os.getenv("LANGFLOW_API_URL", "https://api.langflow.astra.datastax.com/lf/fb36b4bb-1733-4ceb-9aa6-6d89dda82bde/api/v1/run/bd427161-9e86-4d3d-9c89-39e77bf4c1ec?stream=false")
LANGFLOW_AUTH_TOKEN = os.getenv("LANGFLOW_AUTH_TOKEN", "AstraCS:hvzlnuszyXeFzdJIriwaITUF:0d4d497cf012454fa7d5dda3af2380621537ed6e5da527dcadeb6a9b8bd5719d")

# Meta Webhook Verification Token (Must match the one entered in Meta Developer Console)
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "nobel1234")

# ✅ Webhook Verification for Meta
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    token_sent = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    if token_sent == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403

# ✅ Handling WhatsApp Messages & Forwarding to Langflow
@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    data = request.json
    print("📩 Incoming WhatsApp Message:", data)  # Debugging Log

    if "messages" in data:
        user_message = data["messages"][0]["text"]["body"]
        sender_id = data["messages"][0]["from"]

        # ✅ Prepare payload for Langflow API
        langflow_payload = {
            "input_value": user_message,
            "output_type": "chat",
            "input_type": "chat",
            "tweaks": {
                "ChatInput-x8JWf": {},
                "ChatOutput-Kpapr": {},
                "Memory-3EJnx": {},
                "Prompt-VLpMd": {},
                "OpenAIModel-zWeAk": {},
                "AstraDBChatMemory-KTyj9": {}
            }
        }

        # ✅ Send message to Langflow
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LANGFLOW_AUTH_TOKEN}"
        }

        response = requests.post(LANGFLOW_API_URL, json=langflow_payload, headers=headers)
        response_json = response.json()

        # ✅ Extract chatbot reply
        bot_reply = response_json.get("output", "Sorry, I didn't understand that.")

        # ✅ Send reply back to WhatsApp (Using Meta's format)
        whatsapp_headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        whatsapp_payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": sender_id,
            "type": "text",
            "text": {
                "body": bot_reply
            }
        }

        # ✅ Send message to WhatsApp & print response
        response = requests.post(f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages", 
                                 headers=whatsapp_headers, json=whatsapp_payload)

        print("🔹 WhatsApp API Response:", response.status_code, response.text)  # Debugging log

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(port=5000)
