#!/usr/bin/env python3
"""Samantha AI — Personal agent that executes real actions on your computer."""

import os
import sys
import logging
import traceback
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.config import config_manager
from core.session import SessionManager
from core.memory import MemoryManager, memory_manager
from core.intent import IntentClassifier, intent_classifier
from core.commands import CommandProcessor
from core.status import StatusIndicator
from core.prompts import prompt_manager
from voice.recognition import SpeechRecognitionService, speech_recognition_service
from voice.tts import TTSService, tts_service
from actions.browser import browser_action
from actions.media import control_spotify
from actions.messaging import whatsapp_action
from ai.provider import LLMProvider

# Configure logging
logging_level = config_manager.get('logging.level', 'INFO')
logging_format = config_manager.get('logging.format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.basicConfig(
    level=getattr(logging, logging_level, logging.INFO),
    format=logging_format,
)
logger = logging.getLogger("Samantha")


class SamanthaAgent:
    """Main agent class — listens, understands, and acts."""

    def __init__(self):
        logger.info("Initializing Samantha AI Agent...")

        self.session = SessionManager()
        self.llm = LLMProvider()
        self.command_processor = CommandProcessor()

        # Voice I/O
        self.recognizer = speech_recognition_service
        self.tts = tts_service

        # Memory & intent
        self.memory = memory_manager
        self.intent_classifier = intent_classifier

        self.running = False
        logger.info(f"Samantha initialized. LLM provider: {self.llm.provider_name}")

    def run(self):
        """Main loop — listen, classify, act, respond."""
        self.running = True
        print("\n" + "=" * 50)
        print("  SAMANTHA AI AGENT")
        print(f"  LLM: {self.llm.provider_name}")
        print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("  Say 'Hey Samantha' or type a command")
        print("  Say 'quit' or 'exit' to stop")
        print("=" * 50 + "\n")

        if self.tts:
            self.tts.speak("Hello! I'm Samantha, your AI assistant. How can I help?")

        while self.running:
            try:
                # Listen for input (voice or keyboard fallback)
                user_input = self._get_input()
                if not user_input:
                    continue

                # Check for exit
                if user_input.lower().strip() in ['quit', 'exit', 'bye', 'goodbye']:
                    self._shutdown()
                    break

                # Classify intent
                intent = self.intent_classifier.classify(user_input)
                logger.info(f"Input: '{user_input}' | Intent: {intent}")

                # Track usage
                self.memory.add_command(user_input, intent.get('category', 'general'))

                # Process command
                response = self._process(user_input, intent)

                # Respond
                print(f"\nSamantha: {response}\n")
                if self.tts:
                    self.tts.speak(response)

            except KeyboardInterrupt:
                self._shutdown()
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                logger.error(traceback.format_exc())
                print(f"\nSorry, something went wrong: {e}\n")

    def _get_input(self) -> str:
        """Get user input via voice or keyboard."""
        try:
            if self.recognizer:
                text = self.recognizer.listen()
                if text:
                    print(f"\nYou: {text}")
                    return text
        except Exception as e:
            logger.debug(f"Voice input failed, falling back to keyboard: {e}")

        # Keyboard fallback
        try:
            return input("You: ").strip()
        except EOFError:
            return ""

    def _process(self, user_input: str, intent: dict) -> str:
        """Process user input and execute appropriate action."""
        category = intent.get('category', 'general')

        # Direct action categories
        if category == 'browser':
            return browser_action(user_input)
        elif category == 'spotify' or category == 'music':
            return control_spotify(user_input)
        elif category == 'whatsapp' or category == 'messaging':
            return whatsapp_action(user_input)
        elif category == 'system':
            from actions.system import system_action
            return system_action(user_input)

        # For general/conversational queries, use LLM
        system_prompt = prompt_manager.get_prompt('assistant')
        result = self.llm.query(user_input, system_prompt)

        # Execute any structured commands from LLM
        if result.get('commands'):
            self.command_processor.execute(result['commands'])

        return result.get('text', "I'm not sure how to help with that.")

    def _shutdown(self):
        """Clean shutdown."""
        self.running = False
        print("\nGoodbye! Samantha shutting down.")
        if self.tts:
            self.tts.speak("Goodbye!")
        self.session.save()
        logger.info("Samantha shut down cleanly.")


def main():
    """Entry point."""
    print(f"\nStarting Samantha AI Agent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        agent = SamanthaAgent()
        agent.run()
    except Exception as e:
        logger.error(f"Critical error: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
