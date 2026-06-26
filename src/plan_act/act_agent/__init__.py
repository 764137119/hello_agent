from crewai import LLM

from crewai import LLM

locl_llm = LLM(
    model="openai/gpt-4o",
    api_key="your-api-key",
    base_url="https://api.openai.com/v1",  # Optional custom endpoint
    organization="org-...",  # Optional organization ID
    project="proj_...",  # Optional project ID
    temperature=0.7,
    max_tokens=4000,
    max_completion_tokens=4000,  # For newer models
    top_p=0.9,
    frequency_penalty=0.1,
    presence_penalty=0.1,
    stop=["END"],
    seed=42,  # For reproducible outputs
    stream=True,  # Enable streaming
    timeout=60.0,  # Request timeout in seconds
    max_retries=3,  # Maximum retry attempts
    logprobs=True,  # Return log probabilities
    top_logprobs=5,  # Number of most likely tokens
    reasoning_effort="medium"  # For o1 models: low, medium, high
)