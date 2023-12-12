from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class Context:
    """Context dataclass.

    Fields
    ------
    text: str
        Context text.
    metadata: dict
        Metadata associated with context.
    id: Optional[str]
        ID of context if being pulled from Tonic Validate.
    """

    text: str
    metadata: dict  # type: ignore
    id: Optional[str] = None


@dataclass
class QuestionWithAnswer:
    """Question with answer dataclass.

    Fields
    ------
    question: str
        Question text.
    answer: str
        Answer text.
    id: Optional[str]
        ID of question with answer if being pulled from Tonic Validate.
    context_list: Optional[List[Context]]
        List of context objects associated with question with answer.
    """

    question: str
    answer: str
    id: Optional[str] = None
    context_list: Optional[List[Context]] = None

    @staticmethod
    def from_json(json_dict: Dict[str, Any]) -> "QuestionWithAnswer":
        """Create QuestionWithAnswer object from JSON dictionary.

        Parameters
        ----------
        json_dict: Dict[str, Any]
            JSON dictionary to create QuestionWithAnswer object from. JSON schema:
            {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "answer": {"type": "string"},
                    "context_list": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "text": {"type": "string"},
                                "metadata": {"type": "object"},
                            },
                            "required": ["text"],
                        },
                    },
                },
                required: ["question", "answer"]
            }
        """
        if "context_list" in json_dict:
            context_list = json_dict["context_list"]
        else:
            context_list = None
        return QuestionWithAnswer(
            question=json_dict["question"],
            answer=json_dict["answer"],
            context_list=context_list,
        )


@dataclass
class Benchmark:
    """Benchmark dataclass.

    Fields
    ------
    question_with_answer_list: List[QuestionWithAnswer]
        List of question with answer objects associated with benchmark.
    id: Optional[str]
        ID of benchmark if being pulled from Tonic Validate.
    """

    question_with_answer_list: List[QuestionWithAnswer]
    id: Optional[str] = None

    @staticmethod
    def from_json_list(json_list: List[Dict[str, Any]]) -> "Benchmark":
        """Create Benchmark object from list of JSON dictionaries.

        Parameters
        ----------
        json_list: List[Dict[str, Any]]
            List of JSON dictionaries to create Benchmark object from. JSON schema:
            {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string"},
                        "answer": {"type": "string"},
                        "context_list": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "text": {"type": "string"},
                                    "metadata": {"type": "object"},
                                },
                                "required": ["text"],
                            },
                        },
                    },
                    required: ["question", "answer"]
                }
            }
        """
        question_with_answer_list = [
            QuestionWithAnswer.from_json(json_dict) for json_dict in json_list
        ]
        return Benchmark(question_with_answer_list=question_with_answer_list)
