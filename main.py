
import csv
import time
import requests
import redis
from gpt4all import GPT4All


def get_answer(model, question):
    start_time = time.time()
    output = model.generate(question, max_tokens=1000)
    end_time = time.time()
    time_in_milliseconds = (end_time - start_time) * 1000
    return output, time_in_milliseconds


def get_wolfram_alpha_answer(question):
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    # Check if the answer is in the cache
    cached_answer = redis_client.get(question)
    if cached_answer is not None:
        print(f"Retrieved from Redis: {question}")  # Debugging line
        answer = cached_answer.decode()
    else:
        appid = "L3PH8R-Xxxxxx"  # Replace with your actual App ID
        encoded_question = requests.utils.quote(question)
        url = f"https://api.wolframalpha.com/v1/result?i={encoded_question}&appid={appid}"
        response = requests.get(url)
        if response.status_code == 200:
            # Cache the response with an expiration of 4 hours (14400 seconds)
            redis_client.setex(question, 14400, response.text)
            answer = response.text
        else:
            answer = None  # Handle cases where Wolfram Alpha doesn't return an answer
    return answer

def read_questions(file_path):
    questions = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader, None)  # Skip the header row
        for row in csv_reader:
            if row:  # Check if the row is not empty
                question = row[1]  # Get the question from the second column
                questions.append(question)
    return questions


def write_results(results):
    with open("LLM_Answers.csv", mode='w', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(["Question", "Model", "Answer", "TimeInMillisecondsToGetAnswer", "Correctness"])
        csv_writer.writerows(results)


def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


def assess_answer_similarity(model, question, wolfram_answer, llm_answer):
    similarity_prompt = f"Provide a numerical rating between 1 and 10 to indicate the semantic similarity between " \
                        f"the following answers, where 1 means completely different and 10 means exactly the same. " \
                        f"Focus on the meaning and information conveyed, rather than exact wording. " \
                        f" Please return a single value representing the similarity." \
                        f"Example:\n" \
                        f"Question: What is the capital of France?\n" \
                        f"Answer 1: Paris is the capital of France.\n" \
                        f"Answer 2: The capital of France is Paris.\n" \
                        f"Similarity: 10\n" \
                        f"Question: {question}\n" \
                        f"Answer 1: {wolfram_answer}\n" \
                        f"Answer 2: {llm_answer}\n" \
                        f"Similarity: "

    similarity_output, _ = get_answer(model, similarity_prompt)
    index = similarity_output.lower().find("\n")
    try:
        if index != -1:  # Check if "question" is found in the string
            return similarity_output[:index]
        return similarity_output
    except ValueError:
        # Handle cases where the model does not return a numerical value
        return None


def main():
    mini_orca_model = GPT4All("orca-mini-3b-gguf2-q4_0.gguf")
    instruct_model = GPT4All("mistral-7b-instruct-v0.1.Q4_0.gguf")
    questions = read_questions("General_Knowledge_Questions.csv")
    results = []
    nbr_answers_Wolfram = 0
    avg_answer_rating_mini_orca = 0.0
    avg_answer_rating_instruct = 0.0



    for question in questions:
        mini_orca_answer, mini_orca_time = get_answer(mini_orca_model, question)
        mini_orca_answer = remove_prefix(mini_orca_answer, "\n")
        instruct_answer, instruct_time = get_answer(instruct_model, question)
        instruct_answer = remove_prefix(instruct_answer, "\n\n")
        wolfram_answer = get_wolfram_alpha_answer(question)

        if wolfram_answer is None:
            continue  # Skip the question if Wolfram Alpha doesn't have an answer
        nbr_answers_Wolfram += 1
        # Use the Orca model to assess answer similarity/correctness
        orca_correctness = assess_answer_similarity(mini_orca_model, question, wolfram_answer, mini_orca_answer)
        if orca_correctness is not None:
            results.append([question, "mini_orca-model", mini_orca_answer, mini_orca_time, orca_correctness])
            # Use the Orca model to assess answer similarity/correctness
        instruct_correctness = assess_answer_similarity(mini_orca_model, question, wolfram_answer, instruct_answer)
        if instruct_correctness is not None:
            results.append([question, "instruct-model", instruct_answer, instruct_time, instruct_correctness])
    write_results(results)
    print(f"Number of questions answered: {nbr_answers_Wolfram}")
    

if __name__ == "__main__":
    main()
