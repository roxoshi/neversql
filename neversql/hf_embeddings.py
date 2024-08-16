import chromadb
from chromadb.db.base import UniqueConstraintError
from chromadb import Documents, EmbeddingFunction, Embeddings
import torch.nn.functional as F
import torch
from transformers import AutoModel, AutoTokenizer
from uuid import uuid4

class HFEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model_name=None):
        if model_name is None:
            model_name = 'Alibaba-NLP/gte-large-en-v1.5'
        self.model_name = model_name
    
    def __call__(self, input: Documents) -> Embeddings:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model_path = self.model_name
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModel.from_pretrained(model_path, trust_remote_code=True).to(device)

        # Tokenize the input texts
        batch_dict = tokenizer(input, max_length=4096, padding=True, truncation=True, return_tensors='pt').to(device)

        outputs = model(**batch_dict)
        embeddings = outputs.last_hidden_state[:, 0]
        embeddings = F.normalize(embeddings, p=2, dim=1)
        return embeddings.tolist()
        

def sample_code():
    client = chromadb.PersistentClient(path='db-dev/')
    embed = HFEmbeddingFunction()

    try:
        collection = client.create_collection(
            name='tempcollection', 
            embedding_function=embed,
            metadata={"hnsw:space": "cosine"})
    except UniqueConstraintError:
        collection = client.get_collection(name = 'tempcollection', embedding_function=embed)
    stext = 'create table "election" ("election_id" int,"representative_id" int,"date" text,"votes" real,"vote_percent" real,"seats" real,"place" real,primary key ("election_id"),foreign key ("representative_id") references `representative`("representative_id"))'
    print(len(stext))
    texts = [stext for i in range(100)]
    ids = [str(uuid4()) for i in range(100)]
    collection.add(
        documents=texts,
        ids = ids
    )

    result = collection.query(
        query_texts="Find a question",
        n_results=1,
    )
    # client.reset()
    print("Result: \n", result)

# sample_code()
