from typing import Dict, List

import pytest
from tonic_validate.classes import Benchmark, LLMResponse, Run
from tonic_validate.classes.llm_response import CallbackLLMResponse
from tonic_validate.metrics import (
    AnswerConsistencyBinaryMetric,
    AnswerConsistencyMetric,
    AnswerContainsPiiMetric,
    AnswerMatchMetric,
    AnswerSimilarityMetric,
    AugmentationAccuracyMetric,
    AugmentationPrecisionMetric,
    BinaryMetric,
    ContainsTextMetric,
    ContextContainsPiiMetric,
    ContextLengthMetric,
    DuplicationMetric,
    HateSpeechContentMetric,
    LatencyMetric,
    RegexMetric,
    ResponseLengthMetric,
    RetrievalPrecisionMetric,
)
from tonic_validate import ValidateScorer


def check_run(
    expected_metric_scores: Dict[str, float],
    scorer: ValidateScorer,
    llm_responses: List[LLMResponse],
) -> None:
    run = scorer.score_responses(llm_responses)
    for metric_name, expected_score in expected_metric_scores.items():
        assert run.overall_scores[metric_name] == expected_score
        for item in run.run_data:
            assert item.scores[metric_name] == expected_score


@pytest.mark.parametrize("answer, expected_score", [("Fido", 1.0), ("Rex", 0.0)])
def test_answer_consistency_binary_metric(answer, expected_score):
    metric = AnswerConsistencyBinaryMetric()
    benchmark = Benchmark(
        questions=["What is the name of Ryan's dog?"],
        answers=["Fido"],
    )
    llm_response = LLMResponse(
        llm_answer=answer,
        llm_context_list=[
            "Fido is the name of Ryan's dog.",
            "Ryan has a dog named Fido.",
        ],
        benchmark_item=benchmark.items[0],
    )
    scorer = ValidateScorer([metric])
    check_run({metric.name: expected_score}, scorer, [llm_response])


@pytest.mark.parametrize(
    "answer, expected_score",
    [
        ("Fido is his dog and Whiskers is his cat.", 1.0),
        ("Fido is his dog and Rex is his cat.", 0.5),
        ("Spot is his dog and Rex is his cat.", 0.0),
    ],
)
def test_answer_consistency_metric(answer, expected_score):
    metric = AnswerConsistencyMetric()
    benchmark = Benchmark(
        questions=["What is the name of Ryan's dog and cat?"],
        answers=["Fido is his dog and Whiskers is his cat."],
    )
    llm_response = LLMResponse(
        llm_answer=answer,
        llm_context_list=[
            "Fido is the name of Ryan's dog.",
            "Ryan has a cat named Whiskers.",
        ],
        benchmark_item=benchmark.items[0],
    )
    scorer = ValidateScorer([metric])
    check_run({metric.name: expected_score}, scorer, [llm_response])


@pytest.mark.parametrize(
    "answer, expected_score",
    [
        ("Los Angeles 90001", 1.0),
        ("Los Angeles", 1.0),
        ("I am not sure.", 0.0),
    ],
)
def test_answer_contains_pii_metric(answer, expected_score):
    metric = AnswerContainsPiiMetric(["LOCATION_CITY", "LOCATION_ZIP"])
    benchmark = Benchmark(
        questions=["Where does Ryan live?"],
        answers=["Los Angeles 90001"],
    )
    llm_response = LLMResponse(
        llm_answer=answer,
        llm_context_list=[],
        benchmark_item=benchmark.items[0],
    )
    scorer = ValidateScorer([metric])
    check_run({metric.name: expected_score}, scorer, [llm_response])


