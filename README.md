# LLM Responses Quality Checker

This project evaluates the quality of responses from large language models (LLMs) by comparing them to answers from Wolfram Alpha. It uses Docker, Redis, and local LLMs to create a scalable and efficient testing environment.

## Prerequisites

- **Docker Desktop**: Install from [Docker's website](https://www.docker.com/products/docker-desktop).
- **Redis**: Use Docker to run a Redis container. Start the container and access RedisInsight at `localhost:8001` to ensure it's running.
- **Wolfram Alpha API**: Sign up at [Wolfram Alpha API](https://products.wolframalpha.com/api/) and generate an App ID using the 'Short Answers API'.
- **Local LLMs**: Install and configure `gpt4all` to run different models locally.
- **Python**: Ensure Python is installed with packages necessary to interact with LLMs via API.

## Installation and Setup

1. **Verify Docker Installation**:
   - Run the `hello-world` Docker image to confirm Docker is correctly installed.
2. **Redis Setup**:
   - Start the Redis container using Docker and verify by accessing RedisInsight via your browser.
3. **Wolfram Alpha Setup**:
   - Test your Wolfram Alpha App ID by making an API request:  
     ```
     https://api.wolframalpha.com/v1/result?i=How+fast+can+a+cheetah+run%3F&appid=YOUR_APP_ID
     ```
4. **Local LLM Setup**:
   - Install `gpt4all`, run it, and test multiple models with simple queries to ensure functionality.

## Running the Application

- Download the list of 50 general knowledge questions.
- The Python application should:
  - Iterate over each question.
  - Query each LLM for a response.
  - Compare the LLM response to the Wolfram Alpha answer using a similarity metric.
  - Store results in a list with the following structure: `Question, Model, Answer, TimeInMillisecondsToGetAnswer, Correctness`.

## Metrics Evaluated

- **Response Time**: Time taken by the LLM to generate an answer.
- **Correctness**: Evaluated on a scale from 0 to 10, comparing the LLM's answer to the standard answer from Wolfram Alpha.

## Caching

- Implement caching with Redis to store responses from Wolfram Alpha for four hours to minimize API calls.

## Output

- Upon completion, the application will output:
  - Number of questions answered.
  - Average and lowest ratings for each LLM model used.

## Usage

- Start the application and monitor the output for insights into the LLM performance and accuracy.
- Experiment with different prompt configurations to optimize response quality.
