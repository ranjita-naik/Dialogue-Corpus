import os
import nltk
import string
import pickle
import random
import Utils
import OpenSubtitles
from tqdm import tqdm



class DataSet:

    def __init__(self, args):

        self.args = args

        self.DATASET_NAME = 'OpenSubtitles'
        self.NO_SAMPLE_DIALOGUES_TO_DISPLAY = 10

        # Path variables
        self.corpusDir = os.path.join(self.args.rootDir, 'data', self.DATASET_NAME )
        self.skipLines = self.args.skipLines
        basePath = self._construct_base_path()
        self.fullPath = basePath + '.pkl'

        self.trainingSamples = []
        self.load_corpus()

        # Displays dialogue summary
        self._print_stats()

        # Let's display some sample dialogues
        self.display_sample_dialogues()


    def _print_stats(self):
        print('Loaded {}:  {} QA'.format(self.DATASET_NAME, len(self.trainingSamples)))


    def _construct_base_path(self):
        path = os.path.join(self.args.rootDir, 'data' + os.sep )
        path += 'dataset-{}'.format(self.DATASET_NAME)
        return path



    def get_sample_size(self):
        return len(self.trainingSamples)


    def load_corpus(self):
        datasetExist = os.path.isfile(self.fullPath)
        if not datasetExist:
            print('Constructing full dataset...')

            corpusData = OpenSubtitles.OpenSubtitles(self.corpusDir, self.skipLines)

            self.create_full_corpus(corpusData.get_conversations())
            self.save_dataset(self.fullPath)
        else:
            self.load_dataset(self.fullPath)

        self._print_stats()



    def save_dataset(self, filename):
        # save_dataset and load_dataset need to be in sn
        with open(os.path.join(filename), 'wb') as handle:
            data = {
                'trainingSamples': self.trainingSamples
            }
            pickle.dump(data, handle, -1)



    def load_dataset(self, filename):
        dataset_path = os.path.join(filename)
        print('Loading dataset from {}'.format(dataset_path))
        with open(dataset_path, 'rb') as handle:
            data = pickle.load(handle)
            self.trainingSamples = data['trainingSamples']


    def create_full_corpus(self, conversations):
        for conversation in tqdm(conversations, desc='Extract conversations'):
            self.extract_conversation(conversation)


    def extract_conversation(self, conversation):
        for i in range(0, len(conversation['lines']) - 1, 1):

            inputLine = conversation['lines'][i]
            targetLine = conversation['lines'][i + 1]

            inputWords = self.extract_text(inputLine['text'])
            targetWords = self.extract_text(targetLine['text'])

            if inputWords and targetWords:  # Filter wrong samples (if one of the list is empty)
                self.trainingSamples.append([inputWords, targetWords])



    def extract_text(self, line):
        sentences = []

        # Extract sentences
        sentencesToken = nltk.sent_tokenize(line)

        # We add sentence by sentence until we reach the maximum length
        for i in range(len(sentencesToken)):
            tokens = nltk.word_tokenize(sentencesToken[i])

            tempWords = []
            for token in tokens:
                tempWords.append(token)  # Create the vocabulary and the training sentences

            sentences.append(tempWords)

        return sentences


    def sequence2str(self, sequence, clean=False):
        if not sequence:
            return ''

        if not clean:
            return ' '.join([idx for idx in sequence])

        sentence = []
        for word in sequence:
            sentence.append(word)


        return self.detokenize(sentence)


    def detokenize(self, tokens):
        return ''.join([
            ' ' + t if not t.startswith('\'') and
                       t not in string.punctuation
            else t
            for t in tokens[0]]).strip().capitalize()


    def display_sample_dialogues(self):
        print('Disaplying random conversations...')

        for i in range(self.NO_SAMPLE_DIALOGUES_TO_DISPLAY):
            idSample = random.randint(0, len(self.trainingSamples) - 1)
            print('Q: {}'.format(self.sequence2str(self.trainingSamples[idSample][0], clean=True)))
            print('A: {}'.format(self.sequence2str(self.trainingSamples[idSample][1], clean=True)))
            print()
        pass




