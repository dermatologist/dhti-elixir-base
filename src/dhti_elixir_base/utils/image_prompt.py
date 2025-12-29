from langchain_core.prompts import HumanMessagePromptTemplate, ChatPromptTemplate

def image_prompt(encoded_image_url: str, input_prompt: str, system_prompt: str) -> ChatPromptTemplate:
    """Creates a ChatPromptTemplate that includes an image and text prompt.

    Args:
        encoded_image_url (str): _description_
        input_prompt (str): _description_
        system_prompt (str): _description_

    Returns:
        ChatPromptTemplate: _description_

    Usage:
            {
               "system_prompt": lambda x: x["system_prompt"],
               "input": lambda x: x["input"],
               "encoded_image_url": lambda x: x["encoded_image_url"],
           }
            | image_prompt.  # <-----------
            | llm
            | StringOutputParser()
    """

    human = HumanMessagePromptTemplate.from_template(
        template=[
            {"type": "text", "text": "{input_prompt}"},
            {
                    "type": "image_url",
                    "image_url": "{encoded_image_url}",
            },
        ]
    )

    image_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system", "{system_prompt}",
            ),
            human,
        ]
    )

    return image_prompt
