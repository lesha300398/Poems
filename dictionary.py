import pickle;

import time;
class Dictionary:
    @staticmethod
    def load_pickle(filename):
        storage_file = open(filename, 'rb')      
        data = pickle.load(storage_file) 
        storage_file.close() 
        return data;
    def __init__(self, tree_filename='combined_tree.pickle', word_array_filename='combined.pickle'):
        self.tree = Dictionary.load_pickle(tree_filename);
        #self.word_array = Dictionary.load_pickle(word_array_filename);
    @staticmethod
    def ignore_rhyme( data, rhyme,save_rhyme=False, index=-1):
        res = [];
        for i in data:
            for el in data[i]:
                if(index == -1 or index == el[1]):
                    res.append((el[0],el[1],i) if save_rhyme else el);
        return res;
    @staticmethod
    def filter_rhyme(data,rhyme,save_rhyme=False,index=-1):
        res = [];
        temp_res = [];
        if rhyme in data:
            for el in data[rhyme]:
                if(index == -1 or index == el[1]):
                    res.append((el[0],el[1],rhyme) if save_rhyme else el)
        return res;
    @staticmethod
    def SSR_filter(data, SS=-1,rhyme=-1,save_rhyme=False, index=-1):#syllables, stress, rhyme
        if(rhyme==-1):
            rhyme_handler = Dictionary.ignore_rhyme
        else:
            rhyme_handler = Dictionary.filter_rhyme
        res = []
        if(SS==-1):
            for i in data:
                res+=rhyme_handler(data[i],rhyme,save_rhyme, index);
        elif SS in data:
            res+=rhyme_handler(data[SS],rhyme, save_rhyme,index);
        return res;
    @staticmethod
    def SSR_search_word(data, word):#returns index
        res = []
        for ss in data:
            #res+=rhyme_handler(data[i],rhyme,save_rhyme);
            for i in data[ss]:
                for el in data[ss][i]:
                    if(el[0] == word):
                        return el[1];
        return -1;

    def get_verb_basics(self,persons=(0,1,2),gender=(0,1,2,3),additional_output=False):#add: (person(-1 undefined), gender(-1 undefined, 3-multiple), time (3-command))
        verbs = self.tree['дієслово'];
        res =[];
        add = [];
        quantity = [];
        if(3 in gender):
            quantity.append(1);
        if((0 in gender) or (1 in gender) or (2 in gender)):
            quantity.append(0);
        past_allowed = [];
        if(0 in quantity):
            past_allowed +=list(gender);
        if(1 in quantity):
            past_allowed.append(3);

        for pq in past_allowed:#past
            res.append(verbs[0][pq]);
            add.append(((0,1,2), (pq,), 0))
        for p in persons:#present
            for q in quantity:
                res.append(verbs[1][p][q]);
                add.append(((p,),(0,1,2) if q==0 else (3,), 1))

        for p in persons:#future
            for q in quantity:
                res.append(verbs[2][p][q]);
                add.append((p,(0,1,2) if q==0 else (3,), 2))

        for p in (x for x in persons if x < 2):#command
            for q in quantity:
                res.append(verbs[2][p][q]);
                add.append((p,(0,1,2) if q==0 else (3,), 3))
        if(additional_output):
            return (res,add);
        return res;
    def get_noun_basics(self,vidm = range(7), gender=range(4), additional_output=False): #add:  gender
        nouns = self.tree['іменник'];
        res =[];
        add= [];
        for v in vidm:
            for g in gender:
                res.append(nouns[v][g]);
                add.append((v,g))
        if(additional_output):
            return (res, add);
        return res;
    def get_adj_basics(self,vidm = range(6), gender=range(4), additional_output=False): #add:  (vidm, gender)
        adjs = self.tree['прикметник'];
        res =[];
        add =[];
        for v in vidm:
            for g in gender:
                res.append(adjs[v][g]);
                add.append((v,g));
        if(additional_output):
            return (res, add);
        return res;
    def get_all_other_basics(self):
        res = [];
        for simple_part in ["незмінне", "прийменник", "частка", "вигук","присудкове", "сполучник", "сполука", "вставне", "дієприслівник", "прислівник"]:
            res.append(self.tree[simple_part]);
        return res;
    def search_part(self, word, part):
        if(part == "іменник"):
            basics = self.get_noun_basics();
        elif(part == "прикметник"):
            basics = self.get_adj_basics();
        elif(part == "дієслово"):
            basics = self. get_verb_basics();
        elif(part in ["незмінне", "прийменник", "частка", "вигук","присудкове", "сполучник", "сполука", "вставне", "дієприслівник", "прислівник"]):
            basics = [self.tree[part]];
        res = [];
        for b in basics:
            index=Dictionary.SSR_search_word(b,word);
            if(index!=-1):
                return index;
        return -1;
    def get_word_indices(self, word):
        #check if noun
        parts = {};
        for part in ["іменник","прикметник","дієслово","незмінне", "прийменник", "частка", "вигук","присудкове", "сполучник", "сполука", "вставне", "дієприслівник", "прислівник"]:
            index = self.search_part(word, part);
            if(index!=-1):
                parts[part] = index;
        return parts;
    def get_verbs(self, SS=-1, rhyme=-1, save_rhyme=False):
        verbs = self.tree['дієслово'];
        res =[];
        for pq in verbs[0]:#past
            res+=Dictionary.SSR_filter(pq,SS,rhyme,save_rhyme);
        for p in verbs[1]:#present
            for q in p:
                res+=Dictionary.SSR_filter(q,SS,rhyme,save_rhyme);
        for p in verbs[2]:#future
            for q in p:
                res+=Dictionary.SSR_filter(q,SS,rhyme,save_rhyme);
        for p in verbs[3]:#command
            for q in p:
                res+=Dictionary.SSR_filter(q,SS,rhyme,save_rhyme);
        return res;
    @staticmethod
    def convert_syllable_string_to_tuple(syllable_string):
        syllables = len(syllable_string);
        stress = syllable_string.find('/')+1;
        return (syllables, stress)

    def get_noun_rhymes(self,vidm = range(7), gender=range(4), SS=-1, rhyme=-1,save_rhyme=False, index=-1):
        temp_res = [];
        (temp_res,add_info) = self.get_noun_basics(vidm,gender,True);
        res=[];
        for i, x in enumerate(temp_res):
            res+=[el+(add_info[i],)for el in Dictionary.SSR_filter(x,SS,rhyme,save_rhyme,index)];
        return res;    

    def get_adj_rhymes(self, vidm = range(7), gender=range(4), SS=-1, rhyme=-1,save_rhyme=False, index=-1):
        temp_res = [];
        (temp_res,add_info) = self.get_adj_basics(vidm,gender,True);
        res=[];
        for i, x in enumerate(temp_res):
            res+=[el+(add_info[i],) for el in Dictionary.SSR_filter(x,SS,rhyme,save_rhyme,index)];
        return res;    

    def get_verb_rhymes(self, persons=(0,1,2),gender=(0,1,2,3), SS=-1, rhyme=-1,save_rhyme=False, index=-1):
        temp_res = [];
        (temp_res, add_info)= self.get_verb_basics(persons,gender, True);
        res=[];
        for i, x in enumerate(temp_res):
            res+=[el+(add_info[i],) for el in Dictionary.SSR_filter(x,SS,rhyme,save_rhyme,index)];
        return res;
    
    def get_other_rhymes(self,part, SS=-1, rhyme=-1,save_rhyme=False, index=-1):
        temp_res = [];
        temp_res.append(self.tree[part]);
        res = [];
        for i in temp_res:
            res+=Dictionary.SSR_filter(i,SS,rhyme,save_rhyme,index);
        return res;


    def get_any_rhymes(self, SS=-1, rhyme=-1,save_rhyme=False, index=-1):
        temp_res = [];
        temp_res += self.get_noun_basics();
        temp_res += self.get_adj_basics();
        temp_res += self.get_verb_basics();
        temp_res += self.get_all_other_basics();
        res=[];
        for i in temp_res:
            res+=Dictionary.SSR_filter(i,SS,rhyme,save_rhyme,index);
        return res;


    def get_words(self, part, info, ending, syllables):
        # part is one of ["іменник", "прикметник", "дієслово", "дієприслівник", "прислівник"]
        # info is a dict {"vidm": int,
        #                 'gender': int} for noun, adj;
        #                {"persons": int,
        #                 "gender": int,
        #                 "time": int} for verbs;
        #                {} for the other two
        # ending is str or None
        # syllables is str like "__/_"
        # return array of matching words
        real_end = -1 if ending==None else ending;
        real_syll = Dictionary.convert_syllable_string_to_tuple(syllables);
        if(part == "іменник"):
            vidm = (info['vidm'],) if 'vidm' in info else range(7);
            gender = (info['gender'],) if 'gender' in info else range(4);
            res  = (self.get_noun_rhymes(vidm,gender, real_syll,real_end,True));
        elif(part == "прикметник"):
            vidm = (info['vidm'],) if 'vidm' in info else range(7);
            gender = (info['gender'],) if 'gender' in info else range(4);
            res  = self.get_adj_rhymes(vidm,gender, real_syll,real_end,True);
        elif(part == "дієслово"):
            persons = (info['persons'],) if 'persons' in info else range(3);
            gender = (info['gender'],) if 'gender' in info else range(4);
            time = (info['time'],) if 'time' in info else range(4) #ignored
            res  = self.get_verb_rhymes(persons,gender,time, real_syll,real_end,True);
        elif(part in ["незмінне", "прийменник", "частка", "вигук","присудкове", "сполучник", "сполука", "вставне", "дієприслівник", "прислівник"]):
            res  = self.get_other_rhymes(part, real_syll,real_end);

        return res;
    @staticmethod
    def pick_word(words):
        pass;

