from sql import Word
import sql
import json
from os import listdir, mkdir
from os.path import join, exists

vowels = set('аеиіоуяюєї')

def get_syllables(word1, stress):
    strip1 = word1.strip(" 0123456789*")
    split = strip1.split(" ")
    word = split[-1].strip()
    if len(list(word)) == 0 and len(list(word1)) != 0:
        print("")
    if stress is None:
        stress = word.find('́')
        stress -= 1

    syllables = []
    name = []

    def exclude_stress(char):
        return char != '́'
    for i, ch in enumerate(filter(exclude_stress, list(word))):
        name.append(ch)
        if ch.lower() in vowels:
            syllables.append("/" if stress == i else '_')
    return ''.join(syllables), ''.join(name)

def get_tail(word, syllables):
    chars = list(word.lower())
    result = []
    reversed_syllables = list(reversed(list(syllables)))
    if reversed_syllables.__contains__('/'):
        i_stress = reversed_syllables.index('/')
    else:
        return word

    for char in reversed(chars):
        if len(result) < 2 or i_stress >= 0:
            result.append(char)
        else:
            break
        if char in vowels:
            i_stress -= 1
    return ''.join(reversed(result))


def read():
    folder = "words_json"
    session = sql.DBSession()
    for file_name in listdir(folder):
        print(file_name)
        with open(join(folder, file_name), encoding='utf8') as json_file:
            data = json.load(json_file)
            print(len(data))
            for entry in data:


                name = entry['name']
                stress = entry['stress']
                syntax = entry['syntax']
                part = syntax['part']

                if part == 'іменник':
                    gender = syntax['gender']
                    details = entry['details']
                    singular = details['singular']
                    plural = details['plural']
                    base = None
                    for i, form_name in enumerate(singular):
                        if form_name == ' ':
                            continue
                        word_model = Word()
                        syllables, form_name = get_syllables(form_name, stress=None)
                        word_model.name = form_name
                        word_model.syllables = syllables
                        word_model.tail = get_tail(form_name, syllables)
                        word_model.part = part
                        word_model.gender = gender
                        word_model.form = i
                        if base is None:
                            base = word_model

                        else:
                            word_model.base = base
                        # print(part)
                        session.add(word_model)


                    for i, form_name in enumerate(plural):
                        if form_name == ' ':
                            continue
                        word_model = Word()
                        syllables, form_name = get_syllables(form_name, stress=None)
                        word_model.name = form_name
                        word_model.syllables = syllables
                        word_model.tail = get_tail(form_name, syllables)
                        word_model.part = part
                        word_model.gender = "plural"
                        word_model.form = i

                        if base is None:
                            base = word_model
                        else:
                            word_model.base = base

                        session.add(word_model)


                elif part == 'прикметник':

                    details = entry['details']
                    base = None
                    for i_g, gender in enumerate(['masculine', 'feminine', 'neuter', 'plural']):
                        for i, form_name1 in enumerate(details[gender]):
                            if form_name1 == ' ':
                                continue
                            word_model = Word()
                            syllables, form_name = get_syllables(form_name1, stress=None)
                            word_model.name = form_name
                            word_model.syllables = syllables
                            word_model.tail = get_tail(form_name, syllables)
                            word_model.part = part
                            word_model.gender = gender
                            word_model.form = i
                            if base is None:
                                base = word_model
                            else:
                                word_model.base = base
                            # print(part)
                            session.add(word_model)

                elif part == 'дієслово':
                    pass

                session.commit()

            for word in session.query(Word).filter(Word.base_id == None).all():
                word.base_id = word.id
            session.commit()

read()
# print(get_syllables('аба́ка',None))