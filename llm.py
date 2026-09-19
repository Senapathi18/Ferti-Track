# modules/llm.py
# ══════════════════════════════════════════════════════════════
# FertiTrack LLM Module — Powered by Google Gemini (FREE)
# ══════════════════════════════════════════════════════════════
#
# SETUP:
#   1. Get free key: https://aistudio.google.com/app/apikey
#   2. pip install google-generativeai
#   3. Add to config.py: GEMINI_API_KEY = "AIzaSy..."
#   4. Restart app
#
# USAGE:
#   from modules.llm import FertiLLM
#   llm = FertiLLM()
#   reply = llm.ask("Who owes me money?", context=shop_data)
# ══════════════════════════════════════════════════════════════

import os
import sys
import datetime

# Ensure the project root (parent of modules/) is on sys.path so
# `from config import GEMINI_API_KEY` works even when this file is
# run directly (e.g. `python modules/llm.py`) and not just when
# imported from the main app entry point.
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

try:
    import google.generativeai as genai
    GEMINI_INSTALLED = True
except ImportError:
    GEMINI_INSTALLED = False

DEFAULT_MODEL       = "gemini-2.5-flash"   
DEFAULT_MAX_TOKENS  = 1024
DEFAULT_TEMPERATURE = 0.3

BASE_SYSTEM_PROMPT = """You are FertiBot, the AI assistant built into
FertiTrack fertilizer shop software in Andhra Pradesh, India.

You know:
- All FertiTrack features and how to use them
- Indian fertilizer GST rules (5% Urea/DAP/NPK, 18% pesticides)
- Andhra Pradesh farming seasons and patterns
- Telugu language (reply in Telugu if user writes Telugu)

Always use Rs. for money. Be friendly and give clear steps.
Never make up data - only use what is given to you."""


def _get_api_key():
    try:
        from config import GEMINI_API_KEY
        if GEMINI_API_KEY and not GEMINI_API_KEY.startswith("AIzaSy-your"):
            return GEMINI_API_KEY
    except Exception:
        pass
    return os.environ.get("GEMINI_API_KEY", "")


def get_llm_status():
    if not GEMINI_INSTALLED:
        return {
            "ready": False,
            "reason": "Library not installed.\nRun: python -m pip install google-generativeai",
            "model": None
        }
    key = _get_api_key()
    if not key:
        return {
            "ready": False,
            "reason": "GEMINI_API_KEY missing in config.py.\nGet free key: https://aistudio.google.com/app/apikey",
            "model": None
        }
    return {"ready": True, "reason": "Ready", "model": DEFAULT_MODEL}


def is_llm_ready():
    return get_llm_status()["ready"]


def get_setup_instructions():
    status = get_llm_status()
    if status["ready"]:
        return f"Gemini AI ready. Model: {status['model']}"
    return (
        "SETUP GEMINI AI:\n"
        "1. Run: python -m pip install google-generativeai\n"
        "2. Get FREE key: https://aistudio.google.com/app/apikey\n"
        "3. Add to config.py: GEMINI_API_KEY = 'AIzaSy...'\n"
        "4. Restart FertiTrack"
    )


