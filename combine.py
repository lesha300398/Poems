import os
import json
import copy;
import re;
import pickle;
import os;
directory = r'./current'


def parse_json(directory):
    result =[];
    for entry in os.scandir(directory):
        if entry.is_file():
            with open(entry.path) as f:
                data = json.load(f);
                for x in data:
                    if not x['name'][0].isupper():
                        result.append(x)
                print(entry.path)
    print(str(len(result))+" words");
    return result;

def split_by_part(values, indices):
    split_data = {};
    for i in indices:
        if not (values[i]['syntax']['part'] in split_data):
            split_data[values[i]['syntax']['part']] = [];
        split_data[values[i]['syntax']['part']].append(i);
    return split_data;

def get_syllables_stress_rhyme(word):
    syllabels = 0;
    stress = 0;
    rhyme = 0;
    for i,char in enumerate(word):
        #print(i)
        if char in ['а','о','е','и','у','і','є','ю','я','ї']:
            syllabels +=1;
        elif char == '́':
            stress = syllabels;
            rhyme = word[i-1:i]+word[i+1:]
    if(rhyme == 0 and syllabels == 1):
        stress = 1;
        for i,char in enumerate(word):
            if char in ['а','о','е','и','у','і','є','ю','я','ї']:
                rhyme =word[i:];
    return [syllabels,stress,rhyme];

def parse_final_stage(values, indices): #values = string array. values[i] corresponds to some_global_words[indices[i]]
    index_tree = {};
    for i,s in enumerate(values):
        s = s.replace('*','');
        if(s[:10] =="партма"+'́'+"фіє"):
            print(s.replace('́',''));

        params = get_syllables_stress_rhyme(s);
        syllable_stress = (params[0],params[1])
        if not (syllable_stress in index_tree):
            index_tree[syllable_stress] = {};
        if not (params[2] in index_tree[syllable_stress]):
            index_tree[syllable_stress][params[2]]=[];
        index_tree[syllable_stress][params[2]].append((s.replace('́',''),indices[i]));
    return index_tree;


noun_gender_set ={ # temp fix, don't forget to split by comma first
    "іменник чоловічого або жіночого роду":["masculine","feminine"],
    "іменник жіночого або чоловічого роду":["masculine","feminine"],
    "іменник жіночого або середнього роду":["neuter","feminine"],
    "іменник середнього або жіночого роду":["neuter","feminine"],
    "іменник чоловічого або середнього роду":["masculine","neuter"],
    "іменник середнього або чоловічого роду":["masculine","neuter"],
    "іменник чоловічого роду":["masculine"],
    "іменник жіночого роду":  ["feminine"],
    "іменник середнього роду":["neuter"],
    "іменник з прийменником":[], # not a noun!!!
}
def parse_nouns(values, indices):
    vidminky = {"називний":0,"родовий":1, "давальний":2,"знахідний":3,"орудний":4,"місцевий":5,"кличний":6};
    genders = {"masculine":0,"feminine":1,"neuter":2, "plural":3};
    index_tree = [];
    for v in range(7):
        index_tree.append([]);
        for g in range(4):
            index_tree[v].append([])
    
    temp_index_tree = copy.deepcopy(index_tree);
    temp_word_tree = copy.deepcopy(index_tree);
    
    for i in indices:
        noun_genders = noun_gender_set[values[i]['syntax']['original'].split(',')[0]];
        gender_indices = [genders[i] for i in noun_genders];
        if(len(gender_indices)==0):
            continue; #іменник з прийменником
        if 'singular' in values[i]['details']:
            for gender_index in gender_indices:
                for j in range(7): # відмінки
                    for word in values[i]['details']['singular'][j].split(", "): #handle multiple comma-separated words
                        temp_word_tree[j][gender_index].append(word);
                        temp_index_tree[j][gender_index].append(i);
        if 'plural' in values[i]['details']:
            for j in range(7): # відмінки
                temp_word_tree[j][3].append(values[i]['details']['plural'][j]);
                temp_index_tree[j][3].append(i);
    
    for v in range(7):
        index_tree.append([]);
        for g in range(4):
            index_tree[v][g] = parse_final_stage(temp_word_tree[v][g],temp_index_tree[v][g]);
    return index_tree;

