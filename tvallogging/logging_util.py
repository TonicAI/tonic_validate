from typing import Any, Dict

from tvallogging.chat_objects import Benchmark, QuestionWithAnswer


def convert_benchmark_response_to_benchmark(
    benchmark_response: Dict[str, Any]
) -> Benchmark:
    """Convert benchmark response to Benchmark object."""
    id = benchmark_response["id"]
    questions_with_answers = benchmark_response["questions_with_answers"]
    question_with_answer_list = []
    for q_and_a_dict in questions_with_answers:
        if "context_list" not in q_and_a_dict:
            q_and_a_dict["context_list"] = None
        question_with_answer_list.append(
            QuestionWithAnswer(
                id=q_and_a_dict["id"],
                question=q_and_a_dict["question"],
                answer=q_and_a_dict["answer"],
                context_list=q_and_a_dict["context_list"],
            )
        )
    return Benchmark(id=id, question_with_answer_list=question_with_answer_list)
