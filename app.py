
# import os
# from flask import Flask, request, jsonify, render_template
# from flask_cors import CORS

# import requests
# from dotenv import load_dotenv
# from langchain_openai import ChatOpenAI
# from langchain_community.agent_toolkits import GmailToolkit
# from langchain import hub
# from langchain.agents import AgentExecutor, create_openai_functions_agent 
# from memory_store import SupabaseMemory
# from supabase import create_client, Client
# from langchain_community.tools.gmail.utils import (
#     build_resource_service,
#     get_gmail_credentials,
# )
# import openmeteo_requests

# import requests_cache
# import pandas as pd
# from retry_requests import retry



# app = Flask(__name__)
# CORS(app)



# # load env vars
# load_dotenv('.env.local')
# print("Environment variables loaded.")

# # get apis
# # openai api
# llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# print("ChatOpenAI initialized.")

# # langchain api
# api_key = os.getenv('LANGCHAIN_API_KEY')
# if not api_key:
#     raise ValueError("API key not provided")
# print("LangChain API key obtained.")

# # elevenlabs api
# elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
# voice_id = os.getenv("VOICE_ID")

# # supabase api
# supabase_url = os.getenv("SUPABASE_URL")
# supabase_key = os.getenv("SUPABASE_ANON_KEY")


# # init supabase client
# supabase: Client = create_client(supabase_url, supabase_key)
# print("Supabase client initialized.")

# # create memory
# memory = SupabaseMemory( supabase_client=supabase, table_name="conversations", session_id="default" )
# print("SupabaseMemory initialized.")

# # gmail credentials, api resource and toolkit
# credentials = get_gmail_credentials(
#     token_file="token.json",
#     scopes=["https://mail.google.com/"],
#     client_secrets_file="credentials.json",
# )
# print("Gmail credentials obtained.")

# api_resource = build_resource_service(credentials=credentials)
# print("API resource service built.")

# toolkit = GmailToolkit(api_resource=api_resource)
# print("GmailToolkit initialized.")

# # Setup the Open-Meteo API client with cache and retry on error
# cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
# retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
# openmeteo = openmeteo_requests.Client(session = retry_session)

# # tools = toolkit.get_tools()
# # tools

# # toolkit = GmailToolkit()



# # prompt

# # instructions = """You are an assistant."""
# # base_prompt = hub.pull("langchain-ai/openai-functions-template")
# # prompt = base_prompt.partial(instructions=instructions)
# # print("Prompt created.")

# # agent = create_openai_functions_agent(llm, toolkit.get_tools(), prompt, memory=memory)
# # print("OpenAI functions agent created with memory.")

# # agent_executor = AgentExecutor(
# #     agent=agent,
# #     tools=toolkit.get_tools(),
# #     verbose=False,
# # )
# # print("AgentExecutor initialized.")

# # response = agent_executor.invoke(
# #     {
# #         "input": "Get top 3 emails received today",
# #     }
# # )
# # print("AgentExecutor invoked.")
# # print("Response:", response)

# def create_agent():
#     instructions = """You are a personal assistant with access to email, calendar, and other personal information. 
#     Your tasks include:
#     1. Reading and summarizing emails
#     2. Drafting email responses
#     3. Managing calendar events and reminders
#     4. Providing weather updates
#     5. Checking and responding to messages
    
#     Always be concise and clear in your responses. When drafting emails, maintain a professional tone.
#     For calendar events, include time, date, and any important details."""
    
#     base_prompt = hub.pull("langchain-ai/openai-functions-template")
#     prompt = base_prompt.partial(instructions=instructions)
    
#     agent = create_openai_functions_agent(llm, toolkit.get_tools(), prompt, memory=memory)
#     return AgentExecutor(
#         agent=agent,
#         tools=toolkit.get_tools(),
#         verbose=True,
#         memory=memory
#     )


# # Routes
# @app.route("/")
# def index():
#     return render_template("index.html")

# @app.route("/process-input", methods=["POST"])
# def process_input():
#     data = request.json
#     user_input = data.get("input")
    
