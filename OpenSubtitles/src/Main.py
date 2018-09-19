# This is based on https://github.com/Conchylicultor/DeepQA/

import os
import DataSet
import argparse

class DialogueCorpus:

    def __init__(self):
        self.args = None
        self.dataSet = None


    @staticmethod
    def parseArgs(args):

        parser = argparse.ArgumentParser()
        datasetArgs = parser.add_argument_group('Dataset options')

        # All the opensubtitles data files ought to be downloaded here
        datasetArgs.add_argument('--rootDir', type=str, default=None,
                                help='Directory that holds the opensubtitles data files')

        # Set this flag, if you don't want answer to be the next question
        datasetArgs.add_argument('--skipLines', action='store_true',
                                 help='Set this to make only even conversations as questions')

        return parser.parse_args(args)



    def main(self, args=None):
        # First things first, parse the command line arguments
        self.args = self.parseArgs(args)

        # If the root directory is not passed, use the current directory as the root
        if not self.args.rootDir:
            self.args.rootDir = os.getcwd()

        # Kick off the opensubtitles conversation dataset generation.
        self.dataSet = DataSet.DataSet(self.args)



if __name__ == "__main__":
    corpus = DialogueCorpus()
    corpus.main()