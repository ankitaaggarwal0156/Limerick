#!/usr/bin/env python
import argparse
import atexit
import codecs
from collections import defaultdict as dd
import gzip
import os.path
import re
import shutil
from string import punctuation
import sys
import tempfile

import nltk
from nltk.tokenize import word_tokenize

import numpy as np


if sys.version_info[0] == 2:
  from itertools import izip
else:
  izip = zip

# Use word_tokenize to split raw text into words


scriptdir = os.path.dirname(os.path.abspath(__file__))

reader = codecs.getreader('utf8')
writer = codecs.getwriter('utf8')

def prepfile(fh, code):
  if type(fh) is str:
    fh = open(fh, code)
  ret = gzip.open(fh.name, code if code.endswith("t") else code+"t") if fh.name.endswith(".gz") else fh
  if sys.version_info[0] == 2:
    if code.startswith('r'):
      ret = reader(fh)
    elif code.startswith('w'):
      ret = writer(fh)
    else:
      sys.stderr.write("I didn't understand code "+code+"\n")
      sys.exit(1)
  return ret

def addonoffarg(parser, arg, dest=None, default=True, help="TODO"):
  ''' add the switches --arg and --no-arg that set parser.arg to true/false, respectively'''
  group = parser.add_mutually_exclusive_group()
  dest = arg if dest is None else dest
  group.add_argument('--%s' % arg, dest=dest, action='store_true', default=default, help=help)
  group.add_argument('--no-%s' % arg, dest=dest, action='store_false', default=default, help="See --%s" % arg)



class LimerickDetector:

    def __init__(self):
        """
        Initializes the object to have a pronunciation dictionary available
        """
        self._pronunciations = nltk.corpus.cmudict.dict()


    def num_syllables(self, word):
        """
        Returns the number of syllables in a word.  If there's more than one
        pronunciation, take the shorter one.  If there is no entry in the
        dictionary, return 1.
        """

        # TODO: provide an implementation!
        if (word.lower() in (self._pronunciations))==True:
            count = np.array([len(list(y for y in x if y[-1].isdigit())) for x in self._pronunciations[word.lower()]])
            if len(count)>1:
                return count.min()
            else:
                return count[0]
        else:
            return 1
        
        

    def rhymes(self, a, b):
        """
        Returns True if two words (represented as lower-case strings) rhyme,
        False otherwise.
        """
        if (a.lower() in (self._pronunciations))==True:
            a_arr = np.array(self._pronunciations[a.lower()])
        else:
            return False
        if (b.lower() in (self._pronunciations))==True:
            b_arr = np.array(self._pronunciations[b.lower()])
        else:
            return False
        a_trunc = list()
        for j in a_arr:
            for i in range (0 ,len(j)):
                if j[i][-1].isdigit():
                    a_new = list(j[i:len(j)])
                    break
            a_trunc.append(a_new)
        
        b_trunc =list()
        for j in b_arr:
            for i in range (0 ,len(j)):
                if j[i][-1].isdigit():
                    b_new = list(j[i:len(j)])
                    break
            b_trunc.append(b_new)
        
        #finding the shorter string
        shorter = "a"
        for i in a_trunc:
            for j in b_trunc:
                if len(i)==len(j):
                    shorter ="equal"
                elif len(i)>len(j):
                    shorter = "b"
                else:
                    shorter = "a"
        
        #string matching
        if shorter =="equal":
            for i in a_trunc:
                for j in b_trunc:
                    if i==j:
                        return True
        
        elif shorter =="a":
            for i in a_trunc:
                for j in b_trunc:
                    if i== j[len(j)-len(i):len(j)]:
                        return True
        else:
            for i in a_trunc:
                for j in b_trunc:
                    if j== i[len(i)-len(j):len(i)]:
                        return True
                
        # TODO: provide an implementation!

        return False

    def is_limerick(self, text):
        """
        Takes text where lines are separated by newline characters.  Returns
        True if the text is a limerick, False otherwise.

        A limerick is defined as a poem with the form AABBA, where the A lines
        rhyme with each other, the B lines rhyme with each other, and the A lines do not
        rhyme with the B lines.


        Additionally, the following syllable constraints should be observed:
          * No two A lines should differ in their number of syllables by more than two.
          * The B lines should differ in their number of syllables by no more than two.
          * Each of the B lines should have fewer syllables than each of the A lines.
          * No line should have fewer than 4 syllables

        (English professors may disagree with this definition, but that's what
        we're using here.)


        """
        # TODO: provide an implementation!
        
        #tokens = self.apostrophe_tokenize(text)
        items = text.split("\n")
        tokens=list()
        for i in items:
            i= i.strip()
            if i=="":
                continue
            word = re.sub('[^a-zA-Z\' ]', '', i)
            words = word_tokenize(word.lower())
            #words = word_tokenize(i)
            #words=[word.lower() for word in words if word.isalpha()]
            tokens.append(words)
        #print tokens
        
        if len(tokens)<5:
            return False
        
        num_syl=[]
        for item in tokens:
            num =0
            for word in item:
                num = num + self.num_syllables(word)
            num_syl.append(num)
        
        if abs(num_syl[1] - num_syl[0]) >2 or abs(num_syl[4] - num_syl[0]) >2 or abs(num_syl[4] - num_syl[1]) >2 or abs(num_syl[3] - num_syl[2]) >2:
            return False
        for y in num_syl:
            if y < 4:
                return False
        if (num_syl[0]<num_syl[2]) or (num_syl[1]<num_syl[2]) or  (num_syl[4]<num_syl[2]) or  (num_syl[0]<num_syl[3]) or (num_syl[1]<num_syl[3]) or  (num_syl[4]<num_syl[3]):
            return False
         
        #checking for rhyme for A sentences and B    
        rhymA1 = self.rhymes(tokens[0][-1], tokens[1][-1])
        rhymA2 = self.rhymes(tokens[0][-1], tokens[4][-1])
        rhymB = self.rhymes(tokens[2][-1], tokens[3][-1])
        
        if rhymA1 and rhymA2 and rhymB:
            return True
        else:
            return False

