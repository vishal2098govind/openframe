from groq import Groq


def describe_frame(client: Groq, frame: str, index: int) -> str:
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe the scene"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{frame}",
                        },
                    }
                ],
            },
        ],
        model="llama-3.2-11b-vision-preview",
    )

    description = chat_completion.choices[0].message.content
    print("Frame #{i}".format(i=index+1))
    print(chat_completion.choices[0].message.content)
    return description
