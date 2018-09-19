import re
import os
import sys
import datetime
from tqdm import tqdm
from gzip import GzipFile
import xml.etree.ElementTree as ET

class OpenSubtitles:
    # Before going through the code, do have a look at .xml from the opensubtitles dataset.

    def __init__(self, dirName, skipLines):
        print("Loading OpenSubtitles conversations from %s" % dirName)
        self.skipLines  = skipLines
        self.conversations = []
        self.tag_re = re.compile(r'(<!--.*?-->|<[^>]*>)')
        self.conversations = self.load_conversations(dirName)


    def load_conversations(self, dirName):
        conversations = []
        dirList = self.files_in_dir(dirName)
        for filepath in tqdm(dirList, "OpenSubtitles data files"):
            if filepath.endswith('gz'):
                try:
                    doc = self.get_xml(filepath)
                    conversations.extend(self.generate_list(doc))
                except ValueError:
                    tqdm.write("Skipping file %s with errors." % filepath)
                except:
                    print("Unexpected error:", sys.exc_info()[0])
                    raise
        return conversations



    def get_conversations(self):
        return self.conversations


    def generate_list(self, tree):
        # This function will parse the xml file and generate conversations out of it.
        root = tree.getroot()

        timeFormat = '%H:%M:%S'
        maxDelta = datetime.timedelta(seconds=1)

        startTime = datetime.datetime.min
        strbuf = ''
        sentList = []

        for child in root:
            for elem in child:
                if elem.tag == 'time':
                    elemID = elem.attrib['id']
                    elemVal = elem.attrib['value'][:-4]
                    if elemID[-1] == 'S':
                        startTime = datetime.datetime.strptime(elemVal, timeFormat)
                    else:
                        sentList.append((strbuf.strip(), startTime, datetime.datetime.strptime(elemVal, timeFormat)))
                        strbuf = ''
                else:
                    try:
                        strbuf = strbuf + " " + elem.text
                    except:
                        pass

        conversations = []

        if self.skipLines:
            step = 2
        else:
            step = 1

        for idx in range(0, len(sentList) - 1, step):
            cur = sentList[idx]
            nxt = sentList[idx + 1]
            if nxt[1] - cur[2] <= maxDelta and cur and nxt:
                tmp = {}
                tmp["lines"] = []
                tmp["lines"].append(self.get_line(cur[0]))
                tmp["lines"].append(self.get_line(nxt[0]))

                conversations.append(tmp)

        return conversations


    def get_line(self, sentence):
        line = {}
        line["text"] = self.tag_re.sub('', sentence).replace('\\\'', '\'').strip().lower()
        return line


    def get_xml(self, filepath):
        fext = os.path.splitext(filepath)[1]
        if fext == '.gz':
            tmp = GzipFile(filename=filepath)
            return ET.parse(tmp)
        else:
            return ET.parse(filepath)


    def files_in_dir(self, dirname):
        result = []
        for dirpath, dirs, files in os.walk(dirname):
            for filename in files:
                fname = os.path.join(dirpath, filename)
                result.append(fname)
        return result