def parse_adjectives(values, indices): 
    vidminky = {"називний":0,"родовий":1, "давальний":2,"знахідний":3,"орудний":4,"місцевий":5};
    genders = {"masculine":0,"feminine":1,"neuter":2, "plural":3};
    index_tree = [];
    for v in range(6):
        index_tree.append([]);
        for g in range(4):
            index_tree[v].append([])
    
    temp_index_tree = copy.deepcopy(index_tree);
    temp_word_tree = copy.deepcopy(index_tree);
    
    for i in indices:
        for g in genders:
            if g in values[i]['details']:
                for j in range(6): # відмінки
                    for word in values[i]['details'][g][j].split(", "): #handle multiple comma-separated words
                        temp_word_tree[j][genders[g]].append(word);
                        temp_index_tree[j][genders[g]].append(i);
    for v in range(6):
        index_tree.append([]);
        for g in range(4):
            index_tree[v][g] = parse_final_stage(temp_word_tree[v][g],temp_index_tree[v][g]);
    return index_tree;

def parse_verbs(values, indices): #values = string array. values[i] corresponds to some_global_words[indices[i]]
    time_list = {"past":0,"present":1, "future":2,"command":3}

    past_fields = {'masculine':0,'feminine':1,'neuter':2,'plural':3}
    future_fields = {'first_person':0,'second_person':1,'third_person':2}
    present_fields = {'first_person':0,'second_person':1,'third_person':2} 
    quantity = {'singular':0,'plural':1}

    #additional formes are ignored, for nnow
    command_fields={'first_person':0,'second_person':1}
    genders = {"masculine":0,"feminine":1,"neuter":2, "plural":3};
    index_tree = [];
    for i in range(4):
        index_tree.append([]);  
    for j in range(4):
        index_tree[0].append([])
    for i in (1,2):
        for j in range(3):
            index_tree[i].append([])
            for k in range(2):
                index_tree[i][j].append([])
    for j in range(2):
        index_tree[3].append([])
        for k in range(2):
            index_tree[3][j].append([])

    temp_index_tree = copy.deepcopy(index_tree);
    temp_word_tree = copy.deepcopy(index_tree);
    for i in indices:
        #1. get past
        if 'past' in values[i]['details']:
            for f in past_fields:
                if f in values[i]['details']['past']:
                    for word in values[i]['details']['past'][f].split(", "): #handle multiple comma-separated words
                        temp_word_tree[0][past_fields[f]].append(word);
                        temp_index_tree[0][past_fields[f]].append(i);

        #2 get present and future
        if 'present' in values[i]['details']:
            for f in present_fields:
                if f in values[i]['details']['present']:
                    for q in quantity:
                        if q in values[i]['details']['present'][f]:
                            for word in values[i]['details']['present'][f][q].split(", "): #handle multiple comma-separated words
                                temp_word_tree[1][present_fields[f]][quantity[q]].append(word);
                                temp_index_tree[1][present_fields[f]][quantity[q]].append(i);
        if 'future' in values[i]['details']:
            for f in future_fields:
                if f in values[i]['details']['future']:
                    for q in quantity:
                        if q in values[i]['details']['future'][f]:
                            for word in values[i]['details']['future'][f][q].split(", "): #handle multiple comma-separated words
                                temp_word_tree[2][future_fields[f]][quantity[q]].append(word);
                                temp_index_tree[2][future_fields[f]][quantity[q]].append(i);
        #3 get command
        if 'command' in values[i]['details']:
            for f in command_fields:
                if f in values[i]['details']['command']:
                    for q in quantity:
                        if q in values[i]['details']['command'][f]:
                            for word in values[i]['details']['command'][f][q].split(", "): #handle multiple comma-separated words
                                temp_word_tree[3][command_fields[f]][quantity[q]].append(word);
                                temp_index_tree[3][command_fields[f]][quantity[q]].append(i);
    
    for j in range(4):
        index_tree[0][j] = parse_final_stage(temp_word_tree[0][j],temp_index_tree[0][j]);
    for i in (1,2):
        for j in range(3):
            for k in range(2):
                index_tree[i][j][k]=parse_final_stage(temp_word_tree[i][j][k],temp_index_tree[i][j][k]);
    for j in range(2):
        for k in range(2):
            index_tree[3][j][k] = parse_final_stage(temp_word_tree[3][j][k],temp_index_tree[3][j][k]);
    return index_tree;