class FertiLLM:
    """
    FertiTrack AI powered by Google Gemini (Free).

    Usage:
        llm = FertiLLM()
        reply = llm.ask("What are today's sales?", context=data)
    """

    def __init__(self, system_prompt=None, temperature=DEFAULT_TEMPERATURE):
        self.system_prompt = system_prompt or BASE_SYSTEM_PROMPT
        self.temperature   = temperature
        self.history       = []
        self._model        = None
        self._chat         = None

        if GEMINI_INSTALLED:
            key = _get_api_key()
            if key:
                try:
                    genai.configure(api_key=key)
                    self._model = genai.GenerativeModel(
                        model_name=DEFAULT_MODEL,
                        system_instruction=self.system_prompt,
                        generation_config=genai.GenerationConfig(
                            temperature=self.temperature,
                            max_output_tokens=DEFAULT_MAX_TOKENS,
                        )
                    )
                    self._chat = self._model.start_chat(history=[])
                except Exception as e:
                    print(f"Gemini init error: {e}")

    def ask(self, question, context=None, remember=True):
        """Ask Gemini a question. Returns the answer as a string."""
        status = get_llm_status()
        if not status["ready"]:
            return f"AI not available:\n{status['reason']}"
        if not self._chat:
            return "AI connection failed. Check GEMINI_API_KEY in config.py"

        try:
            if context and len(self.history) == 0:
                message = f"SHOP DATA:\n{context}\n\n---\n\nQuestion: {question}"
            elif context:
                message = f"[Data refreshed: {datetime.date.today()}]\n\n{question}"
            else:
                message = question

            if remember:
                self.history.append({"role": "user", "content": question})

            response = self._chat.send_message(message)
            reply    = response.text

            if remember:
                self.history.append({"role": "assistant", "content": reply})

            return reply
        except Exception as e:
            return self._handle_error(e)

    def quick_ask(self, question, context=None):
        """One-shot question with no memory saved."""
        if not GEMINI_INSTALLED or not self._model:
            return get_setup_instructions()
        try:
            msg       = f"SHOP DATA:\n{context}\n\n---\n\n{question}" if context else question
            temp_chat = self._model.start_chat(history=[])
            response  = temp_chat.send_message(msg)
            return response.text
        except Exception as e:
            return self._handle_error(e)

    def clear_history(self):
        """Clear conversation memory and start fresh."""
        self.history = []
        if GEMINI_INSTALLED and self._model:
            try:
                self._chat = self._model.start_chat(history=[])
            except Exception:
                pass

    def analyse_sales(self, sales_data):
        """Analyses sales data and gives key insights."""
        return self.quick_ask(
            "Analyse this sales data:\n"
            "1. Total revenue\n2. Best selling product\n"
            "3. Any concerns\n4. One business tip\n"
            "Be brief and simple.",
            context=sales_data
        )

    def generate_report_summary(self, report_data, report_type="sales"):
        """Generates a plain English summary of a report."""
        prompts = {
            "sales":  "Summarise this sales report in 3 sentences. Mention total, top customer, trend.",
            "stock":  "Summarise this stock. What is low, expiring, needs ordering?",
            "credit": "Who owes money? List top 3 and total outstanding.",
            "pl":     "Summarise profit and loss. Give revenue, profit, margin.",
        }
        return self.quick_ask(
            prompts.get(report_type, "Summarise this data briefly."),
            context=report_data
        )

    def answer_software_question(self, question):
        """Answers how-to questions about FertiTrack features."""
        return self.quick_ask(
            f"How to question about FertiTrack software: {question}\n"
            "Give numbered step-by-step instructions. Be brief."
        )

    def translate_to_telugu(self, text):
        """Translates text to Telugu."""
        return self.quick_ask(
            f"Translate to Telugu script only:\n\n{text}"
        )

    def check_gst_rate(self, product_name, category):
        """Returns GST rate and HSN code for a fertilizer product."""
        return self.quick_ask(
            f"GST rate and HSN code for:\n"
            f"Product: {product_name}, Category: {category}\n"
            "Give: rate %, HSN code, reason."
        )

    def suggest_reorder(self, stock_data):
        """Suggests which products to reorder."""
        return self.quick_ask(
            "Based on this stock:\n"
            "1. Which products need urgent reorder?\n"
            "2. How much to order?\n"
            "3. Which are overstocked?",
            context=stock_data
        )

    def predict_seasonal_demand(self, sales_history):
        """Predicts demand based on AP farming seasons."""
        return self.quick_ask(
            "Based on sales history and AP farming seasons "
            "(Kharif: June-Oct, Rabi: Nov-Mar), predict:\n"
            "1. High demand products next month?\n"
            "2. How much stock to prepare?\n"
            "3. Seasonal advice?",
            context=sales_history
        )

    def _handle_error(self, error):
        err = str(error).lower()
        if "api_key" in err or "invalid" in err or "401" in err:
            return "Invalid API key. Check GEMINI_API_KEY in config.py\nGet key: https://aistudio.google.com/app/apikey"
        if "quota" in err or "429" in err:
            return "Free tier limit reached. Wait 1 minute and try again."
        if "network" in err or "connection" in err:
            return "No internet connection. Check WiFi and try again."
        if "blocked" in err or "safety" in err:
            return "Question blocked by safety filter. Please rephrase."
        return f"AI Error: {str(error)[:200]}"


def quick_question(question, context=None):
    """Ask Gemini one quick question without creating a class."""
    return FertiLLM().quick_ask(question, context=context)


if __name__ == "__main__":
    print("\n" + "="*50)
    print("  FertiTrack LLM — Google Gemini Test")
    print("="*50)

    status = get_llm_status()
    print(f"\nStatus: {'READY' if status['ready'] else 'NOT READY'}")

    if not status["ready"]:
        print(f"\n{get_setup_instructions()}")
    else:
        print(f"Model : {status['model']}")
        print("Testing connection...")
        llm   = FertiLLM()
        reply = llm.quick_ask(
            "Say hello as FertiBot inside FertiTrack "
            "fertilizer software in Andhra Pradesh. 2 sentences only."
        )
        print(f"\nGemini says:\n{reply}")
        print("\n" + "="*50)
        print("  Gemini Working Correctly!")
        print("="*50)