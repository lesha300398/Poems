import sql
from sql import Word
import numpy as np
from dictionary import Dictionary


class NoWordsError(Exception):
    pass


class PoemLine:
    def __init__(self, rhyme_symbol, syllables):
        self.rhyme_symbol = rhyme_symbol
        self.syllables = syllables
        self.words = None

    def __str__(self):
        return ' '.join([w.name for w in self.words])


class MorphUnit:
    def __init__(self, part, info):
        if part is not None:
            self.part = part
        else:
            self.part = np.random.choice(["іменник", "прикметник", "дієслово", "дієприслівник", "прислівник"])
        if info is not None:
            self.info = info
        elif self.part == "іменник" or self.part == "прийменник":
            self.info = {"vidm": np.random.choice(range(1, 5)),
                         'gender': np.random.choice(range(4))}
        elif self.part == "дієслово":
            self.info = {"persons": np.random.choice(range(3)),
                         "gender": np.random.choice(range(4)),
                         "time": np.random.choice(range(3))}
        else:
            self.info = dict()

    def generate_another(self):
        if self.part == "іменник":
            return MorphUnit(part="прикметник", info=self.info)
        elif self.part == "прикметник":
            part = np.random.choice(["прикметник", "дієприслівник", "прислівник"])
            if part == "прикметник":
                info = self.info
            else:
                info = dict()
            return MorphUnit(part=part, info=info)

        elif self.part == "дієслово":
            part = np.random.choice(["іменник", "дієприслівник", "прислівник"])

            return MorphUnit(part=part, info=None)
        else:
            part = np.random.choice(["дієприслівник", "прислівник"])
            return MorphUnit(part=part, info=None)


def split_syllables_into_words(syllables):
    syllables = list(syllables)
    word_count = syllables.count("/")
    result = []
    current_word = []
    for syllable in syllables:
        if current_word.__contains__('/') and len(result) < word_count - 1 and (
                syllable == '/' or np.random.randint(2) == 0):
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
                for i_word, syllable_word in reversed(list(enumerate(syllable_words))):

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
                    if i_word == 0:
                        word_lines.append(list(reversed(word_line)))
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


def get_morph(n_words):
    if n_words < 2:
        raise ValueError
    gender =  np.random.choice(range(4))
    result = [MorphUnit(part="іменник",
                        info={"vidm": 0,
                              'gender': gender}),
              MorphUnit(part="дієслово",
                        info={'gender': gender,
                              "persons": np.random.choice(range(3)),
                              "time": np.random.choice(range(3))})]
    weights = dict(zip(["іменник", "прикметник", "дієслово", "дієприслівник", "прислівник"], [5,4,5,1,1]))
    while len(result) < n_words:
        index = np.random.choice(range(len(result)), p=[weights[x] for x in result])
        offset = np.random.choice([0, 1])
        result.insert(index + offset, result[index].generate_another())
    return result


def make_rhymed_lines_new(poem_lines, max_attempts, words_to_include):
    attempts = 0
    session = sql.DBSession()
    while attempts < max_attempts:
        try:
            tail = None
            word_lines = []
            for poem_line in poem_lines:

                syllable_words = split_syllables_into_words(poem_line.syllables)
                morph_words = get_morph(len(syllable_words))
                word_line = []
                for i_word, syllable_word in reversed(list(enumerate(syllable_words))):
                    morph_unit = morph_words[i_word]
                    query_result = _d.get_words(part=morph_unit.part, info=morph_unit.info, ending=tail, syllables=syllable_word )

                    if not query_result:
                        raise NoWordsError
                    word = query_result[np.random.randint(len(query_result))]

                    word_line.append(word)
                    if i_word == len(syllable_words) - 1:
                        tail = word.tail
                    if i_word == 0:
                        word_lines.append(list(reversed(word_line)))
            for i, poem_line in enumerate(poem_lines):
                poem_line.words = word_lines[i]
            return
        except NoWordsError:
            attempts += 1
    raise NoWordsError


def generate_poem_new(words_to_include, syllables_template, rhyme_template, max_attempts):
    words_to_include = dict([(word, False) for word in words_to_include])
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
        make_rhymed_lines_new(rhyme_dict[rhyme_symbol], max_attempts=max_attempts, words_to_include=words_to_include)

    return '\n'.join([str(line) for line in poem_lines])

_d = Dictionary()
# np.random.seed(0)
# session = sql.DBSession()
# query = session.query(Word)
# result = query.all()
# print(len(result))
# # for w in map(lambda x: x.name, result):
# #     print(w)
# print(generate_poem(words_to_include='',
#                     syllables_template= "/__/__/_\n"+
#                                         "/__/__/\n" +
#                                         "/__/__/_/__/__/\n" +
#                                         "/__/__/_\n" +
#                                         "/__/__/\n" +
#                                         "/__/__/_\n" +
#                                         "___/__/"
#
#                     ,
#                     rhyme_template='abbcdcd',
#                     max_attempts=50))
# print(generate_poem(words_to_include='',
#                     syllables_template="_/_/_/_/\n" +
#                                        "_/_/___/_\n" +
#                                        "_/_/___/_\n" +
#                                        "_/_/___/"
#
#                     ,
#                     rhyme_template='abba',
#                     max_attempts=50))

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
