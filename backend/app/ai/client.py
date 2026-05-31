from openai import OpenAI
from ..config import settings
import logging

logger = logging.getLogger(__name__)

_client = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        if not settings.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not set — AI calls will use mock responses")
            return None
        _client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _client
