
from dictionary import Dictionary
class Generator:
    def __init__(self, dictionary = Dictionary()):
        self.d = dictionary;
        #self.word_array = Dictionary.load_pickle(word_array_filename);
    #row_length (syllables):int, num_rows:int rhymes = [<line_number>,<line_number>] (to find the better line numbers)
    rules ={
        "VP":["дієслово"]
        "NP":
        "іменник":
        "прикметник":
        "дієслово":
        "прислівник":
    }
    def generate_sentence(row_length,num_rows,restrictions=[] ) 