# extra credit methods    
    def apostrophe_tokenize(self, text):
        items = text.split("\n")
        tokens=list()
        for i in items:
            i= i.strip()
            if i=="":
                continue
            word = re.sub('[^a-zA-Z ]', '', i)
            words = word.lower().split()
            tokens.append(words)
        return tokens
        
        
    def guess_syllables(self, word):
        word = word.lower()
        if len(word)==1:
            return 0
        num_vowels=0
        for char in word:
            if char in "aeiou":
                num_vowels = num_vowels+1
        if num_vowels ==1:
            return num_vowels
        if word[-1]=="e":
            num_vowels = num_vowels -1
        for i in range (0,len(word)-1):
            if word[i] in "aeiou" and word[i+1] in "aeiou":
                num_vowels = num_vowels -1
        if num_vowels ==1:
            return num_vowels
        for i in range (0,len(word)-1):
            if word[i] in "y" and word[i+1] in "aeiou":
                num_vowels = num_vowels -1
        
        return num_vowels
        


# The code below should not need to be modified
def main():
  parser = argparse.ArgumentParser(description="limerick detector. Given a file containing a poem, indicate whether that poem is a limerick or not",
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  addonoffarg(parser, 'debug', help="debug mode", default=False)
  parser.add_argument("--infile", "-i", nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="input file")
  parser.add_argument("--outfile", "-o", nargs='?', type=argparse.FileType('w'), default=sys.stdout, help="output file")




  try:
    args = parser.parse_args()
  except IOError as msg:
    parser.error(str(msg))

  infile = prepfile(args.infile, 'r')
  outfile = prepfile(args.outfile, 'w')

  ld = LimerickDetector()
  lines = ''.join(infile.readlines())
  outfile.write("{}\n-----------\n{}\n".format(lines.strip(), ld.is_limerick(lines)))

if __name__ == '__main__':
  main()
