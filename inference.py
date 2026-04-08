from openai import OpenAI

client = OpenAI()

def run_inference(input_text: str):
    print("START")

    # Dummy call (not actually used)
    print("STEP: received input")

    # Your real system can be plugged here later
    print("STEP: processing")

    output = f"Processed: {input_text}"

    print("END")

    return output
