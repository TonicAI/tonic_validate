<picture>
  <source media="(prefers-color-scheme: light)" srcset="./readme_images/TonicValidate-Horizontal-Dark-Icon.svg">
  <source media="(prefers-color-scheme: dark)" srcset="./readme_images/TonicValidate-Horizontal-White-Icon.svg">
  <img src="./README_images/TonicValidate-Horizontal-Dark-Icon.svg">
</picture>

Tonic Validate is a platform for RAG development and experiment tracking. Sign up for a [free Tonic Validate account](https://validate.tonic.ai/signup), to try it out. This repository, `tonic_validate` (formerly `tvalmetrics`) is the SDK component of Tonic Validate. It contains the code for calculating RAG metrics to be used with Tonic Validate.

Install Tonic Validate via
```
pip install tonic-validate
```

# Tonic Validate

Evaluating a RAG application is difficult. There are several moving pieces to evaluate and there are not hard metrics for evaluation like in traditional machine learning tasks. For these reasons, we created Tonic Validate to allow you to shed light on how your RAG application is performing. The metrics in Tonic Validate use LLM-assisted evaluation, which means they use an LLM (i.e. gpt-4) to score different aspects of the outputs of a RAG application. Admittedly, while using LLM-assisted evaluation to calculate metrics creates "soft" metrics, we've found that when you break down a RAG application into pieces and use an LLM to grade each piece individually, the LLM can grade the pieces as well as or better than the acting LLM in the RAG application answers the questions. [Research also agrees](https://arxiv.org/abs/2306.05685) that using an LLM as an evaluator of unstructured text is almost as good as using a human.

Whenever a question is asked to a RAG application, the following objects can be considered:
* The question
* The correct answer to the question
* The answer that the RAG application returned
* The context that the RAG application retrieved and used to answer the question

The metrics in Tonic Validate use these objects and LLM-assisted evaluation to answer questions about the RAG application.
* **Answer similarity score**: How well does the RAG answer match what the answer should be?
* **Retrieval precision**: Is the retrieved context relevant to the question?
* **Augmentation precision**: Is the relevant retrieved context in the answer?
* **Augmentation accuracy**: How much of the retrieved context is in the answer?
* **Answer consistency (binary)**: Does the answer contain any information that does not come from the retrieved context?
 
For the complete definitions of these metrics, see the [RAG metrics reference](https://docs.tonic.ai/validate/rag-metrics/tonic-validate-rag-metrics-reference) section of our documentation or the [RAG metrics reference table](#metrics-reference-table) below. To see how these metrics vary with chunk size and number of retrieved context chunks for a simple RAG application, check out this [RAG metrics analysis jupyter notebook](examples/rag_metrics_sweep_analysis.ipynb).

The different metrics in Tonic Validate require different inputs to calculate (see reference table below).

Ideally, you have a benchmark dataset of questions and reference answers where the reference answers serve as the ground truth correct answers to the questions. When you have a benchmark dataset of questions and reference answers, you can utilize all of the metrics after you:

* Run the questions in the benchmark dataset through your RAG application
* Get the RAG application answers
* Get the retrieved context

It is common when building and evaluating a RAG application to not have a benchmark dataset of questions and reference answers. In this case, you cannot calculate the answer similarity score, but you can calculate all other scores.

# Installation and setup

Install Tonic Validate with pip:
```
pip install tonic-validate
```

Tonic Validate uses LLM-assisted evaluation to calculate RAG metrics. The LLM evaluator currently supports the Open AI gpt-4 and gpt-3.5 family of [models](https://platform.openai.com/docs/models/overview).
To use the Open AI models, Tonic Validate assumes that:
* You have an Open AI API key.
* The API key is set as the value of an environment variable.
To get an Open AI API key, go to the [OpenAI API key page](https://platform.openai.com/account/api-keys).
In your Python script or Jupyter notebook, to set your Open AI API key as an environment variable,
```python
import os
os.environ["OPENAI_API_KEY"] = "put-your-openai-api-key-here"
```

# Quickstart

Here's a code snippet to get you started.

```python
from tonic_validate import ValidateApi, ValidateScorer, Benchmark, LLMResponse
from tonic_validate.metrics import AnswerConsistencyMetric, AugmentationAccuracyMetric
benchmark = Benchmark(
    questions=["What is the capital of France?"],
    answers=["Paris"]
)
responses = []
for item in benchmark:
    # llm_answer is the answer that LLM gives
    # llm_context_list is a list of the context that the LLM used to answer the question
    llm_response = LLMResponse(
        llm_answer="Paris",
        llm_context_list=["Paris is the capital of France."],
        benchmark_item=item
    )
    responses.append(llm_response)
scorer = ValidateScorer([
    AnswerConsistencyMetric(),
    AugmentationAccuracyMetric()
])
run = scorer.score_run(responses)
validate_api = ValidateApi("your-api-key")
validate_api.upload_run("your-project-id", run)
```

If you want to see a benchmark you created in the Tonic Validate UI with benchmark_id ``, you can use the following code snippet.
```python
benchmark = validate_api.get_benchmark("benchmark0id")
for item in benchmark:
    print(item.question, item.answer)
```

You can upload a benchmark via

```python
validate_api.new_benchmark(benchmark, "name-here")
```


For a quickstart example using [LlamaIndex](https://github.com/run-llama/llama_index) for RAG, chech out this [quickstart jupyter notebook](examples/quickstart_example_paul_graham_essays.ipynb).

# Metrics reference

To help understand what part of a RAG application each metric measures, the following table defines the components of a typical RAG application.

## RAG Components Table

| Component          | Definition                                                   | Examples                                                     |
| ------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **Document store** | Where the textual data is stored.                            | Google Docs, Notion, Word documents                          |
| **Chunker**        | How each document is broken into pieces (or chunks) that are then embedded. | [Llama Hub](https://llamahub.ai/)                            |
| **Embedder**       | How each document chunk is transformed into a vector that stores its semantic meaning. | [text-embedding-ada-002](https://platform.openai.com/docs/guides/embeddings/what-are-embeddings), [sentence transformer](https://github.com/UKPLab/sentence-transformers), |
| **Retriever**      | The algorithm that retrieves relevant chunks of text from the user query. The relevant chunks of text are used as context to answer the user query. | Take the top cosine similarity scores between the embedding of the user query and the embedded document chunks. |
| **Prompt builder** | How the user query, along with conversation history and retrieved document chunks, are put into the context window to prompt the LLM for an answer to the user query. | Here's a user query {user_query} and here's a list of context that might be helpful to answer the user's query: {context_1}, {context_2}. Answer the user's query using the given context. |
| **LLM**            | The large model that takes the prompt from the prompt builder and returns an answer for the user's query. | gpt3.5-turbo, gpt4, Llama 2, Claude                          |

## Metrics reference table

The possible inputs for a RAG metric are:
* **Question**: The question asked.
* **Reference answer**: A prewritten answer that serves as the ground truth for how the RAG application should answer the question.
* **LLM answer**: The answer the RAG application gives to the question.
* **Retrieved context**: The retrieved context that is used in the prompt of the RAG application.
* **Top k context**: The top k pieces of context of the retrieval system, where k is fixed and the retrieved context is always a subset of the top k context.

The following metrics reference table shows, for each Tonic Validate metric:
* The inputs of the metric
* How the metric is defined
* What the metric measures

| Metric Name              | Inputs                                                    | Formula | What does it measure? | Which components does it evaluate? |
| ----------------------- | --------------------------------------------------------- | ------------------------------------------------------------ | ------------------------------------ |----|
| **Answer similarity score** | Question + Reference answer + LLM answer | Score between 0 and 5 | How well the reference answer matches the LLM answer. | All components.                     |
| **Retrieval precision** | Question + Retrieved context                         | (Count of relevant retrieved context) / (Count of retrieved context) | Whether the context retrieved is relevant to answer the given question. | Chunker + Embedder + Retriever    |
| **Augmentation precision** | Question + Retrieved context + LLM answer             | (Count of relevant retrieved context in LLM answer) / (Count of relevant retrieved context) | Whether the relevant context is in the LLM answer. | Prompt builder + LLM                |
| **Augmentation accuracy** | Retrieved context + LLM answer                          | (Count of retrieved context in LLM answer) / (Count of retrieved context) | Whether all the context is in the LLM answer. | Prompt builder + LLM                |
| **Answer consistency** or **Answer consistency binary** | Retrieved context + LLM answer                          | (Count of the main points in the answer that can be attributed to context) / (Count of main points in answer) | Whether there is information in the LLM answer that does not come from the context. | Prompt builder + LLM                |



# FAQ

### What models can I use an an LLM evaluator?

We currently allow the family of chat completion models from Open AI.

This restriction makes it easy to follow the logic for the definition of the metrics in this package. It also ensures that this package does not depend on langchain, which also makes the logic of the package easier to follow.

We'd like to add more models as choices for the LLM evaluator without adding to the complexity of the package too much.
