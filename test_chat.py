"""Quick debug: check vectorstore state after upload."""
import json
import urllib.request

API = "http://localhost:8000"

# Login
login_data = json.dumps({"email": "test@docutrust.com", "password": "Test1234!"}).encode()
req = urllib.request.Request(f"{API}/login", data=login_data, headers={"Content-Type": "application/json"})
resp = urllib.request.urlopen(req)
result = json.loads(resp.read())
token = result["access_token"]
user_id = result["user"]["id"]
print(f"[OK] Logged in as: {result['user']['email']} (id: {user_id})")

# List documents
req2 = urllib.request.Request(f"{API}/documents", headers={"Authorization": f"Bearer {token}"})
resp2 = urllib.request.urlopen(req2)
docs = json.loads(resp2.read())
print(f"\n[Documents] Found {len(docs)} documents:")
for d in docs:
    print(f"  - {d['filename']} (chunks: {d['chunks_count']}, status: {d['status']}, id: {d['id']})")

# Ask question via chat
print("\n--- Asking: 'What is the market size of AI in healthcare?' ---")
chat_data = json.dumps({"question": "What is the market size of AI in healthcare?", "top_k": 6}).encode()
chat_req = urllib.request.Request(
    f"{API}/chat",
    data=chat_data,
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
)
try:
    resp3 = urllib.request.urlopen(chat_req, timeout=120)
    chat_result = json.loads(resp3.read())
    print(f"\nRetrieval Score: {chat_result.get('retrieval_score', 'N/A')}")
    print(f"Web Search Used: {chat_result.get('web_search_used', 'N/A')}")
    print(f"Sources: {json.dumps(chat_result.get('sources', []), indent=2)}")
    print(f"\nAnswer:\n{chat_result.get('answer', 'N/A')}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
