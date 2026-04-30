"""AI Service Module - OpenRouter/OpenAI Integration"""

import logging
from typing import Optional, List, Dict
import json
import numpy as np
from config.settings import settings
import openai

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI operations using OpenRouter/OpenAI API"""

    def __init__(self):
        self.api_key = settings.openrouter_api_key or settings.openai_api_key
        self.model = settings.ai_model or "openai/gpt-3.5-turbo"
        self.base_url = "https://openrouter.ai/api/v1" if settings.openrouter_api_key else None
        self.client = None
        if self.api_key:
            self.client = openai.AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url or "https://api.openai.com/v1"
            )

    async def generate_summary(self, text: str, max_length: int = 500) -> Optional[str]:
        """Generate a concise summary of the given text"""
        if not self.client:
            logger.warning("AI client not configured")
            return None
        try:
            prompt = f"Please summarize the following text in a concise and informative way, in the same language as the original text:\n\n{text[:4000]}"
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_length,
                temperature=0.5,
            )
            summary = response.choices[0].message.content.strip()
            logger.info("Summary generated successfully")
            return summary
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return None

    async def generate_embeddings(self, text: str) -> Optional[List[float]]:
        """Generate embeddings vector for the given text"""
        if not self.client:
            logger.warning("AI client not configured")
            return None
        try:
            embedding_model = "openai/text-embedding-3-small"
            response = await self.client.embeddings.create(
                model=embedding_model,
                input=text[:8000]
            )
            embedding = response.data[0].embedding
            logger.info("Embeddings generated successfully")
            return embedding
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            return None

    async def classify_book(self, title: str, description: str, author: str = "") -> Optional[Dict[str, str]]:
        """Classify a book by suggesting category, tags, and language"""
        if not self.client:
            logger.warning("AI client not configured")
            return None
        try:
            prompt = (
                f"You are a librarian. Given the book details, suggest a category (e.g., programming, history, self development, etc.), "
                f"a list of tags (comma separated), and the primary language of the book.\n"
                f"Book title: {title}\nAuthor: {author}\nDescription: {description[:500]}\n\n"
                f"Respond ONLY in JSON format: {{\"category\": \"...\", \"tags\": \"...\", \"language\": \"...\"}}"
            )
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            result = json.loads(response.choices[0].message.content)
            logger.info(f"Book classified: {result}")
            return result
        except Exception as e:
            logger.error(f"Error classifying book: {str(e)}")
            return None

    async def answer_question(self, question: str, context: str) -> Optional[str]:
        """Answer a question based on a given context (e.g., book content)"""
        if not self.client:
            logger.warning("AI client not configured")
            return None
        try:
            prompt = f"Based on the following text, answer the question. If the answer cannot be found, say 'I don't know'.\n\nText: {context[:3000]}\n\nQuestion: {question}\nAnswer:"
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.2,
            )
            answer = response.choices[0].message.content.strip()
            logger.info("Question answered successfully")
            return answer
        except Exception as e:
            logger.error(f"Error answering question: {str(e)}")
            return None

    async def generate_recommendations(self, user_history: List[str]) -> Optional[List[str]]:
        """Generate book recommendations based on user history (list of book IDs/descriptions)"""
        if not self.client:
            logger.warning("AI client not configured")
            return None
        try:
            history_str = "\n".join([f"- {item}" for item in user_history[-10:]])
            prompt = f"A user has read the following books:\n{history_str}\n\nSuggest 3 similar books (just titles) that the user might like. Respond as a JSON list of strings."
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            recs = json.loads(content).get("recommendations", [])
            return recs
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return None

    def similarity_score(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            if not embedding1 or not embedding2:
                return 0.0
            arr1 = np.array(embedding1)
            arr2 = np.array(embedding2)
            dot_product = np.dot(arr1, arr2)
            norm1 = np.linalg.norm(arr1)
            norm2 = np.linalg.norm(arr2)
            if norm1 == 0 or norm2 == 0:
                return 0.0
            return float(dot_product / (norm1 * norm2))
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
