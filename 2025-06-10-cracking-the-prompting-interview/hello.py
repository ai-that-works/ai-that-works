from baml_client import b
from baml_client.types import Content

def main():
    contents = [
        Content(url="https://en.wikipedia.org/wiki/France", content="France is a country in Europe."),
    ]
    answer = b.AnswerQuestion(question="What is the capital of France?", contents=[])
    for url in answer.citations:
        print(contents[url].url)


if __name__ == "__main__":
    main()
