import openai
import pycountry as pycountry
from django.conf import settings

from reviews.services.exceptions import RateLimitError

openai.api_key = settings.OPENAI_API_KEY


def openai_api_calculate_cost(usage, model="gpt-3.5-turbo-instruct"):
    pricing = {
        'gpt-3.5-turbo-instruct': {
            'prompt': 0.0015,
            'completion': 0.002,
        },
        'gpt-3.5-turbo-1106': {
            'prompt': 0.001,
            'completion': 0.002,
        },
        'gpt-4-1106-preview': {
            'prompt': 0.010,
            'completion': 0.030,
        },
        'gpt-4': {
            'prompt': 0.03,
            'completion': 0.06,
        }
    }

    try:
        model_pricing = pricing[model]
    except KeyError:
        raise ValueError("Invalid model specified")

    prompt_cost = usage.prompt_tokens * model_pricing['prompt'] / 1000
    completion_cost = usage.completion_tokens * model_pricing['completion'] / 1000

    total_cost = prompt_cost + completion_cost
    # round to 6 decimals
    total_cost = round(total_cost, 6)

    # print(f"\nTokens used:  {usage.prompt_tokens:,} prompt + {usage.completion_tokens:,} completion = {usage.total_tokens:,} tokens")
    # print(f"Total cost for {model}: ${total_cost:.4f}\n")

    return total_cost


class ReplyGenerator:
    def __init__(self):
        pass

    def translate(self, text, lang):
        prompt = f"Rewrite in {lang} language:\n\n{text}"
        try:
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=prompt,
                temperature=0.7,
                max_tokens=350,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
        except openai.error.APIError as e:
            print(e)
            return

        text = response.choices[0].text.strip()
        if "\n" in text or ':' in text:
            # print(prompt)
            # print(text)
            text = response.choices[0].text.strip().split("\n")[-1]

        return text

    def generate_reply(self, text, lang, starRating, authorName, keyword, signature):
        text = text.strip()
        if text[-1] != '.':
            text += '.'
        #
        # # Detect language
        # if re.search(r'(best|cool|beautiful|good|wow|)', text, re.IGNORECASE):
        #     lang = 'en'

        # try:
        #     lang_detected = langdetect.detect(text)
        # except LangDetectException:
        #     lang_detected = None

        try:
            language = pycountry.languages.lookup(lang)
        except LookupError:
            if '-' in lang:
                language = pycountry.languages.lookup(lang.split('-')[0])
            else:
                language = pycountry.languages.lookup('en')

        if starRating >= 4:
            prompt_ask = f"Ask how he likes {keyword} "
        elif starRating <= 2:
            prompt_ask = 'Ask to remove negative review'
        else:
            prompt_ask = ''


        prompt_author = f"from a user named {authorName}" if authorName else ""

        prompt_signature = f"Sign off as {signature}." if signature else ""

        prompt = f"Compose a thoughtful and positive response in {language.name} language to a {starRating}-star Google Play review {prompt_author}. " \
                 f"Acknowledge their appreciation and express gratitude. " \
                 f"{prompt_ask}. " \
                 f"Do not ask to contact us anyway. " \
                 f"Keep the reply professional and friendly, limited to 250 characters. {prompt_signature}:\n{text}"

        # print(prompt)
        # print()
        try:
            response = openai.Completion.create(
                model="gpt-3.5-turbo-instruct",
                prompt=prompt,
                temperature=0.7,
                max_tokens=350,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
        except openai.error.RateLimitError as e:
            print(e)
            raise RateLimitError()
        except openai.error.APIError as e:
            print(e)
            return

        text = response.choices[0].text.strip(" \n\t\r\".")

        if "\n" in text or ':' in text:
            # print(prompt)
            # print(text)
            text = text.split("\n")[-1]
        #
        # if lang != 'en':
        #     text = self.translate(text, lang)

        print(text)

        cost = openai_api_calculate_cost(response.usage, model="gpt-3.5-turbo-instruct")
        return text, cost
