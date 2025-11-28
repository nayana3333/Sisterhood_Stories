from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import os
import json
from django.utils import timezone

# Try to import OpenAI (both old and new API formats)
openai_client = None
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    try:
        import openai
        OPENAI_AVAILABLE = True
    except ImportError:
        openai = None
        OPENAI_AVAILABLE = False

class ChatbotView(TemplateView):
    template_name = "chatbot/chatbot.html"


@require_POST
def chat_api(request):
    text = (request.POST.get("text") or "").strip()
    if not text:
        return JsonResponse({"ok": False, "error": "empty"}, status=400)
    
    # Debug logging
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Chat API called with text: {text[:50]}")
    
    # Maintain short-term context in session
    history = request.session.get("chat_history", [])

    def detect_emotion(txt: str):
        t = (txt or "").lower()
        distress = any(k in t for k in ["hopeless", "give up", "end it", "suicide", "self harm", "hurt myself", "kill myself", "want to die"])
        if any(k in t for k in ["anxious", "panic", "anxiety", "stress", "overwhelmed", "scared", "worried", "nervous"]):
            return "anxious", distress
        if any(k in t for k in ["sad", "lonely", "down", "cry", "depressed", "low", "upset", "hurt", "disappointed"]):
            return "sad", distress
        if any(k in t for k in ["happy", "excited", "grateful", "proud", "joy", "celebrate", "great"]):
            return "happy", distress
        return "neutral", distress

    def detect_intent(txt: str):
        """Detect what the user is asking about"""
        t = txt.lower()
        intents = []
        if any(k in t for k in ["career", "resume", "interview", "job", "work", "professional", "salary", "promotion"]):
            intents.append("career")
        if any(k in t for k in ["relationship", "partner", "dating", "breakup", "marriage", "friend"]):
            intents.append("relationship")
        if any(k in t for k in ["health", "period", "pregnancy", "medical", "doctor", "symptom"]):
            intents.append("health")
        if any(k in t for k in ["mentor", "guidance", "advice", "help", "support"]):
            intents.append("support")
        if any(k in t for k in ["report", "abuse", "harassment", "unsafe", "danger"]):
            intents.append("report")
        if any(k in t for k in ["self care", "wellness", "meditation", "exercise", "fitness"]):
            intents.append("wellness")
        return intents

    emotion, distress = detect_emotion(text)
    intents = detect_intent(text)

    # Compose system prompt with empathy and safety guidance
    system_prompt = (
        "You are Sisterly AI — a warm, compassionate companion for women. "
        "Respond like a caring sister: empathetic, non-judgmental, supportive, and concise. "
        "Offer gentle guidance (breathing, grounding, journaling, self-care). "
        "Maintain short-term context from recent conversation turns. "
        "If distress appears, add a kind safety reminder and suggest professional help. "
        "Keep tone soft and encouraging. Use emojis sparingly (1-2 max). "
        "Be helpful with any topic: career, relationships, health, wellness, or general support. "
        "Keep responses under 200 words and conversational."
    )

    # Truncate history to last 8 messages (4 pairs) for better context
    recent = history[-8:]
    messages = [{"role": "system", "content": system_prompt}]
    for m in recent:
        messages.append(m)
    messages.append({"role": "user", "content": text})

    # Try OpenAI first for rich responses
    api_key = os.getenv("OPENAI_API_KEY")
    answer = None
    
    if api_key and OPENAI_AVAILABLE:
        try:
            # Try new OpenAI API format first
            try:
                global openai_client
                if openai_client is None:
                    openai_client = OpenAI(api_key=api_key)
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    max_tokens=300,
                    temperature=0.7,
                )
                answer = response.choices[0].message.content.strip()
            except (NameError, AttributeError, TypeError):
                # Fallback to old API format
                openai.api_key = api_key
                resp = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    max_tokens=300,
                    temperature=0.7,
                )
                answer = resp.choices[0].message["content"].strip()
        except Exception as e:
            # If OpenAI fails, use fallback
            answer = None

    # Enhanced local fallback with better responses
    if not answer:
        t = text.lower()
        
        # Handle distress first
        if distress:
            answer = (
                "Hey sister, I'm really concerned about you. You're not alone, and there are people who want to help. "
                "If you're in immediate danger, please call your local emergency services or a crisis hotline. "
                "You can also connect with a counselor here on our platform. Would you like me to help you find support?"
            )
        # Handle emotions
        elif emotion == "anxious":
            answer = (
                "I feel your anxiety, and that's completely valid. Let's try some grounding together: "
                "Take 4 deep breaths (inhale for 4, hold for 4, exhale for 6). "
                "Notice 5 things you can see, 4 things you can touch, 3 things you can hear, 2 things you can smell, and 1 thing you can taste. "
                "Would you like more calming techniques, or would it help to talk to a counselor?"
            )
        elif emotion == "sad":
            answer = (
                "Hey sister, I hear you and your feelings are valid. It's okay to not be okay. "
                "Sometimes a gentle walk, warm tea, journaling, or talking to someone can help. "
                "What feels manageable right now? I'm here to support you."
            )
        elif emotion == "happy":
            answer = (
                "That's wonderful! I'm so happy for you. Celebrating your wins, big or small, is important. "
                "Would you like to capture this moment? Maybe write it down or share it with someone you trust?"
            )
        # Handle specific intents
        elif "career" in intents:
            answer = (
                "I'd love to help with your career journey! Whether it's resume tips, interview prep, or navigating workplace challenges, "
                "I'm here. We can work on STAR method for behavioral questions, salary negotiation, or finding your next opportunity. "
                "What specific area would you like to focus on?"
            )
        elif "relationship" in intents:
            answer = (
                "Relationships can be complex, and I'm here to listen. Whether you're navigating dating, friendships, or family dynamics, "
                "your feelings matter. Would you like to talk through what's on your mind? I can also help you find resources or connect with a counselor."
            )
        elif "health" in intents:
            answer = (
                "Your health is important. While I can offer general wellness support and information, "
                "for specific medical concerns, I'd recommend consulting with a healthcare professional. "
                "I can help you find resources or talk through general wellness topics. What would be most helpful?"
            )
        elif "report" in intents:
            answer = (
                "Thank you for reaching out. Your safety is the top priority. "
                "If you're in immediate danger, please contact local authorities. "
                "You can report concerns through our platform's reporting system, and we have counselors available to support you. "
                "Would you like help accessing these resources?"
            )
        elif "wellness" in intents:
            answer = (
                "Self-care is so important! I can share ideas for meditation, gentle movement, nutrition tips, or mindfulness practices. "
                "What area of wellness interests you? Remember, self-care looks different for everyone—what feels good to you?"
            )
        elif "support" in intents:
            answer = (
                "I'm here to support you, sister. Whether you need someone to listen, guidance on next steps, "
                "or help connecting with resources, I've got you. What's on your mind? You can also explore our counseling services or community groups."
            )
        # General fallback
        else:
            answer = (
                "I'm here for you, sister. I'm listening and ready to help however I can. "
                "Whether you need support, advice, resources, or just someone to talk to, I'm here. "
                "What would be most helpful right now?"
            )

    # Add safety note if distress (but not already included)
    if distress and "immediate danger" not in answer.lower():
        safety = (
            "\n\n💜 Remember: If you're in immediate danger, please seek local help or call a crisis hotline. "
            "You can also connect with a counselor here: /counseling/"
        )
        answer = f"{answer}{safety}"

    # Save context
    history.append({"role": "user", "content": text})
    history.append({"role": "assistant", "content": answer})
    request.session["chat_history"] = history[-12:]  # keep last 12 turns (6 pairs)

    return JsonResponse({"ok": True, "answer": answer, "emotion": emotion})