#     try:
#         agent_executor = create_agent()
#         response = agent_executor.invoke({"input": user_input})
        
#         # Store conversation in Supabase
#         supabase.table("conversations").insert({
#             "human_input": user_input,
#             "assistant_response": response["output"],
#             "timestamp": datetime.now().isoformat(),
#         }).execute()
        
#         return jsonify({
#             "success": True,
#             "response": response["output"],
#             "requiresAction": False  # Set to True if user needs to approve something
#         })
#     except Exception as e:
#         return jsonify({"success": False, "error": str(e)}), 500

# @app.route("/get-weather", methods=["GET"])
# def get_weather():
#     try:
#         lat = request.args.get("lat", default="52.52", type=str)
#         lon = request.args.get("lon", default="13.41", type=str)
#         timezone = request.args.get("timezone", default="auto", type=str)

#         # Configure weather API request
#         url = "https://api.open-meteo.com/v1/forecast"
#         params = {
#             "latitude": float(lat),
#             "longitude": float(lon),
#             "current": [
#                 "temperature_2m",
#                 "apparent_temperature",
#                 "is_day",
#                 "precipitation",
#                 "rain",
#                 "showers",
#                 "snowfall",
#                 "weather_code"
#             ],
#             "hourly": [
#                 "temperature_2m",
#                 "precipitation_probability",
#                 "weather_code"
#             ],
#             "daily": [
#                 "temperature_2m_max",
#                 "temperature_2m_min",
#                 "sunrise",
#                 "sunset",
#                 "precipitation_sum"
#             ],
#             "timezone": timezone
#         }

#         # Make API request
#         responses = openmeteo.weather_api(url, params=params)
#         response = responses[0]

#         # Process current weather
#         current = response.Current()
#         current_data = {
#             "temperature": current.Variables(0).Value(),
#             "feels_like": current.Variables(1).Value(),
#             "is_day": bool(current.Variables(2).Value()),
#             "precipitation": current.Variables(3).Value(),
#             "rain": current.Variables(4).Value(),
#             "showers": current.Variables(5).Value(),
#             "snowfall": current.Variables(6).Value(),
#             "weather_code": current.Variables(7).Value(),
#             "time": datetime.fromtimestamp(current.Time()).strftime('%Y-%m-%d %H:%M:%S')
#         }

#         # Process daily forecast
#         daily = response.Daily()
#         daily_data = {
#             "dates": [datetime.fromtimestamp(ts).strftime('%Y-%m-%d') for ts in daily.Variables(0).Times()],
#             "max_temp": daily.Variables(0).ValuesAsNumpy().tolist(),
#             "min_temp": daily.Variables(1).ValuesAsNumpy().tolist(),
#             "sunrise": [datetime.fromtimestamp(ts).strftime('%H:%M') for ts in daily.Variables(2).ValuesAsNumpy()],
#             "sunset": [datetime.fromtimestamp(ts).strftime('%H:%M') for ts in daily.Variables(3).ValuesAsNumpy()],
#             "precipitation_sum": daily.Variables(4).ValuesAsNumpy().tolist()
#         }

#         # Process hourly forecast (next 24 hours)
#         hourly = response.Hourly()
#         hourly_data = {
#             "times": [datetime.fromtimestamp(ts).strftime('%H:%M') for ts in hourly.Variables(0).Times()][:24],
#             "temperature": hourly.Variables(0).ValuesAsNumpy().tolist()[:24],
#             "precipitation_probability": hourly.Variables(1).ValuesAsNumpy().tolist()[:24],
#             "weather_code": hourly.Variables(2).ValuesAsNumpy().tolist()[:24]
#         }

