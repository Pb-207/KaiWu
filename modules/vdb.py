from txtai.embeddings import Embeddings
from modules.llm import cf


def similar_chunks(keywords, chunks, reindex):
    print('Analyzing similarity...')
    embeddings = Embeddings(
        {"path": cf.get('PDF', 'embedding_model'), "gpu": cf.getboolean('PDF', 'embedding_gpu'), "tokenize": True,
         "backend": "faiss"})
    embeddings.index([(uid, text, None) for uid, text in enumerate(chunks)], reindex=reindex)
    uid = embeddings.search(keywords, cf.getint('CHAT', 'top_k'))

    return uid


# def similar_chunks(keywords, chunks):
#     embeddings = Embeddings(
#         {"path": cf.get('PDF', 'embedding_model'), "gpu": cf.getboolean('PDF', 'embedding_gpu'), "tokenize": True,
#          "backend": "faiss"})
#     if embeddings.exists(path="/temp/vdb"):
#         embeddings.load(path="/temp/vdb")
#         uid = embeddings.search(keywords, cf.getint('CHAT', 'top_k'))
#     else:
#         embeddings.index([(uid, text, None) for uid, text in enumerate(chunks)])
#         uid = embeddings.search(keywords, cf.getint('CHAT', 'top_k'))
#         if cf.getboolean('PDF', 'save2disk'):
#             embeddings.save(path="/temp/vdb")
#
#     return uid
