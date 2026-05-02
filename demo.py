"""
demo.py — CivicPath Local Demo Script
======================================
This script demonstrates the CivicPath API endpoints running locally.
Make sure the server is running (`uvicorn main:app --reload --port 8000`) before executing this script.
"""

import httpx
import asyncio
import json

API_BASE = "http://localhost:8000"

async def run_demo():
    print("🚀 Starting CivicPath Local Demo\n")
    
    async with httpx.AsyncClient() as client:
        # 1. Check Health
        print("1️⃣ Checking Server Health...")
        try:
            res = await client.get(f"{API_BASE}/health")
            print(f"Status {res.status_code}:", res.json(), "\n")
        except Exception as e:
            print(f"❌ Server not running. Please start it with: uvicorn main:app --port 8000\nError: {e}\n")
            return

        # 2. Check Google Services Registry
        print("2️⃣ Fetching Google Services Manifest...")
        res = await client.get(f"{API_BASE}/google-services")
        data = res.json()
        print(f"Status {res.status_code}: Total Services Integrated -> {data.get('total_google_services')}")
        print("Services include:", ", ".join(list(data.get('services', {}).keys())[:3]), "...\n")

        # 3. Simulate Journey Creation (Demo Mode will fallback to demo_data.py)
        print("3️⃣ Starting an Election Journey...")
        payload = {
            "state": "california",
            "is_registered": False,
            "is_first_time": True,
            "election_type": "general",
            "language": "en"
        }
        res = await client.post(f"{API_BASE}/journey/start", json=payload)
        journey = res.json()
        print(f"Status {res.status_code}: Journey created with ID '{journey.get('journey_id', 'demo-id')}'")
        print(f"Generated {len(journey.get('steps', []))} personalized steps.\n")

        # 4. Simulate AI Chat
        print("4️⃣ Asking AI Assistant a question...")
        chat_payload = {
            "message": "When is the deadline to register in California?",
            "journey_id": journey.get("journey_id"),
            "language": "en"
        }
        res = await client.post(f"{API_BASE}/chat", json=chat_payload)
        chat_reply = res.json()
        print(f"Status {res.status_code}: AI Assistant Reply:\n> {chat_reply.get('response', 'No response')}\n")

    print("🎉 Demo complete! The fallback demo data works perfectly for testing without real API keys.")

if __name__ == "__main__":
    asyncio.run(run_demo())
