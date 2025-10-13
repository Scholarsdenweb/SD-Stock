import requests


def send_sms(api_key, message_id, variables_values, numbers='7903956216', sender_id="SCHDEN"):
    url = "https://www.fast2sms.com/dev/bulkV2"
    payload = {
    "sender_id": sender_id,
    "message": message_id,
    "variables_values": variables_values,
    "route": "dlt",
    "numbers": numbers 
    }

    headers = {
    "authorization": api_key,
    "Content-Type": "application/x-www-form-urlencoded",
    "Cache-Control": "no-cache",
    }

    response = requests.post(url, data=payload, headers=headers)

    # Optional: handle errors or print response
    if response.status_code == 200:
        print("SMS sent successfully:", response.json())
    else:
        print("Failed to send SMS:", response.status_code, response.text)
        
    return response    