def parse_all(directory):
    result = parse_json(directory);
    indices = range(len(result));
    part_indices = split_by_part(result, indices);
    root = dict();
    for simple_part in ["незмінне", "прийменник", "частка", "вигук","присудкове", "сполучник", "сполука", "вставне", "дієприслівник", "прислівник"]:

        temp_arr = [re.sub(r'\ \d', '', result[i]['name']) for i in part_indices[simple_part]];  # removing numbers from the end of the word with regex
        root[simple_part] = parse_final_stage(temp_arr, part_indices[simple_part]); 
    print("parsed simple words");
    root['іменник'] = parse_nouns(result,part_indices['іменник'])
    print("parsed nouns");
    root['прикметник'] = parse_adjectives(result,part_indices['прикметник'])
    print("parsed adjectives");
    root['дієслово'] =  parse_verbs(result,part_indices['дієслово'])
    print("parsed verbs");
    print("parsed all!");
    return [result,root];

def storeData(data, filename): 
    os.remove(filename)
    # Its important to use binary mode 
    storage_file = open(filename, 'ab') 
    # source, destination 
    pickle.dump(data, storage_file)                      
    storage_file.close() 
  
def loadData(filename): 
    # for reading also binary mode is important 
    storage_file = open(filename, 'rb')      
    data = pickle.load(storage_file) 
    #    for keys in db: 
    #        print(keys, '=>', db[keys]) 
    storage_file.close() 
    return data;

final_results = parse_all(directory);
storeData(final_results[0],'combined.pickle')
storeData(final_results[1],'combined_tree.pickle')


#with open('combined.json', 'w') as outfile:
#    json.dump(final_result[0], outfile, ensure_ascii=False)
#with open('combined_tree.json', 'w') as outfile:
#    json.dump(final_result[1], outfile, ensure_ascii=False)
#print("len: "+str(final_result["прийменник"]));
#print(sum([len(final_result[i]) for i in final_result]));
#for i in part_indices['незмінне']:
#    print(result[i])


'''
all_parts={ 
    "дієслово доконаного виду":
    "дієслово недоконаного виду":
    "іменник жіночого роду":
    "прикметник":
    "іменник чоловічого роду":
    "дієприкметник":
    "іменник середнього роду":
    "прислівник":
    "іменник чоловічого роду, істота':
    "іменник чоловічого або жіночого роду, істота":
    "іменник жіночого роду, істота":
    "-":
    "прикметник, вищий ступінь" : "unparsed", # "прикметник"
    "іменник середнього роду, істота": "іменник",
    "множинний іменник": "unparsed", #іменник
    "прийменник": "прийменник",
    "дієслово недоконаного і доконаного виду":"дієслово",
    "прикметник, найвищий ступінь":"unparsed",#прикметник
    "присудкове слово": "unparsed",
    "займенник з прийменником":"займенник", # to check
    "множинний іменник, істота":"unparsed", #іменник
    "прикметник з прислівником":"прикметник", # to check
    "іменник чоловічого або жіночого роду":"іменник", # fix
    "вигук":"вигук",
    "числівник кількісний":"unparsed" #числівник
    "числівник порядковий":
    "сполучник"
    "частка"
    "займенник"
    "іменник чоловічого або середнього роду, істота"
    "іменник чоловічого або середнього роду"
    "власна назва"
    "дієприслівник з часткою"
    "іменник жіночого або чоловічого роду, істота"
    "сполука":
    "дієприслівник"
    "дієприкметник з прислівником"
    "вставне слово"
    "іменник з прийменником":"unparsed"
    "займенник з часткою"
    "іменник жіночого або середнього роду"
    "незмінне слово"
    "прізвище"
    "іменник жіночого або середнього роду, істота"
    "сполучник і частка"
    "іменник жіночого або чоловічого роду"
    'числівник типу "два"'
    'прислівник з частками'
    'прислівник і частка'
    'абревіатура'
    'числівник з прийменником'
    'числівник'
}
'''

'''
дієслово 49292
іменник 87477 (містить незмінюванний іменник с прийменником)
прикметник 51161
дієприкметник 13724
прислівник 10486
- 51 (негоден, потрібен, славен)
прикметник, 2342 (прикметиник вищого ступеня)
множинний 1693 (множинний іменник)
прийменник 165 
присудкове 204
займенник 119
вигук 583
числівник 137
сполучник 147
частка 143
власна 10
дієприслівник 190
сполука 54
вставне 33
незмінне 15
прізвище 8
абревіатура 1
'''



