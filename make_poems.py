import sql
from sql import Word
import numpy as np


class NoWordsError(Exception):
    pass

class PoemLine:
    def __init__(self, rhyme_symbol, syllables):
        self.rhyme_symbol = rhyme_symbol
        self.syllables = syllables
        self.words = None

    def __str__(self):
        return ' '.join([w.name for w in self.words])


def split_syllables_into_words(syllables):
    syllables = list(syllables)
    word_count = syllables.count("/")
    result = []
    current_word = []
    for syllable in syllables:
        if current_word.__contains__('/') and len(result) < word_count - 1 and (syllable == '/' or np.random.randint(2) == 0):
            result.append(''.join(current_word))
            current_word = [syllable]
        else:
            current_word.append(syllable)
    result.append(''.join(current_word))
    return result

def make_rhymed_lines(poem_lines, max_attempts):
    attempts = 0
    session = sql.DBSession()
    while attempts < max_attempts:
        try:
            tail = None
            word_lines = []
            for poem_line in poem_lines:

                syllable_words = split_syllables_into_words(poem_line.syllables)
                word_line = []
                for i_word, syllable_word in enumerate(syllable_words):

                    query = session.query(Word).filter(Word.syllables == syllable_word)
                    if i_word == len(syllable_words) - 1 and tail is not None:
                        query = query.filter(Word.tail == tail)
                    query_result = query.all()
                    if not query_result:
                        raise NoWordsError
                    word = query_result[np.random.randint(len(query_result))]

                    word_line.append(word)
                    if i_word == len(syllable_words) - 1:
                        tail = word.tail
                        word_lines.append(word_line)
            for i, poem_line in enumerate(poem_lines):
                poem_line.words = word_lines[i]
            return
        except NoWordsError:
            attempts += 1
    raise NoWordsError

def generate_poem(words_to_include, syllables_template, rhyme_template, max_attempts):

    rhyme_template = list(rhyme_template)
    syllable_lines = syllables_template.split('\n')

    poem_lines = []
    rhyme_dict = dict()
    for rhyme_symbol, syllable_line in zip(rhyme_template, syllable_lines):
        poem_line = PoemLine(rhyme_symbol=rhyme_symbol, syllables=syllable_line)
        poem_lines.append(poem_line)
        if rhyme_symbol in rhyme_dict:
            rhyme_dict[rhyme_symbol].append(poem_line)
        else:
            rhyme_dict[rhyme_symbol] = [poem_line]

    for rhyme_symbol in rhyme_dict:
        make_rhymed_lines(rhyme_dict[rhyme_symbol], max_attempts=max_attempts)

    return '\n'.join([str(line) for line in poem_lines])


# np.random.seed(0)
# session = sql.DBSession()
# query = session.query(Word)
# result = query.all()
# print(len(result))
# # for w in map(lambda x: x.name, result):
# #     print(w)
print(generate_poem(words_to_include='',
                    syllables_template= "/__/__/_\n"+
                                        "/__/__/\n" +
                                        "/__/__/_/__/__/\n" +
                                        "/__/__/_\n" +
                                        "/__/__/\n" +
                                        "/__/__/_\n" +
                                        "___/__/"

                    ,
                    rhyme_template='abbcdcd',
                    max_attempts=50))


# "/__/__/_\n"+
# "/__/__/\n" +
# "/__/__/_/__/__/\n" +
# "/__/__/_\n" +
# "/__/__/\n" +
# "/__/__/_\n" +
# "___/__/"
#
# 'abbcdcd'
# В райдугу чайка летіла.
# Хмара спливала на схід.
# Може б, і ти захотіла: Чайці податися вслід?
# Сонце на заході впало.
# Райдуга згасла в імлі.
# Темно і холодно стало
# На неспокійній землі (Л. Первомайський).




# "_/_/_/_/\n"+
# "_/_/___/_\n" +
# "_/_/___/_\n"+
# "_/_/___/"
#
# 'abba'
#
# Яких іще зазнаю кар?
# Якими нетрями ітиму
# Шляхами з Риму і до Криму
# Під ґвалт і кпини яничар? (І. Світличний).