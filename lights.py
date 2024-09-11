#!/usr/bin/python3
import requests

def get_light_state(ip_address):
    url = f'http://{ip_address}:80/api/pL3shrHhGQAqNtA9H7ww4gvCstu6ZpKbB-ZOd7lU/lights'
    response = requests.get(url)
    return response.json()

def update_light_state(ip_address, state):
    url = f'http://{ip_address}:80/api/pL3shrHhGQAqNtA9H7ww4gvCstu6ZpKbB-ZOd7lU/lights/1/state'
    headers = {'Content-Type': 'application/json'}
    response = requests.put(url, headers=headers, json=state)
    return response.json()

# Example usage:
#ip_address = "192.168.71.133"
#light_state = get_light_state(ip_address)
#print(light_state)

#new_state = {"on": True, "xy": [0.64, 0.33], "sat": 255, "bri": 254}
#response = update_light_state(ip_address, new_state)
#print(response)

def call_language_model():
  localip = "192.168.71.132"
  url = f'http://{localip}:1234/v1/chat/completions'

  system_prompt = f"""
You are a helpful, smart, kind, and efficient AI assistant.
You always fulfill the user's requests to the best of your ability.
"""
  user_message = f"""
Introduce yourself.
"""

  print(f"System: {system_prompt}")
  print(f"User: {user_message}")

  data = {
    "model": "bartowski/Meta-Llama-3.1-8B-Instruct-GGUF",
    "messages": [
      { "role": "system", "content": system_prompt },
      { "role": "user", "content": user_message }
    ],
    "temperature": 0.7,
    "max_tokens": -1,
    "stream": False
  }

  response = requests.post(url, json=data)

  #print(response.text)
  print("Assistant: ")
  print(response.json()["choices"][0]["message"]["content"])

if __name__ == "__main__":
    call_language_model()
