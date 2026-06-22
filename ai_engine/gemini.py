import json
import urllib.request
import urllib.parse
from django.conf import settings

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

def call_gemini(prompt: str) -> str:
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return ""
    
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 512}
    }).encode('utf-8')
    
    url = f"{GEMINI_URL}?key={api_key}"
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'}, method='POST')
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            return data['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception as e:
        print(f"Gemini error: {e}")
        return ""


def analyze_ticket(title: str, description: str) -> dict:
    """Run all AI analyses on a ticket."""
    combined = f"Title: {title}\nDescription: {description}"
    
    prompt = f"""Analyze this support ticket and respond ONLY with valid JSON:

{combined}

Return exactly this JSON structure:
{{
  "category": "one of: authentication, billing, technical, feature_request, bug_report, account, performance, other",
  "priority": "one of: low, medium, high, critical",
  "sentiment": "one of: positive, neutral, negative, very_negative",
  "escalation_required": true or false,
  "summary": "1-2 sentence summary of the issue",
  "solution": "suggested solution or next steps in 2-3 sentences",
  "department": "one of: backend, frontend, devops, billing, security, general"
}}

Base priority on urgency/impact. Base escalation on sentiment being very_negative or issue being critical."""

    result = call_gemini(prompt)
    
    if not result:
        return _fallback_analysis(title, description)
    
    # Strip markdown fences if present
    result = result.strip()
    if result.startswith('```'):
        result = result.split('\n', 1)[1].rsplit('```', 1)[0].strip()
    
    try:
        data = json.loads(result)
        return {
            'category': data.get('category', 'other'),
            'priority': data.get('priority', 'medium'),
            'sentiment': data.get('sentiment', 'neutral'),
            'escalation_required': bool(data.get('escalation_required', False)),
            'ai_summary': data.get('summary', ''),
            'ai_solution': data.get('solution', ''),
            'suggested_department': data.get('department', 'general'),
        }
    except json.JSONDecodeError:
        return _fallback_analysis(title, description)


def _fallback_analysis(title: str, description: str) -> dict:
    """Rule-based fallback when Gemini is unavailable."""
    text = (title + ' ' + description).lower()
    
    category = 'other'
    for kw, cat in [('login','authentication'),('password','authentication'),('pay','billing'),('charge','billing'),('bug','bug_report'),('error','technical'),('slow','performance'),('feature','feature_request')]:
        if kw in text:
            category = cat
            break
    
    priority = 'high' if any(w in text for w in ['urgent','critical','cannot','broken','down']) else 'medium'
    sentiment = 'negative' if any(w in text for w in ['terrible','worst','awful','horrible','frustrated']) else 'neutral'
    
    return {
        'category': category,
        'priority': priority,
        'sentiment': sentiment,
        'escalation_required': sentiment == 'very_negative',
        'ai_summary': f"Customer reported: {title[:100]}",
        'ai_solution': "Please investigate the issue and provide appropriate support based on the ticket details.",
        'suggested_department': 'general',
    }