@pytest.mark.parametrize(
    "answer, case_match, expected_score",
    [
        ("paris", False, 1.0),
        ("Paris", False, 1.0),
        ("Paris", True, 1.0),
        ("paris", True, 0.0),
        ("I am not sure.", False, 0.0),
        ("I am not sure.", True, 0.0),
    ],
)
def test_answer_match_metric(answer, case_match, expected_score):
    metric = AnswerMatchMetric("Answer Match", "Paris", case_match)
    benchmark = Benchmark(
        questions=["Where is the Eiffel Tower?"],
        answers=["Paris"],
    )
    llm_response = LLMResponse(
        llm_answer=answer,
        llm_context_list=[],
        benchmark_item=benchmark.items[0],
    )
    scorer = ValidateScorer([metric])
    check_run({metric.name: expected_score}, scorer, [llm_response])


@pytest.mark.parametrize(
    "answer, score_checker",
    [
        (
            "Paris is the capital of France and Madrid is the capital of Spain.",
            lambda x: x == 5.0,
        ),
        (
            "Paris is the capital of France and Washington DC is the capital of Spain.",
            lambda x: x < 5.0 and x > 0.0,
        ),
        ("I am not sure.", lambda x: x == 0.0),
    ],
)
def test_answer_similarity_metric(answer, score_checker):
    metric = AnswerSimilarityMetric()
    benchmark = Benchmark(
        questions=["What are the capitals of France and Spain?"],
        answers=["Paris is the capital of France and Madrid is the capital of Spain."],
    )
    llm_response = LLMResponse(
        llm_answer=answer,
        llm_context_list=[],
        benchmark_item=benchmark.items[0],
    )
    scorer = ValidateScorer([metric])
    run = scorer.score_responses([llm_response])
    assert score_checker(run.overall_scores[metric.name])
    for item in run.run_data:
        assert score_checker(item.scores[metric.name])


@pytest.mark.parametrize(
    "answer, expected_score",
    [
        ("Paris is the capital of France and Madrid is the capital of Spain.", 1.0),
        # (
        #     "Paris is the capital of France and Washington DC is the capital of Spain.",
        #     0.5,
        # ),
        ("Paris is the capital of France.", 0.5),
        ("I am not sure.", 0.0),
    ],
)
def test_augmentation_accuracy_metric(answer, expected_score):
    metric = AugmentationAccuracyMetric()
    benchmark = Benchmark(
        questions=["What are the capitals of France and Spain?"],
        answers=["Paris is the capital of France and Madrid is the capital of Spain."],
    )
    llm_response = LLMResponse(
        llm_answer=answer,
        llm_context_list=[
            "Paris is the capital of France.",
            "Madrid is the capital of Spain.",
        ],
        benchmark_item=benchmark.items[0],
    )
    scorer = ValidateScorer([metric])
    check_run({metric.name: expected_score}, scorer, [llm_response])


@pytest.mark.parametrize(
    "answer, expected_score",
    [
        ("Paris is the capital of France and Madrid is the capital of Spain.", 1.0),
        # (
        #     "Paris is the capital of France and Madrid is the capital of Spain. A dog is a pet.",
        #     0.5,
        # ),
        ("Paris is the capital of France.", 0.5),
        ("Paris is the capital of France and a dog is a pet.", 0.5),
        ("A dog is a pet", 0.0),
        ("I am not sure", 0.0),
    ],
)
def test_augmentation_precision_metric(answer, expected_score):
    metric = AugmentationPrecisionMetric()
    benchmark = Benchmark(
        questions=["What are the capitals of France and Spain?"],
        answers=["Paris is the capital of France and Madrid is the capital of Spain."],
    )
    llm_response = LLMResponse(
        llm_answer=answer,
        llm_context_list=[
            "Paris is the capital of France.",
            "Madrid is the capital of Spain.",
            "A dog is a pet.",
        ],
        benchmark_item=benchmark.items[0],
    )
    scorer = ValidateScorer([metric])
    check_run({metric.name: expected_score}, scorer, [llm_response])


