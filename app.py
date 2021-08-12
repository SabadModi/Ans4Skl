from flask import Flask, render_template, request, send_file
# from flask_ngrok import run_with_ngrok
import os
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder='templates')
# run_with_ngrok(app)

@app.route("/", methods=['GET', 'POST'])
def main():
    if request.method == 'GET':
        return(render_template('main.html'))

    if request.method == "POST":
        link = request.form['link']
        question_link = request.form['question_link']

        text = request.form.get('text')
        question_text = request.form.get('question_text')

        file_input = request.files['fileInput']

        question_file = request.form.get('question_file')
########## WEBSITE ##############
        if(link and question_link):
            # from summarizer import Summarizer
            from transformers import pipeline #Import Summarization Model Pipeline
            from bs4 import BeautifulSoup  # Perform Web Scraping
            import requests  # Make HTTP/HTTPS Calls to the website and return the html

            summarizer = pipeline('summarization') #Importing our Summarization from the Hugging Face Transformers Pipeline

            URL = link

            r = requests.get(URL)
            # Passes all the html code we got from requests into BeautifulSoup for html parsing(formatting)
            soup = BeautifulSoup(r.text, 'html.parser')
            # Finds all the Headers and Paragraphste
            results = soup.find_all(['h1', 'p'])

            # Loops through every line of code in our results array and gets the text from it
            text = [result.text for result in results]

            # Appends the text that is received to form a string with all the text in the article
            ARTICLE = ''.join(text)

            ARTICLE = ARTICLE.replace('.', '.<eos>')
            ARTICLE = ARTICLE.replace('!', '!<eos>')
            ARTICLE = ARTICLE.replace('?', '?<eos>')
            sentences = ARTICLE.split('<eos>') # Splits the ARTICLE into different sentences based on the <eos> tag

            max_chunk = 500 # Limit 500 words per chunk to not cross token limit
            
            current_chunk = 0 
            chunks = []

            for sentence in sentences:
              if len(chunks) == current_chunk+1: # Checks whether we have a current chunk
                if len(chunks[current_chunk]) + len(sentence.split(' ')) <= max_chunk: # Checks whether the size of the current chunk and current sentence is less than 500 words
                  chunks[current_chunk].extend(sentence.split(' ')) # Gets the current chunk and splits the current sentence and appends it
                else:
                  current_chunk += 1 # Creates a new chunk because our current chunk + current sentence > 500
              else:
                print(current_chunk)
                chunks.append(sentence.split(' ')) # Split sentence into individual words and append it to chunks list

            for chunk_id in range(len(chunks)):
              chunks[chunk_id] = ' '.join(chunks[chunk_id]) # Forms complete sentences and appends all sentences into 1 string per chunk
            
            res = summarizer(chunks, max_length=200, min_length=50, do_sample=False)


            full = ' '.join([summ['summary_text'] for summ in res]) # Joining all the summary text into one string

            with open('summarized.txt', 'w') as f:
              f.write(full)

            bullet_points = full.split('. ')
            print(bullet_points)

            ############# QnA PART ##############
            print("Started with QnA")
            from transformers import AutoTokenizer, AutoModelForQuestionAnswering
            from transformers import pipeline

            tokenizer = AutoTokenizer.from_pretrained(
                "bert-large-uncased-whole-word-masking-finetuned-squad")
            model = AutoModelForQuestionAnswering.from_pretrained(
                "bert-large-uncased-whole-word-masking-finetuned-squad")
            nlp = pipeline('question-answering',
                        model=model, tokenizer=tokenizer)

            return (render_template('main.html',
             summarizedText = '\n\n\u2022'.join(bullet_points),
             userAnswer = nlp({
                'question': question_link,
                'context': ARTICLE
                }).get('answer'),
              works=True
             ))