#         # Weather code interpretation
#         weather_codes = {
#             0: "Clear sky",
#             1: "Mainly clear",
#             2: "Partly cloudy",
#             3: "Overcast",
#             45: "Foggy",
#             48: "Depositing rime fog",
#             51: "Light drizzle",
#             53: "Moderate drizzle",
#             55: "Dense drizzle",
#             61: "Slight rain",
#             63: "Moderate rain",
#             65: "Heavy rain",
#             71: "Slight snow fall",
#             73: "Moderate snow fall",
#             75: "Heavy snow fall",
#             77: "Snow grains",
#             80: "Slight rain showers",
#             81: "Moderate rain showers",
#             82: "Violent rain showers",
#             85: "Slight snow showers",
#             86: "Heavy snow showers",
#             95: "Thunderstorm",
#             96: "Thunderstorm with slight hail",
#             99: "Thunderstorm with heavy hail",
#         }

#         # Add weather descriptions
#         current_data["weather_description"] = weather_codes.get(current_data["weather_code"], "Unknown")
        
#         return jsonify({
#             "current": current_data,
#             "daily": daily_data,
#             "hourly": hourly_data,
#             "location": {
#                 "latitude": response.Latitude(),
#                 "longitude": response.Longitude(),
#                 "timezone": response.Timezone(),
#                 "elevation": response.Elevation()
#             }
#         })

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.route("/text-to-speech", methods=["POST"])
# def text_to_speech():
#     data = request.json
#     text = data.get("text")
    
#     headers = {
#         "xi-api-key": os.getenv("ELEVENLABS_API_KEY"),
#         "Content-Type": "application/json"
#     }
    
#     payload = {
#         "text": text,
#         "voice_id": os.getenv("VOICE_ID"),
#         "model_id": "eleven_monolingual_v1"
#     }
    
#     response = requests.post(
#         "https://api.elevenlabs.io/v1/text-to-speech",
#         headers=headers,
#         json=payload
#     )
    
#     if response.status_code == 200:
#         return Response(response.content, mimetype="audio/mpeg")
#     else:
#         return jsonify({"error": "Text-to-speech conversion failed"}), 500

# if __name__ == "__main__":
#     app.run(port=3000, debug=True)




import os
from datetime import datetime
from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS
import requests
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import GmailToolkit
from langchain import hub
from langchain.agents import AgentExecutor, create_openai_functions_agent
from supabase import create_client, Client
from langchain_community.tools.gmail.utils import build_resource_service, get_gmail_credentials
import openmeteo_requests
import requests_cache
from retry_requests import retry
from langchain.tools import Tool

# Initialize Flask app globally
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

class SimpleConversationStore:
    def __init__(self, supabase_client):
        self.supabase = supabase_client

    def store_conversation(self, human_input, assistant_response):
        try:
            self.supabase.table("conversations").insert({
                "human_input": human_input,
                "assistant_response": assistant_response,
                "timestamp": datetime.now().isoformat(),
            }).execute()
        except Exception as e:
            print(f"Error storing conversation: {str(e)}")
            pass

class APIClients:
    def __init__(self):
        self.llm = None
        self.toolkit = None
        self.openmeteo = None
        self.supabase = None
        self.initialized = False

    def initialize(self):
        if self.initialized:
            return True
            
        try:
            # Load environment variables
            load_dotenv('.env.local')
            print("Environment variables loaded.")

            # Initialize OpenAI
            self.llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            if not self.llm:
                raise ValueError("Failed to initialize ChatOpenAI")
            print("ChatOpenAI initialized.")

            # Initialize LangChain
            api_key = os.getenv('LANGCHAIN_API_KEY')
            if not api_key:
                raise ValueError("LangChain API key not provided")
            print("LangChain API key obtained.")

            # Initialize Supabase
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_ANON_KEY")
            if not all([supabase_url, supabase_key]):
                raise ValueError("Supabase credentials not provided")
            
            self.supabase = create_client(supabase_url, supabase_key)
            print("Supabase client initialized.")

            # Initialize Gmail
            try:
                credentials = get_gmail_credentials(
                    token_file="token.json",
                    scopes=["https://mail.google.com/"],
                    client_secrets_file="credentials.json",
                )
                api_resource = build_resource_service(credentials=credentials)
                self.toolkit = GmailToolkit(api_resource=api_resource)
                print("Gmail toolkit initialized.")
            except Exception as e:
                print(f"Error initializing Gmail: {str(e)}")
                self.toolkit = None

            # Initialize weather API client
            cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
            retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
            self.openmeteo = openmeteo_requests.Client(session=retry_session)
            
            self.initialized = True
            return True

        except Exception as e:
            print(f"Initialization error: {str(e)}")
            return False

