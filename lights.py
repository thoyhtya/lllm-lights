#!/usr/bin/python3
import json
import re
import requests
import time

# Services in local network
HUE_BRIDGE_IP = "192.168.71.133"
LLM_IP = "192.168.71.132"

def get_light_state(hue_bridge_ip=HUE_BRIDGE_IP):
  url = f'http://{hue_bridge_ip}:80/api/pL3shrHhGQAqNtA9H7ww4gvCstu6ZpKbB-ZOd7lU/lights'
  response = requests.get(url)
  #return response.json()
  return json.dumps(response.json())

# Example state = {"on": True, "xy": [0.64, 0.33], "sat": 255, "bri": 254}
def update_light_state(state, hue_bridge_ip=HUE_BRIDGE_IP):
  #print(state)
  #print(type(state))

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

  #for key in supported_keys:
  #  if key not in state_dict or (isinstance(state_dict[key], list) and len(state_dict[key]) == 0):
  #    # Set default values for unsupported parameters
  #    #if key == "on":
  #    #  state_dict[key] = False
  #    if key == "bri":
  #      state_dict[key] = 254
  #    elif key == "xy":
  #      state_dict[key] = [0.5, 0.5]
  #    elif key == "ct":
  #      state_dict[key] = 500
  #    elif key == "sat":
  #      state_dict[key] = 255
  #    elif key == "hue":
  #      state_dict[key] = 0
  #    #elif key == "colormode":
  #    #  state_dict[key] = "xy"
  #    elif key == "effect":
  #      state_dict[key] = "none"
  #    #elif key == "reachable":
  #    #  state_dict[key] = True

  #print(state_dict)

  url = f'http://{hue_bridge_ip}:80/api/pL3shrHhGQAqNtA9H7ww4gvCstu6ZpKbB-ZOd7lU/lights/1/state'
  headers = {'Content-Type': 'application/json'}
  response = requests.put(url, headers=headers, json=state_dict)
  return response.json()

def call_language_model():
  LLM_CHAT_ADDRESS = f'http://{LLM_IP}:1234/v1/chat/completions'

  #examplestate={"on": True, "xy": [0.64, 0.33], "sat": 255, "bri": 254}
  #print(examplestate)
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
Of course! I will send the command straight away! Is there anything else I can help you with?
LIGHTS_01_STATE={json.dumps({'on': 'True', 'xy': [0.64, 0.33], 'sat': 255, 'bri': 254})}
"""

  user_message = f"""
Could you please switch the light to some new color? Pick something nice!
"""

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

  #for msg in data["messages"]:
  #  print(f"{msg['role']}: {msg['content']}")

  response = requests.post(LLM_CHAT_ADDRESS, json=data)

  #print(response.text)
  print("assistant: ")
  message = response.json()["choices"][0]["message"]["content"]
  #  message = """
  #Sure!
  #LIGHTS_01_STATE={"on": "True", "xy": [0.27, 0.7], "sat": 255, "bri": 254}
  #"""
  print(message)

  pattern = r'LIGHTS_01_STATE=({.*})'
  match = re.search(pattern, message)

  if match:
      json_string = match.group(1)
      print("  [Updating state]")
      #print(json_string)
      api_response = update_light_state(json_string)
      #print("  State updated!")
      #print(f"  {api_response}")
  else:
      print("  [No match found]")

if __name__ == "__main__":
  whitestate = {"on": True, "bri": 254, "xy": [0.5, 0.5], "ct": 500}
  redstate = {"on": True, "bri": 254, "xy": [0.67, 0.33], "ct": 500}
  greenstate = {"on": True, "bri": 254, "xy": [0.33, 0.67], "ct": 500}
  bluestate = {"on": True, "bri": 254, "xy": [0.17, 0.07], "ct": 500}

  rgb_red = {"on": True, "rgb": [255, 0, 0]}
  rgb_green = {"on": True, "rgb": [0, 255, 0]}

  #print(update_light_state(bluestate))

  while True:
    call_language_model()
    time.sleep(10)