def simple_poem2(d):
    #word = input("type a word in ukrainian:");
    #w_index = d.get_word_indices(word)['іменник'];
    #print(w_index);
    #first_noun = d.get_noun_rhymes(range(7), range(4), (1,1),-1,True,w_index);

    #first we create verb, which is last in the sentence
    first_noun = d.get_noun_rhymes(range(7), range(4), (1,1),-1,True);
    (first_noun,first_noun_info) = first_noun[randrange(len(first_noun))];
    (first_noun,first_noun_rhyme) = first_noun;
    print(first_noun_info)

    first_ch  = (d.get_other_rhymes("частка", (1,1),-1,False));
    first_ch = first_ch[randrange(len(first_ch))];

    first_s  = (d.get_other_rhymes("сполучник", (1,1),-1,False));
    first_s = first_s[randrange(len(first_s))];

    first_excl  = (d.get_other_rhymes("вигук", (2,2),-1,False));
    first_excl = first_excl[randrange(len(first_excl))];

    first_verb = (d.get_verb_rhymes((0,1,2), (first_noun_info[1],), (3,2),-1,False));
    (first_verb,first_verb_info) = first_verb[randrange(len(first_verb))];
    
    ######################### 2nd line
    second_verb = (d.get_verb_rhymes((2,), first_verb_info[1], (3,2),-1,True));
    (second_verb,second_verb_info) = second_verb[randrange(len(second_verb))];
    (second_verb, second_verb_rhyme) = second_verb;

    second_noun = d.get_noun_rhymes((4,), range(4), (3,1),-1,False);
    (second_noun,second_noun_info) = second_noun[randrange(len(second_noun))];

    second_adj  = (d.get_adj_rhymes((second_noun_info[0],),(second_noun_info[1],), (3,2),-1,False));
    (second_adj,_) = second_adj[randrange(len(second_adj))];

    
    ######################## 3rd line
    third_verb = (d.get_verb_rhymes((2,), second_verb_info[1], (3,2),second_verb_rhyme,False));
    (third_verb,third_verb_info) = third_verb[randrange(len(third_verb))];

    third_noun = d.get_noun_rhymes((4,), range(4), (3,2),-1,False);
    (third_noun,third_noun_info) = third_noun[randrange(len(third_noun))];

    third_extra  = (d.get_other_rhymes("прислівник", (3,2),-1,False));
    third_extra = third_extra[randrange(len(third_extra))];

    
    ################################## 4th line
    fourth_noun = d.get_noun_rhymes(range(7), range(4), (3,3),first_noun_rhyme,False);
    (fourth_noun,fourth_noun_info) = fourth_noun[randrange(len(fourth_noun))];

    fourth_pr   = (d.get_other_rhymes("прийменник", (1,1),-1,False));
    fourth_pr = fourth_pr[randrange(len(fourth_pr))];
    
    fourth_noun2 = d.get_noun_rhymes((4,), range(4), (2,1),-1,False);
    (fourth_noun2,fourth_noun2_info) = fourth_noun2[randrange(len(fourth_noun2))];

    fourth_adj  = (d.get_adj_rhymes((fourth_noun_info[0],),(fourth_noun_info[1],), (3,1),-1,False));
    (fourth_adj,_) = fourth_adj[randrange(len(fourth_adj))];

    fourth_verb = (d.get_verb_rhymes((2,), (fourth_noun_info[1],), (2,1),-1,False));
    (fourth_verb,fourth_verb_info) = fourth_verb[randrange(len(fourth_verb))];
    

    lyrics = first_excl+"! "+first_s+" "+first_ch+" "+first_verb+" "+first_noun+"\n";
    lyrics += second_adj+" "+second_noun+" "+second_verb+"\n"
    lyrics += third_noun+" "+third_extra+" "+third_verb+"\n"
    lyrics += fourth_pr+" "+fourth_noun2+" "+fourth_verb+" "+fourth_noun+"\n"

    return lyrics;

