

from langchain_core.prompts import PromptTemplate


def load_file(filename: str) -> str:
    with open(file=filename, mode="r", encoding="utf-8") as file:
        return file.read()


def load_prompt(filename: str, input_variables: list) -> PromptTemplate:
    return PromptTemplate(
        input_variables=input_variables,
        template=load_file(filename=filename)
    )
