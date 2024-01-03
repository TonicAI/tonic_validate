from typing import Dict
from openai import OpenAI


class OpenAIService:
    def __init__(self, model: str = "gpt-4-1106-preview") -> None:
        self.client = OpenAI()
        self.model = model
        self.cache: Dict[str, str] = {}

    def get_response(
        self,
        prompt: str,
        max_retries: int = 5,
    ) -> str:
        if prompt in self.cache:
            return self.cache[prompt]
        while max_retries > 0:
            try:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful assistant. Respond using markdown.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.0,
                )
                response = completion.choices[0].message.content
                if response is None:
                    raise Exception(
                        f"Failed to get message response from {self.model}, message does not exist"
                    )
                self.cache[prompt] = response
                return response
            except Exception as e:
                print(e)
                max_retries -= 1
        raise Exception(
            f"Failed to get completion response from {self.model}, max retires hit"
        )
