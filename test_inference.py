#!/usr/bin/env python3
"""
Simple script to test LLM service inference
"""
import requests
import json

def test_inference(question, max_tokens=100):
    url = "http://localhost:8000/v1/chat/completions"
    
    payload = {
        "model": "qwen2-7b-instruct-q6_k.gguf",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question}
        ],
        "temperature": 0.7,
        "max_tokens": max_tokens
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"🤖 Pregunta: {question}")
    print("Enviando solicitud al servicio LLM...")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract the assistant's response
            if result.get("choices") and len(result["choices"]) > 0:
                assistant_message = result["choices"][0]["message"]["content"]
                usage = result.get("usage", {})
                
                print(f"✅ Respuesta: {assistant_message}")
                print(f"📊 Tokens: {usage.get('prompt_tokens', 0)} prompt + {usage.get('completion_tokens', 0)} completion = {usage.get('total_tokens', 0)} total")
                print("-" * 50)
                return True
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def main():
    print("🚀 Iniciando pruebas de inferencia del servicio LLM")
    print("=" * 60)
    
    # Test 1: Pregunta simple
    test_inference("¿Cuál es la capital de Francia?", 50)
    
    # Test 2: Pregunta más compleja
    test_inference("Explica brevemente qué es la inteligencia artificial y menciona 3 aplicaciones prácticas.", 150)
    
    # Test 3: Pregunta en inglés
    test_inference("What are the main benefits of using renewable energy sources?", 120)
    
    # Test 4: Pregunta de programación
    test_inference("¿Puedes escribir una función en Python que calcule el factorial de un número?", 200)
    
    print("🎉 Pruebas completadas!")

if __name__ == "__main__":
    main()