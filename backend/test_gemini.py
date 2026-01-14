"""Test script to list available Gemini models"""
import os

# Hardcode the API key for testing
GOOGLE_API_KEY = "AIzaSyDFaKBy4uOFdfz9-PZ_sgk7Ldsu54CNgCw"

try:
    import google.generativeai as genai
    
    genai.configure(api_key=GOOGLE_API_KEY)
    
    print("Available Gemini models:")
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"  - {model.name}")
            
except ImportError:
    print("Installing google-generativeai...")
    import subprocess
    subprocess.run(["pip", "install", "google-generativeai"])
    print("Please run this script again.")
