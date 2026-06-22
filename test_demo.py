"""Create a sample PDF and test the DocuTrust API end-to-end."""
import json
import sys
import os

# Add the backend to path for reportlab
sys.path.insert(0, os.path.dirname(__file__))

# Step 1: Create a sample PDF using reportlab
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

pdf_path = os.path.join(os.path.dirname(__file__), "sample_ai_report.pdf")
doc = SimpleDocTemplate(pdf_path, pagesize=letter)
styles = getSampleStyleSheet()
story = []

story.append(Paragraph("Artificial Intelligence in Healthcare - 2025 Report", styles["Title"]))
story.append(Spacer(1, 20))

content = [
    ("Introduction", 
     "Artificial Intelligence (AI) is revolutionizing healthcare by improving diagnostic accuracy, "
     "personalizing treatment plans, and streamlining administrative processes. In 2025, the global "
     "AI in healthcare market reached $45.2 billion, growing at a compound annual growth rate of 44.9%. "
     "Machine learning algorithms can now detect diseases from medical images with accuracy rates "
     "exceeding 95%, surpassing human radiologists in certain specialties."),
    
    ("Key Applications",
     "The primary applications of AI in healthcare include: (1) Medical Imaging Analysis - Deep learning "
     "models analyze X-rays, MRIs, and CT scans to detect tumors, fractures, and other abnormalities. "
     "(2) Drug Discovery - AI reduces drug development timelines from 12 years to approximately 4 years "
     "by predicting molecular interactions. (3) Electronic Health Records - Natural language processing "
     "extracts insights from unstructured clinical notes. (4) Robotic Surgery - AI-assisted surgical "
     "robots perform minimally invasive procedures with sub-millimeter precision."),
    
    ("Clinical Decision Support",
     "AI-powered clinical decision support systems (CDSS) analyze patient data in real-time to recommend "
     "diagnoses and treatments. These systems integrate data from lab results, vital signs, genetic profiles, "
     "and medical history. Studies show CDSS reduces diagnostic errors by 30% and decreases hospital "
     "readmission rates by 25%. The Mayo Clinic reported a 40% improvement in early cancer detection "
     "using their AI screening platform."),
    
    ("Challenges and Ethics",
     "Despite the benefits, AI in healthcare faces challenges including data privacy concerns under HIPAA "
     "and GDPR regulations, algorithmic bias in training datasets, lack of interpretability in deep learning "
     "models, and resistance from healthcare professionals. The FDA has approved over 500 AI medical "
     "devices as of 2025, but regulatory frameworks continue to evolve."),
    
    ("Future Outlook",
     "By 2030, AI is expected to save the healthcare industry $150 billion annually. Emerging trends "
     "include federated learning for privacy-preserving model training, large language models for medical "
     "documentation, digital twins for personalized treatment simulation, and AI-driven mental health "
     "chatbots serving underserved communities. The integration of AI with wearable devices and IoT "
     "sensors will enable continuous patient monitoring and predictive health analytics."),
]

for title, text in content:
    story.append(Paragraph(title, styles["Heading2"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph(text, styles["BodyText"]))
    story.append(Spacer(1, 15))

doc.build(story)
print(f"[OK] Created sample PDF: {pdf_path}")

# Step 2: Register a test user
import urllib.request

API = "http://localhost:8000"

# Register
reg_data = json.dumps({"name": "Test User", "email": "test@docutrust.com", "password": "Test1234!"}).encode()
req = urllib.request.Request(f"{API}/register", data=reg_data, headers={"Content-Type": "application/json"})
try:
    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read())
    token = result["access_token"]
    print(f"[OK] Registered user: {result['user']['email']}")
except urllib.error.HTTPError as e:
    # User may already exist, try login
    body = e.read()
    print(f"[INFO] Registration: {body.decode()} - trying login...")
    login_data = json.dumps({"email": "test@docutrust.com", "password": "Test1234!"}).encode()
    req2 = urllib.request.Request(f"{API}/login", data=login_data, headers={"Content-Type": "application/json"})
    resp2 = urllib.request.urlopen(req2)
    result = json.loads(resp2.read())
    token = result["access_token"]
    print(f"[OK] Logged in as: {result['user']['email']}")

# Step 3: Upload the PDF
import mimetypes
boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
with open(pdf_path, "rb") as f:
    pdf_bytes = f.read()

body = (
    f"--{boundary}\r\n"
    f'Content-Disposition: form-data; name="files"; filename="sample_ai_report.pdf"\r\n'
    f"Content-Type: application/pdf\r\n\r\n"
).encode() + pdf_bytes + f"\r\n--{boundary}--\r\n".encode()

upload_req = urllib.request.Request(
    f"{API}/upload",
    data=body,
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    },
)
resp = urllib.request.urlopen(upload_req)
upload_result = json.loads(resp.read())
print(f"[OK] Uploaded PDF: {json.dumps(upload_result, indent=2)}")

# Step 4: Ask a question about the document
print("\n--- Asking question: 'What are the key applications of AI in healthcare?' ---\n")
chat_data = json.dumps({"question": "What are the key applications of AI in healthcare?"}).encode()
chat_req = urllib.request.Request(
    f"{API}/chat",
    data=chat_data,
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    },
)
try:
    resp = urllib.request.urlopen(chat_req, timeout=120)
    chat_result = json.loads(resp.read())
    print(f"Answer: {chat_result.get('answer', 'N/A')}")
    print(f"\nRetrieval Score: {chat_result.get('retrieval_score', 'N/A')}")
    print(f"Corrected: {chat_result.get('corrected', 'N/A')}")
    if chat_result.get('citations'):
        print(f"\nCitations:")
        for c in chat_result['citations']:
            print(f"  - {c.get('filename', '')} (page {c.get('page', '?')}): {c.get('snippet', '')[:100]}...")
except Exception as e:
    print(f"Chat error: {e}")
    import traceback
    traceback.print_exc()
