import shutil
import faiss
import os
from tqdm import tqdm
from txtai.embeddings import Embeddings
from modules.llm import load_openai_configs, cf, llm_chain
from modules.dataloader import pdf_loader, tiktoken_len, split_chunk
import gradio as gr


global embeddings


def chat_chain(question):
    global embeddings
    if cf.getboolean('CHAT', 'llm_generate_keywords'):
        keywords = llm_chain(question, '', '', cf.get('PROMPTS', 'prompt_key#1'))
        keywords = keywords.replace("Keywords:", "").replace(".", "").replace("\n", " ")
        print('Keywords:', keywords)
    else:
        keywords = question

    if cf.getboolean('CHAT', 'search_all_chunks'):
        print('Analyzing search results...')
        answer_layer_1 = ''
        for pdf_chunk in tqdm(pdf_chunks):
            new_answer = str(llm_chain(pdf_chunk, question, '', cf.get('PROMPTS', 'prompt_layer_1#1')))
            if new_answer[-1].isalnum():
                if cf.getboolean('CHAT', 'fix_truncation'):
                    new_answer = pdf_chunk
                print(
                    "\n\033[0;31;40mWarning: Incomplete response due to max tokens truncation or cuda out of memory.\033[0m")

            answer_layer_1 = str(answer_layer_1) + "\n" + str(new_answer)

    else:
        uid = embeddings.search(keywords, cf.getint('CHAT', 'top_k'))
        # print(uid)
        answer_layer_1 = ''
        print('Analyzing search results...')
        for id in tqdm(uid):
            new_answer = str(llm_chain(pdf_chunks[id[0]], question, '', cf.get('PROMPTS', 'prompt_layer_1#1')))
            if new_answer[-1].isalnum():
                if cf.getboolean('CHAT', 'fix_truncation'):
                    new_answer = pdf_chunks[id[0]]
                print(
                    "\n\033[0;31;40mWarning: Incomplete response due to max tokens truncation or cuda out of memory.\033[0m")

            answer_layer_1 = str(answer_layer_1) + "\n" + str(new_answer)

    print('Generating answer...')
    epoch = 0
    while tiktoken_len(answer_layer_1) > cf.getint('PDF', 'chunk_size'):
        # print(tiktoken_len(answer_layer_1), answer_layer_1)
        answer_layer_1_chunk = split_chunk(answer_layer_1)
        answer_layer_1 = ''

        epoch = epoch + 1
        print('Epoch', str(epoch) + ':')
        for i in tqdm(range(len(answer_layer_1_chunk))):
            new_answer = str(llm_chain(answer_layer_1_chunk[i], question, '', cf.get('PROMPTS', 'prompt_layer_1#1')))
            if new_answer[-1].isalnum():
                if cf.getboolean('CHAT', 'fix_truncation'):
                    new_answer = answer_layer_1_chunk[i]
                print(
                    "\n\033[0;31;40mWarning: Incomplete response due to max tokens truncation or cuda out of memory.\033[0m")

            answer_layer_1 = str(answer_layer_1) + "\n" + str(new_answer)

    final_answer = str(llm_chain(answer_layer_1, question, '', cf.get('PROMPTS', 'prompt_final#1')))
    if final_answer[-1].isalnum():
        if cf.getboolean('CHAT', 'fix_truncation'):
            final_answer = answer_layer_1
        print("\n\033[0;31;40mWarning: Incomplete response due to max tokens truncation or cuda out of memory.\033[0m")

    if not cf.getboolean('CHAT', 'search_all_chunks'):
        final_answer = final_answer + "\n\n**References:**\n"
        for i in range(min(len(uid), cf.getint('CHAT', 'top_k'))):
            if i == 0 or pdf_index[uid[i][0]] != pdf_index[uid[i - 1][0]]:
                pdf_path = os.path.abspath(pdf_index[uid[i][0]].get('source')).replace("\\", "/").replace(' ', '%20')
                pdf_link = "http://127.0.0.1:" + str(cf.getint('CHAT', 'port')) + "/file=" + pdf_path + "#page=" + str(pdf_index[uid[i][0]].get('page'))
                final_answer = final_answer + "[" + os.path.basename(os.path.abspath(pdf_index[uid[i][0]].get('source'))) + "](" + pdf_link + ")\n[Page: " + str(
                    pdf_index[uid[i][0]].get('page')) + "]\n"

    return final_answer


def chat_interface(question, history=[]):
    # final_answer = llm_chain(question, '', '', '{INPUT1}{INPUT2}{INPUT3}')
    final_answer = chat_chain(question)
    history.append((question, final_answer))
    last_question = question

    return "", history, last_question


if __name__ == '__main__':

    def upload_file(files, override):
        file_paths = [file.name for file in files]
        temp_path = os.getcwd() + "\\temp\\pdf"
        new_file_paths = []
        if override:
            dir = 'temp/pdf/'
            for files in os.listdir(dir):
                path = os.path.join(dir, files)
                try:
                    shutil.rmtree(path)
                except OSError:
                    os.remove(path)

        for file_path in file_paths:
            shutil.move(file_path, temp_path)
            new_file_paths.append(temp_path + "\\" + os.path.basename(file_path))

        global pdf_chunks, pdf_index
        pdf_chunks, pdf_index = pdf_loader('temp/pdf/')
        embeddings = Embeddings(
            {"path": cf.get('PDF', 'embedding_model'), "gpu": cf.getboolean('PDF', 'embedding_gpu'), "tokenize": True,
             "backend": "faiss"})
        print('Embedding chunks...')
        embeddings.index([(uid, text, None) for uid, text in enumerate(pdf_chunks)])
        print('Done.')

        return new_file_paths


    load_openai_configs('config.ini')
    faiss.omp_set_num_threads(cf.getint('PDF', 'faiss_threads'))
    if os.listdir('temp/pdf/'):
        global pdf_chunks, pdf_index
        pdf_chunks, pdf_index = pdf_loader('temp/pdf/')
        embeddings = Embeddings(
            {"path": cf.get('PDF', 'embedding_model'), "gpu": cf.getboolean('PDF', 'embedding_gpu'), "tokenize": True,
             "backend": "faiss"})
        print('Embedding chunks...')
        embeddings.index([(uid, text, None) for uid, text in enumerate(pdf_chunks)])
        print('Done.')

    allowed_paths = []
    allowed_paths.append(os.getcwd() + "\\temp\\pdf")
    with gr.Blocks() as webui:
        chatbot = gr.Chatbot()
        msg = gr.Textbox()
        last_msg = gr.Textbox(visible=False)
        clear = gr.Button("Clear")
        regenerate = gr.Button("Regenerate")
        override = gr.Checkbox(label="Override Existing PDFs", info="Override existing PDFs? Cancel to add PDFs.", value=True)
        pdf_files = gr.File()
        upload_button = gr.UploadButton("Click to Upload PDF Files", file_count="multiple")
        upload_button.upload(upload_file, [upload_button, override], pdf_files)
        msg.submit(chat_interface, [msg, chatbot], [msg, chatbot, last_msg])
        regenerate.click(chat_interface, [last_msg, chatbot], [msg, chatbot, last_msg])
        clear.click(lambda: None, None, chatbot, queue=False)

    webui.launch(show_error=True, allowed_paths=allowed_paths, server_port=cf.getint('CHAT', 'port'))