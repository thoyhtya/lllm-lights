#!/usr/bin/python3
import json
import re
import requests
import time

# Services in local network
HUE_BRIDGE_IP = "192.168.71.133"
HUE_API = f"http://{HUE_BRIDGE_IP}:80/api"
LLM_IP = "192.168.71.132"
LLM_CHAT_ADDRESS = f"http://{LLM_IP}:1234/v1/chat/completions"

def get_light_state():
  url = f"{HUE_API}/pL3shrHhGQAqNtA9H7ww4gvCstu6ZpKbB-ZOd7lU/lights"
  response = requests.get(url)
  return json.dumps(response.json())

# Example state = {"on": True, "xy": [0.64, 0.33], "sat": 255, "bri": 254}
def update_light_state(state):

  # Parse state parameter into a dictionary if it's not already one
  if isinstance(state, str):
    try:
      state_dict = json.loads(state)
    except json.JSONDecodeError as e:
      print(f"Invalid JSON: {state} Exception: {e}")
      return None
  else:
      state_dict = state

  # this string vs boolean shit breaks stuff
  # json.loads() expects "True" to be quoted in the json-string
  # boolean True is required by requests
  state_dict["on"] = True

  # Ensure the state dictionary has the required keys
  supported_keys = ["on", "bri", "xy", "ct", "sat", "hue", "effect", "rbg"]
  for key in list(state_dict.keys()):
    if key not in supported_keys:
      del state_dict[key]

  url = f"{HUE_API}/pL3shrHhGQAqNtA9H7ww4gvCstu6ZpKbB-ZOd7lU/lights/1/state"
  headers = {'Content-Type': 'application/json'}
  response = requests.put(url, headers=headers, json=state_dict)
  return response.json()

def call_language_model(chat=None):
  system_prompt = f"""
You are a helpful, smart, kind, and efficient AI assistant.
You always fulfill the user's requests to the best of your ability.
You have the ability to monitor status of Philips Hue lights in the local network.
Response from Philips Hue Bridge /api/<localbridge>/lights API:
'''
{get_light_state()}
'''
You also have the ability to update the status of light ID 1.
If requested, set a new state by producing a string in the format 'LIGHTS_01_STATE=<newstate>',
where newstate is the json parameter passed to PUT /api/<localbridge>/lights/1/state
Example response:
Of course! This color should be exactly what you requested.
LIGHTS_01_STATE={json.dumps({'on': 'True', 'xy': [0.64, 0.33], 'sat': 255, 'bri': 254})}
"""

  user_message = f"""
Could you please switch the light color to something completely different?
Explain your decision.
"""

  if chat:
    user_message = chat

  data = {
    "model": "bartowski/Meta-Llama-3.1-8B-Instruct-GGUF",
    "messages": [
      { "role": "system", "content": system_prompt },
      { "role": "user", "content": user_message },
    ],
    "temperature": 0.7,
    "max_tokens": -1,
    "stream": False
  }

  response = requests.post(LLM_CHAT_ADDRESS, json=data)
  message = response.json()["choices"][0]["message"]["content"]

  #print(response.text) # model info, token usage, parameters
  print("AI: ")
  print(message)
  print()
  print()

  newstate = parse_commands(message)
  if newstate:
    print(f"  [SYSTEM: Updating state]")
    print(f"  [{newstate}]")
    execute_commands(newstate)
  else:
    print("  [SYSTEM: No actions]")
  print()
  print()

def parse_commands(message):
  pattern = r'LIGHTS_01_STATE=({.*})'
  match = re.search(pattern, message)

  if match:
      return match.group(1)
  else:
      return None

def execute_commands(new_state):
  update_light_state(new_state)

if __name__ == "__main__":
  whitestate = {"on": True, "bri": 254, "xy": [0.5, 0.5], "ct": 500}
  redstate = {"on": True, "bri": 254, "xy": [0.67, 0.33], "ct": 500}
  greenstate = {"on": True, "bri": 254, "xy": [0.33, 0.67], "ct": 500}
  bluestate = {"on": True, "bri": 254, "xy": [0.17, 0.07], "ct": 500}

  rgb_red = {"on": True, "rgb": [255, 0, 0]}
  rgb_green = {"on": True, "rgb": [0, 255, 0]}

  #print(update_light_state(bluestate))

  while True:
    chat = input("HUMAN: ")
    call_language_model(chat)
