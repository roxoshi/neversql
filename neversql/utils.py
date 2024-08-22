import logging
import json
from uuid import uuid4

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

llmlogger = logging.getLogger("llmlogger")
llmlogger.addHandler(logging.FileHandler('logs/llm.log'))
    
def llmlog(func):
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        prompt = args[0] if isinstance(args[0], str) else args[1]
        llmlogger.info(f"{json.dumps({'id': str(uuid4()), 'prompt': prompt, 'response': response})}")
        return response
    return wrapper

if __name__ == '__main__':
    @llmlog
    def llm(prompt):
        return f"Your prompt = `{prompt}` with no additional help from the AI"
    llm("This my prompt")