def create_weather_tool(openmeteo):
    def get_current_weather(location="Berlin"):
        """Get current weather information for a location"""
        try:
            # Default coordinates for Berlin
            latitude = 52.52
            longitude = 13.41

            # Handle different location input formats
            if isinstance(location, str):
                if "," in location:  # If format is "lat,lon"
                    try:
                        lat, lon = location.split(",")
                        latitude = float(lat.strip())
                        longitude = float(lon.strip())
                    except ValueError:
                        # Use default coordinates if parsing fails
                        pass
            
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current": ["temperature_2m", "apparent_temperature", "is_day", 
                          "precipitation", "weather_code"],
                "timezone": "auto"
            }
            
            responses = openmeteo.weather_api(url, params=params)
            if not responses:
                return "Unable to get weather data"
                
            response = responses[0]
            current = response.Current()
            
            weather_codes = {
                0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
                45: "Foggy", 48: "Depositing rime fog", 51: "Light drizzle",
                53: "Moderate drizzle", 55: "Dense drizzle", 61: "Slight rain",
                63: "Moderate rain", 65: "Heavy rain", 71: "Slight snow fall",
                73: "Moderate snow fall", 75: "Heavy snow fall", 77: "Snow grains",
                80: "Slight rain showers", 81: "Moderate rain showers",
                82: "Violent rain showers", 85: "Slight snow showers",
                86: "Heavy snow showers", 95: "Thunderstorm",
                96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
            }
            
            weather_code = current.Variables(4).Value()
            weather_desc = weather_codes.get(weather_code, "Unknown weather condition")
            
            return f"Current weather in {location}: {weather_desc}. Temperature: {current.Variables(0).Value()}°C, " \
                   f"Feels like: {current.Variables(1).Value()}°C"
                   
        except Exception as e:
            return f"Error getting weather: {str(e)}"

    return Tool(
        name="get_weather",
        description="Get current weather information for a location. You can provide a city name or coordinates.",
        func=get_current_weather
    )

def create_agent(llm, toolkit, openmeteo):
    try:
        if not toolkit:
            raise ValueError("Gmail toolkit not initialized")
            
        instructions = """You are a personal assistant with access to email, calendar, and weather information. 
        Your tasks include:
        1. Reading and summarizing emails
        2. Drafting email responses
        3. Managing calendar events and reminders
        4. Providing weather updates
        5. Checking and responding to messages
        
        For weather requests:
        - When asked about weather without a location, use Berlin as the default location
        - You can provide coordinates in the format "latitude,longitude"
        - Or you can provide a city name
        
        Always be concise and clear in your responses. When drafting emails, maintain a professional tone.
        For calendar events, include time, date, and any important details."""
        
        base_prompt = hub.pull("langchain-ai/openai-functions-template")
        prompt = base_prompt.partial(instructions=instructions)
        
        tools = toolkit.get_tools()
        weather_tool = create_weather_tool(openmeteo)
        tools.append(weather_tool)
        
        agent = create_openai_functions_agent(llm, tools, prompt)
        
        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True
        )
    except Exception as e:
        print(f"Agent creation error: {str(e)}")
        raise

# Initialize API clients globally
api_clients = APIClients()
api_clients.initialize()

@app.route("/")
def index():
    try:
        return render_template("index.html")
    except Exception as e:
        print(f"Template rendering error: {str(e)}")
        return str(e), 500