@pytest.mark.parametrize(
    "answer, callback, expected_score",
    [("N/A", lambda x, y: True, 1.0), ("N/A", lambda x, y: False, 0.0)],
)
def test_binary_metric(answer, callback, expected_score):
    # TODO: Fix checking for callback params
    metric = BinaryMetric("Binary Metric", callback)
    benchmark = Benchmark(
        questions=["What is the name of Ryan's dog?"],
        answers=["Fido"],
    )
    llm_response = LLMResponse(
        llm_answer=answer,
        llm_context_list=[
            "Fido is the name of Ryan's dog.",
            "Ryan has a dog named Fido.",
        ],
        benchmark_item=benchmark.items[0],
    )
    scorer = ValidateScorer([metric])
    check_run({metric.name: expected_score}, scorer, [llm_response])


@pytest.mark.parametrize(
    "answer, case_sensitive, expected_score",
    [
        ("The capital of France is paris.", False, 1.0),
        ("The capital of France is paris.", True, 0.0),
        ("I am not sure.", False, 0.0),
    ],
)
def test_contains_text_metric(answer, case_sensitive, expected_score):
    metric = ContainsTextMetric("Contains Text", "Paris", case_sensitive)
    benchmark = Benchmark(
        questions=["What is the capital of France?"],
        answers=["Paris"],
    )
    llm_response = LLMResponse(
        llm_answer=answer,
        llm_context_list=[],
        benchmark_item=benchmark.items[0],
    )
    scorer = ValidateScorer([metric])
    check_run({metric.name: expected_score}, scorer, [llm_response])


@pytest.mark.parametrize(
    "context, expected_score",
    [
        (["Ryan lives in Los Angeles at zip code 90001", "Ryan likes dogs"], 1.0),
        (["Ryan lives in Los Angeles. He likes the city.", "Ryan likes dogs"], 1.0),
        (["Ryan lives in zip code 90001", "Ryan likes dogs"], 1.0),
        (["Ryan likes dogs", "Ryan likes cats"], 0.0),
    ],
)
def test_context_contains_pii_nmetric(context, expected_score):
    metric = ContextContainsPiiMetric(["LOCATION_CITY", "LOCATION_ZIP"])
    benchmark = Benchmark(
        questions=["Where does Ryan live?"],
        answers=["Los Angeles 90001"],
    )
    llm_response = LLMResponse(
        llm_answer="Los Angeles 90001",
        llm_context_list=context,
        benchmark_item=benchmark.items[0],
    )
    scorer = ValidateScorer([metric])
    check_run({metric.name: expected_score}, scorer, [llm_response])


def generate_string(length):
    return "a" * length


@pytest.mark.parametrize(
    "context, expected_score",
    [
        ([generate_string(6), generate_string(6)], 1.0),
        ([generate_string(6), generate_string(7)], 1.0),
        ([generate_string(5), generate_string(5)], 1.0),
        ([generate_string(10), generate_string(10)], 1.0),
        ([generate_string(11), generate_string(11)], 0.0),
        ([generate_string(6), generate_string(11)], 0.0),
        ([generate_string(2), generate_string(2)], 0.0),
        ([generate_string(1), generate_string(1)], 0.0),
        ([generate_string(0), generate_string(0)], 0.0),
    ],
)
def test_context_length_metric(context, expected_score):
    metric = ContextLengthMetric("Context Length", 5, 10)
    benchmark = Benchmark(
        questions=["Where does Ryan live?"],
        answers=["Los Angeles 90001"],
    )
    llm_response = LLMResponse(
        llm_answer="Los Angeles 90001",
        llm_context_list=context,
        benchmark_item=benchmark.items[0],
    )
    scorer = ValidateScorer([metric])
    check_run({metric.name: expected_score}, scorer, [llm_response])


