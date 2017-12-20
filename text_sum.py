import pandas as pd
import numpy as np
import tensorflow as tf
import re
from nltk.corpus import stopwords
import time
from tensorflow.python.layers.core import Dense
from tensorflow.python.ops.rnn_cell_impl import _zero_state_tensors
from app import App

# In[5]:
def clean_text(text, remove_stopwords = True):
    '''Remove unwanted characters, stopwords, and format the text to create fewer nulls word embeddings'''
    
    # Convert words to lower case
    text = text.lower()
    
    # Replace contractions with their longer forms 
    if True:
        text = text.split()
        new_text = []
        for word in text:
            if word in contractions:
                new_text.append(contractions[word])
            else:
                new_text.append(word)
        text = " ".join(new_text)
    
    # Format words and remove unwanted characters
    text = re.sub(r'https?:\/\/.*[\r\n]*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\<a href', ' ', text)
    text = re.sub(r'&amp;', '', text) 
    text = re.sub(r'[_"\-;%()|+&=*%.,!?:#$@\[\]/]', ' ', text)
    text = re.sub(r'<br />', ' ', text)
    text = re.sub(r'\'', ' ', text)
    
    # Optionally, remove stop words
    if remove_stopwords:
        text = text.split()
        stops = set(stopwords.words("english"))
        text = [w for w in text if not w in stops]
        text = " ".join(text)

    return text

def count_words(count_dict, text):
    '''Count the number of occurrences of each word in a set of text'''
    for sentence in text:
        for word in sentence.split():
            if word not in count_dict:
                count_dict[word] = 1
            else:
                count_dict[word] += 1

# In[13]:

def convert_to_ints(text, word_count, unk_count, eos=False):
    '''Convert words in text to an integer.
       If word is not in vocab_to_int, use UNK's integer.
       Total the number of words and UNKs.
       Add EOS token to the end of texts'''
    ints = []
    for sentence in text:
        sentence_ints = []
        for word in sentence.split():
            word_count += 1
            if word in vocab_to_int:
                sentence_ints.append(vocab_to_int[word])
            else:
                sentence_ints.append(vocab_to_int["<UNK>"])
                unk_count += 1
        if eos:
            sentence_ints.append(vocab_to_int["<EOS>"])
        ints.append(sentence_ints)
    return ints, word_count, unk_count



# In[15]:

def pad_sentence_batch(sentence_batch):
    """Pad sentences with <PAD> so that each sentence of a batch has the same length"""
    max_sentence = max([len(sentence) for sentence in sentence_batch])
    return [sentence + [vocab_to_int['<PAD>']] * (max_sentence - len(sentence)) for sentence in sentence_batch]


# In[16]:

def get_batches(summaries, texts, batch_size):
    """Batch summaries, texts, and the lengths of their sentences together"""
    for batch_i in range(0, len(texts)//batch_size):
        start_i = batch_i * batch_size
        summaries_batch = summaries[start_i:start_i + batch_size]
        texts_batch = texts[start_i:start_i + batch_size]
        pad_summaries_batch = np.array(pad_sentence_batch(summaries_batch))
        pad_texts_batch = np.array(pad_sentence_batch(texts_batch))
        
        # Need the lengths for the _lengths parameters
        pad_summaries_lengths = []
        for summary in pad_summaries_batch:
            pad_summaries_lengths.append(len(summary))
        
        pad_texts_lengths = []
        for text in pad_texts_batch:
            pad_texts_lengths.append(len(text))
        
        yield pad_summaries_batch, pad_texts_batch, pad_summaries_lengths, pad_texts_lengths

class Textsum(App):
    def __init__(self):
        super().__init__()
    
    def OnInitProgrmne(self):
        # In[1]:
        print('TensorFlow Version: {}'.format(tf.__version__))


        # In[2]:

        reviews = pd.read_csv("Reviews.csv")


        # In[3]:

        reviews = reviews.dropna()
        reviews = reviews.drop(['Id','ProductId','UserId','ProfileName','HelpfulnessNumerator','HelpfulnessDenominator',
                                'Score','Time'], 1)
        reviews = reviews.reset_index(drop=True)


        # In[4]:

        contractions = { 
        "ain't": "am not",
        "aren't": "are not",
        "can't": "cannot",
        "can't've": "cannot have",
        "'cause": "because",
        "could've": "could have",
        "couldn't": "could not",
        "couldn't've": "could not have",
        "didn't": "did not",
        "doesn't": "does not",
        "don't": "do not",
        "hadn't": "had not",
        "hadn't've": "had not have",
        "hasn't": "has not",
        "haven't": "have not",
        "he'd": "he would",
        "he'd've": "he would have",
        "he'll": "he will",
        "he's": "he is",
        "how'd": "how did",
        "how'll": "how will",
        "how's": "how is",
        "i'd": "i would",
        "i'll": "i will",
        "i'm": "i am",
        "i've": "i have",
        "isn't": "is not",
        "it'd": "it would",
        "it'll": "it will",
        "it's": "it is",
        "let's": "let us",
        "ma'am": "madam",
        "mayn't": "may not",
        "might've": "might have",
        "mightn't": "might not",
        "must've": "must have",
        "mustn't": "must not",
        "needn't": "need not",
        "oughtn't": "ought not",
        "shan't": "shall not",
        "sha'n't": "shall not",
        "she'd": "she would",
        "she'll": "she will",
        "she's": "she is",
        "should've": "should have",
        "shouldn't": "should not",
        "that'd": "that would",
        "that's": "that is",
        "there'd": "there had",
        "there's": "there is",
        "they'd": "they would",
        "they'll": "they will",
        "they're": "they are",
        "they've": "they have",
        "wasn't": "was not",
        "we'd": "we would",
        "we'll": "we will",
        "we're": "we are",
        "we've": "we have",
        "weren't": "were not",
        "what'll": "what will",
        "what're": "what are",
        "what's": "what is",
        "what've": "what have",
        "where'd": "where did",
        "where's": "where is",
        "who'll": "who will",
        "who's": "who is",
        "won't": "will not",
        "wouldn't": "would not",
        "you'd": "you would",
        "you'll": "you will",
        "you're": "you are"
        }
        
        # In[6]:

        # Clean the summaries and texts
        clean_summaries = []
        for summary in reviews.Summary:
            clean_summaries.append(clean_text(summary, remove_stopwords=False))
        print("Summaries are complete.")

        clean_texts = []
        for text in reviews.Text:
            clean_texts.append(clean_text(text))
        print("Texts are complete.")
        # In[8]:

        word_counts = {}

        count_words(word_counts, clean_summaries)
        count_words(word_counts, clean_texts)
                    
        print("Size of Vocabulary:", len(word_counts))

        # In[9]:

        embeddings_index = {}
        with open('numberbatch-en-17.04b.txt', encoding='utf-8') as f:
            for line in f:
                values = line.split(' ')
                word = values[0]
                embedding = np.asarray(values[1:], dtype='float32')
                embeddings_index[word] = embedding

        print('Word embeddings:', len(embeddings_index))


        # In[10]:

        # Find the number of words that are missing from CN, and are used more than our threshold.
        missing_words = 0
        threshold = 20

        for word, count in word_counts.items():
            if count > threshold:
                if word not in embeddings_index:
                    missing_words += 1
                    
        missing_ratio = round(missing_words/len(word_counts),4)*100
                    
        print("Number of words missing from CN:", missing_words)
        print("Percent of words that are missing from vocabulary: {}%".format(missing_ratio))


        # In[11]:

        vocab_to_int = {} 

        value = 0
        for word, count in word_counts.items():
            if count >= threshold or word in embeddings_index:
                vocab_to_int[word] = value
                value += 1

        # Special tokens that will be added to our vocab
        codes = ["<UNK>","<PAD>","<EOS>","<GO>"]   

        # Add codes to vocab
        for code in codes:
            vocab_to_int[code] = len(vocab_to_int)

        # Dictionary to convert integers to words
        int_to_vocab = {}
        for word, value in vocab_to_int.items():
            int_to_vocab[value] = word

        usage_ratio = round(len(vocab_to_int) / len(word_counts),4)*100

        print("Total number of unique words:", len(word_counts))
        print("Number of words we will use:", len(vocab_to_int))
        print("Percent of words we will use: {}%".format(usage_ratio))


        # In[12]:

        embedding_dim = 300
        nb_words = len(vocab_to_int)

        # Create matrix with default values of zero
        word_embedding_matrix = np.zeros((nb_words, embedding_dim), dtype=np.float32)
        for word, i in vocab_to_int.items():
            if word in embeddings_index:
                word_embedding_matrix[i] = embeddings_index[word]
            else:
                # If word not in CN, create a random embedding for it
                new_embedding = np.array(np.random.uniform(-1.0, 1.0, embedding_dim))
                embeddings_index[word] = new_embedding
                word_embedding_matrix[i] = new_embedding

        # Check if value matches len(vocab_to_int)
        print(len(word_embedding_matrix))


        # In[14]:

        word_count = 0
        unk_count = 0

        int_summaries, word_count, unk_count = convert_to_ints(clean_summaries, word_count, unk_count)
        int_texts, word_count, unk_count = convert_to_ints(clean_texts, word_count, unk_count, eos=True)

        unk_percent = round(unk_count/word_count,4)*100

        print("Total number of words in headlines:", word_count)
        print("Total number of UNKs in headlines:", unk_count)
        print("Percent of words that are UNK: {}%".format(unk_percent))



        # In[17]:

        epochs =100
        batch_size = 64
        rnn_size = 256
        num_layers = 3
        learning_rate = 0.001
        keep_probability = 0.5


        # In[18]:

        def text_to_seq(text):
            '''Prepare the text for the model'''
            
            text = clean_text(text)
            return [vocab_to_int.get(word, vocab_to_int['<UNK>']) for word in text.split()]




    def OnTextSum(self,input_sentence):text = text_to_seq(input_sentence)

        checkpoint = "./Model/best_model.ckpt"

        loaded_graph = tf.Graph()
        with tf.Session(graph=loaded_graph) as sess:
            # Load saved model
            loader = tf.train.import_meta_graph(checkpoint + '.meta')
            loader.restore(sess, checkpoint)

            input_data = loaded_graph.get_tensor_by_name('input:0')
            logits = loaded_graph.get_tensor_by_name('predictions:0')
            text_length = loaded_graph.get_tensor_by_name('text_length:0')
            summary_length = loaded_graph.get_tensor_by_name('summary_length:0')
            keep_prob = loaded_graph.get_tensor_by_name('keep_prob:0')
            
            #Multiply by batch_size to match the model's input parameters
            answer_logits = sess.run(logits, {input_data: [text]*batch_size, 
                                              summary_length: [np.random.randint(6,10)], 
                                              text_length: [len(text)]*batch_size,
                                              keep_prob: 1.0})[0] 

        # Remove the padding from the tweet
        pad = vocab_to_int["<PAD>"] 

        print('Original Text:', input_sentence)
        #print('Original Sum: ', input_summary)

        print('\nText')
        print('  Word Ids:    {}'.format([i for i in text]))
        print('  Input Words: {}'.format(" ".join([int_to_vocab[i] for i in text])))

        print('\nSummary')
        print('  Word Ids:       {}'.format([i for i in answer_logits if i != pad]))
        print('  Response Words: {}'.format(" ".join([int_to_vocab[i] for i in answer_logits if i != pad])))
        return " ".join([int_to_vocab[i] for i in answer_logits if i != pad]))