@app.route("/process-input", methods=["POST"])
def process_input():
    if not all([api_clients.llm, api_clients.toolkit, api_clients.openmeteo]):
        return jsonify({"success": False, "error": "Services not properly initialized"}), 500
        
    try:
        data = request.json
        user_input = data.get("input")
        if not user_input:
            return jsonify({"success": False, "error": "No input provided"}), 400

        # Create agent with weather tool
        agent_executor = create_agent(api_clients.llm, api_clients.toolkit, api_clients.openmeteo)
        response = agent_executor.invoke({"input": user_input})
        
        # Store conversation
        if api_clients.supabase:
            conversation_store = SimpleConversationStore(api_clients.supabase)
            conversation_store.store_conversation(user_input, response["output"])
        
        return jsonify({
            "success": True,
            "response": response["output"],
            "requiresAction": False
        })
    except Exception as e:
        print(f"Process input error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/get-weather", methods=["GET"])
def get_weather():
    if not api_clients.openmeteo:
        return jsonify({"error": "Weather service not initialized"}), 500
        
    try:
        lat = request.args.get("lat", default="52.52", type=str)
        lon = request.args.get("lon", default="13.41", type=str)
        timezone = request.args.get("timezone", default="auto", type=str)

        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": float(lat),
            "longitude": float(lon),
            "current": ["temperature_2m", "apparent_temperature", "is_day", "precipitation",
                       "rain", "showers", "snowfall", "weather_code"],
            "hourly": ["temperature_2m", "precipitation_probability", "weather_code"],
            "daily": ["temperature_2m_max", "temperature_2m_min", "sunrise", "sunset",
                     "precipitation_sum"],
            "timezone": timezone
        }

        responses = api_clients.openmeteo.weather_api(url, params=params)
        if not responses:
            raise ValueError("No weather data received")
            
        response = responses[0]
        
        # Process current weather
        current = response.Current()
        current_data = {
            "temperature": current.Variables(0).Value(),
            "feels_like": current.Variables(1).Value(),
            "is_day": bool(current.Variables(2).Value()),
            "precipitation": current.Variables(3).Value(),
            "weather_code": current.Variables(7).Value(),
            "time": datetime.fromtimestamp(current.Time()).strftime('%Y-%m-%d %H:%M:%S')
        }

        return jsonify({
            "current": current_data,
            "location": {
                "latitude": response.Latitude(),
                "longitude": response.Longitude(),
                "timezone": response.Timezone()
            }
        })

    except Exception as e:
        print(f"Weather error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/text-to-speech", methods=["POST"])
def text_to_speech():
    try:
        elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
        # voice_id = os.getenv("VOICE_ID")
        voice_id = "iP95p4xoKVk53GoZ742B"
        
        print(f"Using voice ID: {voice_id}")
        
        if not all([elevenlabs_key, voice_id]):
            raise ValueError("ElevenLabs credentials not configured")
        
        # url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

            
        data = request.json
        text = data.get("text")
        if not text:
            raise ValueError("No text provided")
            
        # First verify the voice exists and is correct
        verify_url = f"https://api.elevenlabs.io/v1/voices"
        verify_headers = {
            "xi-api-key": elevenlabs_key
        }
        
        verify_response = requests.get(verify_url, headers=verify_headers)
        if verify_response.status_code == 200:
            voices = verify_response.json().get("voices", [])
            voice_found = False
            for voice in voices:
                if voice.get("voice_id") == voice_id:
                    print(f"Found voice: {voice.get('name')}")  # Debug log
                    voice_found = True
                    break
            if not voice_found:
                raise ValueError(f"Voice ID {voice_id} not found in available voices")
        
        # Use the verified voice for text-to-speech
        url = "https://api.elevenlabs.io/v1/text-to-speech/iP95p4xoKVk53GoZ742B"
        
        headers = {
            "Accept": "audio/mpeg",
            "xi-api-key": elevenlabs_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.71,
                "similarity_boost": 0.85,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }
        
        print("Sending TTS request with payload:", payload)
        
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            stream=True
        )
        
        if response.status_code == 200:
            return Response(response.content, mimetype="audio/mpeg")
        else:
            error_msg = f"ElevenLabs API error: {response.status_code}"
            try:
                error_details = response.json()
                error_msg += f" - {error_details.get('detail', '')}"
            except:
                pass
            raise ValueError(error_msg)
            
    except Exception as e:
        print(f"Text-to-speech error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=3000, debug=True)