import openai
import os


#openai.api_base = "http://192.168.86.67:1234/v1"
openai.api_base = "http://localhost:1234/v1"
openai.api_key = os.getenv("OPENAI_KEY", "sk-test")

EMBEDDING_MODEL = "text-embedding-embeddinggemma-300m-qat"
COMPLETION_MODEL = "cydonia-v4.1-ms3.2-magnum-diamond-24b-i1"
HERE = os.path.dirname(os.path.abspath(__file__))

# Put your name
key_owner = "<Name>"

maze_assets_loc = os.path.join(HERE, "../../environment/frontend_server/static_dirs/assets")
env_matrix = f"{maze_assets_loc}/the_ville/matrix"
env_visuals = f"{maze_assets_loc}/the_ville/visuals"

fs_storage = os.path.join(HERE, "../../environment/frontend_server/storage")
fs_temp_storage = os.path.join(HERE, "../../environment/frontend_server/temp_storage")

collision_block_id = "32125"

# Verbose 
debug = True


def create_completion(prompt) -> openai.ChatCompletion:
    return openai.ChatCompletion.create(
        model=COMPLETION_MODEL, 
        messages=[{"role": "user", "content": prompt}]
    )
    
def create_embedding(text) -> openai.Embedding:
    return openai.Embedding.create(
        input=[text],
        model=EMBEDDING_MODEL
    )['data'][0]['embedding']
    
def gpt_request(prompt: str, gpt_parameter: dict[str, object]) -> str:
    response = openai.Completion.create(
        model=COMPLETION_MODEL,
        prompt=prompt,
        temperature=gpt_parameter["temperature"],
        max_tokens=gpt_parameter["max_tokens"],
        top_p=gpt_parameter["top_p"],
        frequency_penalty=gpt_parameter["frequency_penalty"],
        presence_penalty=gpt_parameter["presence_penalty"],
        stream=gpt_parameter["stream"],
        stop=gpt_parameter["stop"],)
    return response.choices[0].text