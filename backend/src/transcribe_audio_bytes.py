from deepgram import DeepgramClient, ClientOptionsFromEnv, PrerecordedOptions, FileSource


def transcribe_audio_bytes(audio_bytes: bytes):
    # Configure the request
    dg_client = DeepgramClient("", ClientOptionsFromEnv(
        api_key="948d6bd379f4f635ce34894f2fa7d48b14d560d0"))
    source: FileSource = {
        "buffer": audio_bytes,
    }

    response = dg_client.listen.rest.v("1").transcribe_file(
        source, PrerecordedOptions(punctuate=True, language="en-US",))

    json = response.to_json()
    response.results
    print(f"spoken text: {json}")
    return response