@pytest.mark.parametrize(
    "answer, expected_score",
    [
        ("Ryan's dog is named Fido.", 0.0),
        ("Ryan's dog is named Fido. Ryan's dog is named Fido.", 1.0),
    ],
)
def test_duplication_metric(answer, expected_score):
    metric = DuplicationMetric()
    benchmark = Benchmark(
        questions=["What is the name of Ryan's dog?"],
        answers=["Fido"],
    )
    llm_response = LLMResponse(
        llm_answer=answer,
        llm_context_list=[
            "Fido is the name of Ryan's dog.",
            "Ryan has a dog named Fido.",
        ],
        benchmark_item=benchmark.items[0],
    )
    scorer = ValidateScorer([metric])
    check_run({metric.name: expected_score}, scorer, [llm_response])


@pytest.mark.parametrize(
    "answer, expected_score",
    [
        ("All members of _ group are great.", 0.0),
        ("All members of _ group are horrible.", 1.0),
    ],
)
def test_hate_content_metric(answer, expected_score):
    metric = HateSpeechContentMetric()
    benchmark = Benchmark(
        questions=["What is the name of Ryan's dog?"],
        answers=["Fido"],
    )
    llm_response = LLMResponse(
        llm_answer=answer,
        llm_context_list=[
            "Fido is the name of Ryan's dog.",
            "Ryan has a dog named Fido.",
        ],
        benchmark_item=benchmark.items[0],
    )
    scorer = ValidateScorer([metric])
    check_run({metric.name: expected_score}, scorer, [llm_response])


@pytest.mark.parametrize(
    "time, expected_score",
    [
        (4, 1.0),
        (5, 1.0),
        (6, 0.0),
        (7, 0.0),
    ],
)
def test_latency_metric(time, expected_score):
    metric = LatencyMetric(target_time=5)
    benchmark = Benchmark(
        questions=["What is the name of Ryan's dog?"],
        answers=["Fido"],
    )
    llm_response = LLMResponse(
        llm_answer="Fido",
        llm_context_list=[
            "Fido is the name of Ryan's dog.",
            "Ryan has a dog named Fido.",
        ],
        benchmark_item=benchmark.items[0],
        run_time=time,
    )
    scorer = ValidateScorer([metric])
    check_run({metric.name: expected_score}, scorer, [llm_response])


@pytest.mark.parametrize(
    "answer, match_count, expected_score",
    [
        ("Fido", 1, 1.0),
        ("Fido is the name of Ryan's dog.", 1, 1.0),
        ("Fiddo is Ryan's dog", 1, 1.0),
        ("Fido is Ryan's dog. Ryan loves Fido.", 2, 1.0),
        ("Fid is Ryan's dog", 1, 0.0),
        ("Rex is Ryan's dog", 1, 0.0),
        ("fido is Ryan's dog", 1, 0.0),
    ],
)
def test_regex_metric(answer, match_count, expected_score):
    metric = RegexMetric("Regex Metric", "Fid*o", match_count)
    benchmark = Benchmark(
        questions=["What is the name of Ryan's dog?"],
        answers=["Fido"],
    )
    llm_response = LLMResponse(
        llm_answer=answer,
        llm_context_list=[
            "Fido is the name of Ryan's dog.",
            "Ryan has a dog named Fido.",
        ],
        benchmark_item=benchmark.items[0],
    )
    scorer = ValidateScorer([metric])
    check_run({metric.name: expected_score}, scorer, [llm_response])


@pytest.mark.parametrize(
    "answer, expected_score",
    [
        (generate_string(5), 1.0),
        (generate_string(10), 1.0),
        (generate_string(6), 1.0),
        (generate_string(11), 0.0),
        (generate_string(4), 0.0),
    ],
)
def test_response_length_metric(answer, expected_score):
    metric = ResponseLengthMetric("Response Length", 5, 10)
    benchmark = Benchmark(
        questions=["What is the name of Ryan's dog?"],
        answers=["Fido"],
    )
    llm_response = LLMResponse(
        llm_answer=answer,
        llm_context_list=[
            "Fido is the name of Ryan's dog.",
            "Ryan has a dog named Fido.",
        ],
        benchmark_item=benchmark.items[0],
    )
    scorer = ValidateScorer([metric])
    check_run({metric.name: expected_score}, scorer, [llm_response])