######### TEXT #######################
        if(text and question_text):
          # from summarizer import Summarizer
          from transformers import pipeline #Import Summarization Model Pipeline
          summarizer = pipeline('summarization') #Importing our Summarization from the Hugging Face Transformers Pipeline

          # Appends the text that is received to form a string with all the text in the article
          ARTICLE = text

          res = summarizer(ARTICLE, max_length=200, min_length=50, do_sample=False)

          full = ' '.join([summ['summary_text'] for summ in res]) # Joining all the summary text into one string

          with open('summarized.txt', 'w') as f:
              f.write(full)

          bullet_points = full.split('. ')
          print(bullet_points)

          ############# QnA PART ##############
          print("Started with QnA")
          from transformers import AutoTokenizer, AutoModelForQuestionAnswering
          from transformers import pipeline

          tokenizer = AutoTokenizer.from_pretrained(
              "bert-large-uncased-whole-word-masking-finetuned-squad")
          model = AutoModelForQuestionAnswering.from_pretrained(
              "bert-large-uncased-whole-word-masking-finetuned-squad")
          nlp = pipeline('question-answering',
              model=model, tokenizer=tokenizer)

          return (render_template('main.html',
            summarizedText = '\n\n\u2022'.join(bullet_points),
            userAnswer = nlp({
              'question': question_text,
              'context': ARTICLE
            }).get('answer'),
            works=True
          ))

############# FILES ############
        if(file_name and question_file):
          
          file_name = secure_filename(file_input.filename)
          file_input.save(os.path.join("/content/"+file_name))
          
          # from summarizer import Summarizer
          from transformers import pipeline #Import Summarization Model Pipeline
          summarizer = pipeline('summarization') #Importing our Summarization from the Hugging Face Transformers Pipeline
          
          import textract
          file_content = textract.process(file_name)

          # Appends the text that is received to form a string with all the text in the article
          ARTICLE = str(file_content)

          ARTICLE = ARTICLE.replace('.', '.<eos>')
          ARTICLE = ARTICLE.replace('!', '!<eos>')
          ARTICLE = ARTICLE.replace('?', '?<eos>')
          sentences = ARTICLE.split('<eos>') # Splits the ARTICLE into different sentences based on the <eos> tag

          max_chunk = 400 # Limit 500 words per chunk to not cross token limit
            
          current_chunk = 0 
          chunks = []

          for sentence in sentences:
            if len(chunks) == current_chunk+1: # Checks whether we have a current chunk
              if len(chunks[current_chunk]) + len(sentence.split(' ')) <= max_chunk: # Checks whether the size of the current chunk and current sentence is less than 500 words
                chunks[current_chunk].extend(sentence.split(' ')) # Gets the current chunk and splits the current sentence and appends it
              else:
                current_chunk += 1 # Creates a new chunk because our current chunk + current sentence > 500
            else:
              print(current_chunk)
              chunks.append(sentence.split(' ')) # Split sentence into individual words and append it to chunks list

          for chunk_id in range(len(chunks)):
            chunks[chunk_id] = ' '.join(chunks[chunk_id]) # Forms complete sentences and appends all sentences into 1 string per chunk

          res = summarizer(chunks, max_length=200, min_length=50, do_sample=False)

          full = ' '.join([summ['summary_text'] for summ in res]) # Joining all the summary text into one string

          with open('summarized.txt', 'w') as f:
              f.write(full)

          bullet_points = full.split('. ')
          print(bullet_points)

          ############# QnA PART ##############
          print("Started with QnA")
          from transformers import AutoTokenizer, AutoModelForQuestionAnswering
          from transformers import pipeline

          tokenizer = AutoTokenizer.from_pretrained(
              "bert-large-uncased-whole-word-masking-finetuned-squad")
          model = AutoModelForQuestionAnswering.from_pretrained(
              "bert-large-uncased-whole-word-masking-finetuned-squad")
          nlp = pipeline('question-answering',
              model=model, tokenizer=tokenizer)

          return (render_template('main.html',
            summarizedText = '\n\n\u2022'.join(bullet_points),
            userAnswer = nlp({
              'question': question_file,
              'context': ARTICLE
            }).get('answer'),
            works=True
          ))

@app.route("/tts/", methods=['GET', 'POST'])
def tts():
    from gtts import gTTS
    import os
        
    with open('summarized.txt') as f:
      mytext = f.read()

    myobj = gTTS(text=mytext, lang='en', slow=False)

    myobj.save("tts.mp3")
        
    return send_file('tts.mp3')

if __name__ == "__main__":
    app.run()
