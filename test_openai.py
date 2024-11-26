import openai
import os
import random

# Set your OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_poem(username, message):
    """Generate a 4-line poem for the user based on their name and message."""
    prompt = f"Write a 4-line poem for a live chat user. The user's name is {username}, and their message is: '{message}'. Make the poem witty and non-communal. The name given is a bigot and abusive to others in the channel."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",  # Replace with "gpt-4" if desired
            messages=[
                {"role": "system", "content": "You are a helpful assistant that writes friendly poems."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.9,
        )
        poem = response["choices"][0]["message"]["content"].strip()
        print(f"Generated poem: {poem}")
        return poem
    except Exception as e:
        print(f"Error generating poem: {e}")
        return f"{username}, your message shines bright,\nA beacon of joy, pure delight.\nThanks for speaking in this space,\nYour words bring warmth to every place!"


def generate_hindi_poem(username, message):
    """Generate a 4-line Hindi poem for the user based on their name and message."""
    prompt = f"""Write a 4-line poem in Hindi for a live chat user.
    The user's name is {username}, and their message is: '{message}'. Make the poem witty, and non-communal and in simple Hindi."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",  # Replace with "gpt-4" if desired
            messages=[
                {"role": "system", "content": "You are a helpful assistant that writes friendly poems in Hindi."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.9,
        )
        poem = response["choices"][0]["message"]["content"].strip()
        print(f"Generated Hindi poem: {poem}")
        return poem
    except Exception as e:
        print(f"Error generating Hindi poem: {e}")
        return f"{username}, आपका संदेश बहुत खास,\nलाया हमारे दिलों में मिठास।\nइस चैट में आप अद्भुत हो,\nआपके बिना यह अधूरा हो।"

def generate_witty_onliner_hindi(username, message):
    """Generate a 1-line witty remark for a live chat user based on their name and message."""
    prompt = f"Write a single witty and grim remark for a live chat user in hindi. The user's name is {username}, and their message is: '{message}'. The response should be sharp, engaging, and creative."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",  # Replace with "gpt-4" if desired
            messages=[
                {"role": "system", "content": "You are an assistant that writes sharp and witty one-liners to counter trolls."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.9,
        )
        poem = response["choices"][0]["message"]["content"].strip()
        print(f"Generated Hindi poem: {poem}")
        return poem
    except Exception as e:
        print(f"Error generating Hindi poem: {e}")
        return f"{username}, आपका संदेश बहुत खास,\nलाया हमारे दिलों में मिठास।\nइस चैट में आप अद्भुत हो,\nआपके बिना यह अधूरा हो।"

def generate_witty_line(username, message):
    """Generate a 1-line witty remark for a live chat user based on their name and message."""
    prompt = f"Write a single witty and grim remark for a live chat user. The user's name is {username}, and their message is: '{message}'. The response should be sharp, engaging, and creative."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",  # Replace with "gpt-4" if desired
            messages=[
                {"role": "system", "content": "You are an assistant that writes sharp and witty one-liners to counter trolls."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.9,
        )
        witty_remark = response["choices"][0]["message"]["content"].strip()
        return witty_remark
    except Exception as e:
        print(f"Error generating witty remark: {e}")
        return f"{username}, your {message} was so bold it scared punctuation away!"

# Example Usage



def list_models():
    """List available OpenAI models."""
    models = openai.Model.list()
    for model in models["data"]:
        print(model["id"])
#list_models()
#generate_poem("prabhu", "Most muslims are cause of poverty in india")
#generate_hindi_poem("prabhu", "भारत में गरीबी का कारण अधिकतर मुसलमान हैं")
#witty_remark = generate_witty_line("prabhu", "Most muslims are cause of poverty in india")
witty_remark = generate_witty_onliner_hindi("prabhu", "Most muslims are cause of poverty in india")
print(witty_remark)