@pytest.mark.parametrize(
    "context, expected_score",
    [
        (["Ryan has a dog named Fido.", "Ryan's dog is named Fido."], 1.0),
        (["Ryan has a dog named Rex.", "Ryan's dog is named Rex."], 1.0),
        (["Ryan has a cat named Whiskers.", "Ryan's dog is named Fido."], 0.5),
        (["Ryan has a cat named Whiskers.", "Ryan's dog is named Rex."], 0.5),
        (["Ryan has a cat named Whiskers.", "Ryan's bird is named Polly"], 0.0),
    ],
)
def test_retrieval_precision_metric(context, expected_score):
    metric = RetrievalPrecisionMetric()
    benchmark = Benchmark(
        questions=["What is the name of Ryan's dog?"],
        answers=["Fido"],
    )
    llm_response = LLMResponse(
        llm_answer="Fido",
        llm_context_list=context,
        benchmark_item=benchmark.items[0],
    )
    scorer = ValidateScorer([metric])
    check_run({metric.name: expected_score}, scorer, [llm_response])


def check_perfect_score(run: Run):
    for item in run.overall_scores:
        if item == AnswerSimilarityMetric.name:
            assert run.overall_scores[item] == 5.0
        else:
            assert run.overall_scores[item] == 1.0
    for item in run.run_data:
        for metric_name, score in item.scores.items():
            if metric_name == AnswerSimilarityMetric.name:
                assert score == 5.0
            else:
                assert score == 1.0


def test_score():
    def get_llm_response(question) -> CallbackLLMResponse:
        return {
            "llm_answer": "Fido",
            "llm_context_list": [
                "Fido is the name of Ryan's dog.",
                "Ryan has a dog named Fido.",
            ],
        }

    benchmark = Benchmark(
        questions=["What is the name of Ryan's dog?"] * 2,
        answers=["Fido"] * 2,
    )
    # Score the responses for each question and answer pair
    scorer = ValidateScorer()
    run = scorer.score(benchmark, get_llm_response)
    check_perfect_score(run)


def test_score_responses():
    benchmark = Benchmark(
        questions=["What is the name of Ryan's dog?"] * 2,
        answers=["Fido"] * 2,
    )
    llm_response = LLMResponse(
        llm_answer="Fido",
        llm_context_list=[
            "Fido is the name of Ryan's dog.",
            "Ryan has a dog named Fido.",
        ],
        benchmark_item=benchmark.items[0],
    )
    # Score the responses for each question and answer pair
    scorer = ValidateScorer()
    run = scorer.score_responses([llm_response] * 2)
    check_perfect_score(run)


async def test_async_score():
    async def get_llm_response(question) -> CallbackLLMResponse:
        return {
            "llm_answer": "Fido",
            "llm_context_list": [
                "Fido is the name of Ryan's dog.",
                "Ryan has a dog named Fido.",
            ],
        }

    benchmark = Benchmark(
        questions=["What is the name of Ryan's dog?"] * 2,
        answers=["Fido"] * 2,
    )
    # Score the responses for each question and answer pair
    scorer = ValidateScorer()
    run = await scorer.a_score(benchmark, get_llm_response)
    check_perfect_score(run)


async def test_async_score_responses():
    benchmark = Benchmark(
        questions=["What is the name of Ryan's dog?"] * 2,
        answers=["Fido"] * 2,
    )
    llm_response = LLMResponse(
        llm_answer="Fido",
        llm_context_list=[
            "Fido is the name of Ryan's dog.",
            "Ryan has a dog named Fido.",
        ],
        benchmark_item=benchmark.items[0],
    )
    # Score the responses for each question and answer pair
    scorer = ValidateScorer()
    run = await scorer.a_score_responses([llm_response] * 2)
    check_perfect_score(run)
