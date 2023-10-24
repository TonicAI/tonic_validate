
# Tonic Validate Metrics

This is **Tonic Validate Metrics**, the retrieval augmented generation (RAG) metrics part of Tonic Validate. Tonic Validate Metrics provides fundamental RAG metrics and an evaluation framework for experimenting with RAG systems.

* [Tonic Validate Documentation](https://docs.tonic.ai/validate/).
* Tonic Validate is a platform for RAG development and experiment tracking. To use Tonic Validate Metrics in Tonic Validate, sign up for a [free Tonic Validate account](https://validate.tonic.ai/signup).

Install Tonic Validate Metrics via
```
pip install tvalmetrics
```

## Metrics

Evaluating a RAG system is difficult. There are several moving pieces to evaluate and there are not hard metrics for evaluation like in traditional machine learning tasks. For these reasons, we created Tonic Validate Metrics to allow you to shed light on how your RAG system is performing. The metrics in Tonic Validate Metrics use LLM-assisted evaluation, which means they use an LLM (i.e. gpt-4) to score different aspects of the outputs of a RAG system. Admittedly, while using LLM-assisted evaluation to calculate metrics creates "soft" metrics, we've found that when you break down a RAG system into pieces and use an LLM to grade each piece individually, the LLM can grade the pieces as well as or better than the acting LLM in the RAG system answers the questions. [Research also agrees](https://arxiv.org/abs/2306.05685) that using an LLM as an evaluator of unstructured text is almost as good as using a human.

Whenever a question is asked to a RAG system, the following objects can be considered:
* The question
* The correct answer to the question
* The answer that the RAG system returned
* The context that the RAG system retrieved and used to answer the question

The metrics in Tonic Validate Metrics use these objects use LLM-assisted evaluation to answer questions about the RAG system.
* **Answer similarity score**: How well does the RAG answer match what the answer should be?
* **Retrieval precision**: Is the retrieved context relevant to the question?
* **Augmentation precision**: Is the relevant retrieved context in the answer?
* **Augmentation accuracy**: How much of the retrieved context is in the answer?
* **Answer consistency (binary)**: Does the answer contain any information that does not come from the retrieved context?
* **Retrieval k-recall**: For the top k context vectors, where the retrieved context is a subset of the top k context vectors, is the retrieved context all of the relevant context among the top k context vectors for answering the question?
 
For the complete definitions of these metrics, see the [RAG metrics reference](https://docs.tonic.ai/validate/rag-metrics/tonic-validate-rag-metrics-reference) section of our documentation or the [RAG metrics reference table](#metrics-reference-table) below. To see how these metrics vary with chunk size and number of retrieved context chunks for a simple RAG system, check out this [RAG metrics analysis jupyter notebook](examples/rag_metrics_sweep_analysis.ipynb).

The different metrics in Tonic Validate Metrics require different inputs to calculate (see reference table below).

Ideally, you have a benchmark dataset of questions and reference answers where the reference answers serve as the ground truth correct answers to the questions. When you have a benchmark dataset of questions and reference answers, you can utilize all of the metrics after you:

* Run the questions in the benchmark dataset through your RAG system
* Get the RAG system answers
* Get the retrieved context
* If you use retrieval k-recall, get the top k context

It is common when building and evaluating a RAG system to not have a benchmark dataset of questions and reference answers. In this case, you cannot calculate the answer similarity score, but you can calculate all other scores.

## Installation and setup

Install Tonic Validate Metrics with pip:
```
pip install tvalmetrics
```

Tonic Validate Metrics uses LLM-assisted evaluation to calculate RAG metrics. The LLM evaluator currently supports the Open AI gpt-4 and gpt-3.5 family of [models](https://platform.openai.com/docs/models/overview).
To use the Open AI models, Tonic Validate Metrics assumes that:
* You have an Open AI API key.
* The API key is set as the value of an environment variable.
To get an Open AI API key, go to the [OpenAI API key page](https://platform.openai.com/account/api-keys).
In your Python script or Jupyter notebook, to set your Open AI API key as an environment variable,
```python
import os
os.environ["OPENAI_API_KEY"] = "put-your-openai-api-key-here"
```

## Quickstart

For a quickstart example using a simple [LlamaIndex](https://github.com/run-llama/llama_index) RAG system chech out this [quickstart jupyter notebook](examples/quickstart_example_paul_graham_essays.ipynb).

You can use Tonic Validate Metrics score to calculate RAG metrics with just a few lines of code.

```python
from tvalmetrics import RagScoresCaclulator

question: str # the question asked
reference_answer: str # ground truth answer
llm_answer: str # answer generated by RAG system
retrieved_context_list: List[str] # retrieved context used to answer question

llm_evaluator = "gpt-4"
score_calculator = RagScoresCalculator(llm_evaluator)

# By default, RagScoresCalculator calculates
#    Answer simimlarity scores
#    Retrieval precision
#    Augmentation precision
#    Augmentation accuracy
#    Answer consistency
#    Overall score  
# scores is a Python dataclass, so to access individual scores, use
# scores.answer_similarity_score, scores.retrieval_precision, and so on.
scores = score_calculator.score(
    question, reference_answer, llm_answer, retrieved_context_list
)
```

You can also specify which metrics to calculate when instantiating `RagScoresCalculator`. For example, if you do not have a reference answer or top k context, you only specify the the following scores.

```python
from tvalmetrics import RagScoresCaclulator

question: str # the question asked
reference_answer: str # ground truth answer
llm_answer: str # answer generated by RAG system
retrieved_context_list: List[str] # retrieved context used to answer question

llm_evaluator = "gpt-4"
score_calculator = RagScoreCalculator(
    model=llm_evaluator,
    retrieval_precision=True,
    augmentation_precision=True,
    augmentation_accuracy=True,
    answer_consistency=True
)

# You only specify the inputs that are needed to calculate the specified scores.
scores = score_calculator.score(
    question=question,
    llm_answer=llm_answer,
    retrieved_context_list=retrieved_context_list
)
```

If you have a batch of questions and answers, you can score them all simultaneously and then store the scores in a pandas DataFrame.

```python
from tvalmetrics import RagScoresCaclulator

question_list: List[str] # list of questions
reference_answer_list: List[str] # list of reference answers
llm_answer_list: List[str] # list of answers from the RAG system
retrieved_context_list_list: List[List[str]] # list of lists of retrieved context

llm_evaluator = "gpt-4"
score_calculator = RagScoresCalculator(llm_evaluator)

batch_scores = score_calculator.score_batch(
    question_list, reference_answer_list, llm_answer_list, retrieved_context_list_list
)

# mean of each score over the batch of question
mean_scores = batch_scores.mean_scores

# dataframe that has the input data and the scores for each question
scores_df = batch_scores.to_dataframe()
```

The [examples folder](examples) contains more extensive examples of using Tonic Validate Metrics with a RAG system. The example system is built using [LlamaIndex](https://github.com/run-llama/llama_index) to answer questions about Paul Graham essays on founders.

## Metrics reference

To help understand what part of a RAG system each metric measures, the following table defines the components of a typical RAG system.

### RAG Components Table

| Component          | Definition                                                   | Examples                                                     |
| ------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **Document store** | Where the textual data is stored.                            | Google Docs, Notion, Word documents                          |
| **Chunker**        | How each document is broken into pieces (or chunks) that are then embedded. | [Llama Hub](https://llamahub.ai/)                            |
| **Embedder**       | How each document chunk is transformed into a vector that stores its semantic meaning. | [text-embedding-ada-002](https://platform.openai.com/docs/guides/embeddings/what-are-embeddings), [sentence transformer](https://github.com/UKPLab/sentence-transformers), |
| **Retriever**      | The algorithm that retrieves relevant chunks of text from the user query. The relevant chunks of text are used as context to answer the user query. | Take the top cosine similarity scores between the embedding of the user query and the embedded document chunks. |
| **Prompt builder** | How the user query, along with conversation history and retrieved document chunks, are put into the context window to prompt the LLM for an answer to the user query. | Here's a user query {user_query} and here's a list of context that might be helpful to answer the user's query: {context_1}, {context_2}. Answer the user's query using the given context. |
| **LLM**            | The large model that takes the prompt from the prompt builder and returns an answer for the user's query. | gpt3.5-turbo, gpt4, Llama 2, Claude                          |

### Metrics reference table

The possible inputs for a RAG metric are:
* **Question**: The question asked.
* **Reference answer**: A prewritten answer that serves as the ground truth for how the RAG system should answer the question.
* **LLM answer**: The answer the RAG system gives to the question.
* **Retrieved context**: The retrieved context that is used in the prompt of the RAG system.
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
| **Retrieval k-recall** | Question + Retrieved context + Top k context         | (Count of relevant retrieved context) / (Count of relevant context in top k context) | How well the retrieval system retrieves all of the relevant context. | Chunker + Embedder + Retriever    |



## FAQ

### What models can I use an an LLM evaluator?

We currently allow the family of gpt3.5 and gpt4 models from Open AI.

This restriction makes it easy to follow the logic for the definition of the metrics in this package. It also ensures that this package does not depend on langchain, which also makes the logic of the package easier to follow.

We'd like to add more models as choices for the LLM evaluator without adding to the complexity of the package too much.
