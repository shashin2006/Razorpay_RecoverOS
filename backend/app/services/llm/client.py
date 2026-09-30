from openai import OpenAI

from app.core.config import settings


client = OpenAI(
    base_url=settings.nvidia_base_url,
    api_key=settings.nvidia_api_key,
)

NVIDIA_MODEL = settings.nvidia_model
NVIDIA_SAFETY_MODEL = settings.nvidia_safety_model