def simple_poem(d):
    word = input("type a word in ukrainian:");
    w_index = d.get_word_indices(word)['іменник'];
    print(w_index);
    first_noun = d.get_noun_rhymes(range(7), range(4), (2,2),-1,True,w_index);

    #first we create verb, which is last in the sentence
    #first_noun = d.get_noun_rhymes(range(7), range(4), (2,2),-1,True);
    (first_noun,_,first_noun_rhyme, first_noun_info) = first_noun[randrange(len(first_noun))];
    print(first_noun_info)

    first_adj  = (d.get_adj_rhymes((first_noun_info[0],),(first_noun_info[1],), (4,2),-1,False));
    (first_adj,_,_) = first_adj[randrange(len(first_adj))];

    first_verb = (d.get_verb_rhymes((2,), (first_noun_info[1],), (2,2),-1,False));
    (first_verb,_,first_verb_info) = first_verb[randrange(len(first_verb))];
    ######################### 2nd line
    second_noun = d.get_noun_rhymes(range(7), range(4), (3,3),first_noun_rhyme,False);
    (second_noun,_,second_noun_info) = second_noun[randrange(len(second_noun))];

    second_adj  = (d.get_adj_rhymes((second_noun_info[0],),(second_noun_info[1],), (2,1),-1,False));
    (second_adj,_,_) = second_adj[randrange(len(second_adj))];

    second_verb = (d.get_verb_rhymes((2,), (second_noun_info[1],), (3,2),-1,False));
    (second_verb,_,second_verb_info) = second_verb[randrange(len(second_verb))];
    ######################## 3rd line
    third_noun = d.get_noun_rhymes(range(7), range(4), (3,3) ,-1, False);
    (third_noun,_,third_noun_info) = third_noun[randrange(len(third_noun))];

    third_extra  = (d.get_other_rhymes("прислівник", (3,2),-1,False));
    (third_extra,_) = third_extra[randrange(len(third_extra))];

    third_verb = (d.get_verb_rhymes((2,), (third_noun_info[1],), (2,1),-1,False));
    (third_verb,_,third_verb_info) = third_verb[randrange(len(third_verb))];
    ################################## 4th line
    fourth_noun = d.get_noun_rhymes(range(7), range(4), (2,2),first_noun_rhyme,False);
    (fourth_noun,_,fourth_noun_info) = fourth_noun[randrange(len(fourth_noun))];

    fourth_adj  = (d.get_adj_rhymes((fourth_noun_info[0],),(fourth_noun_info[1],), (3,1),-1,False));
    (fourth_adj,_,_) = fourth_adj[randrange(len(fourth_adj))];

    fourth_verb = (d.get_verb_rhymes((2,), (fourth_noun_info[1],), (3,2),-1,False));
    (fourth_verb,_,fourth_verb_info) = fourth_verb[randrange(len(fourth_verb))];


    lyrics = first_verb+" "+first_adj+" "+first_noun+"\n";
    lyrics += second_verb+" "+second_adj+" "+second_noun+"\n"
    lyrics += third_extra+" "+third_verb+" "+third_noun+"\n"
    lyrics += fourth_verb+" "+fourth_adj+" "+fourth_noun+"\n"

    return lyrics;


if __name__ == "__main__":
    from random import randrange;
    d = Dictionary();
    print(d.get_words('іменник',{'gender':2},'яти','__/_'))
    '''
    word = input("input:");
    w_index = d.get_word_indices(word)['іменник'];
    print(w_index);
    first_noun = d.get_noun_rhymes(range(7), range(4), -1,-1,True,w_index);
    print(first_noun);
    '''
    print(simple_poem(d));
    

    #first_verb_info has ((person),(gender),time)

    #tt = time.time();
    #print(time.time() -tt);
    #print(d.get_verbs(-1,'аєш',True))
    #print(len(d.tree['дієслово'][0]))