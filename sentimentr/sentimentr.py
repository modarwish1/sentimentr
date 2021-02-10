# =============================================================================
# Description: Context-aware sentiment analysis model for formal and informal social media-style parlance
# Author: Mohammad Darwich - modarwish@hotmail.com 
# =============================================================================    




# =============================================================================
# imports
# =============================================================================

from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
import re
import string
from nltk.corpus import wordnet
import math
from nltk.tokenize.casual import TweetTokenizer
import os




# =============================================================================
# Lexica and resources
# =============================================================================

"""
Added these resources to separate external txt files to allow non-developers to easily access and modify them.
"""

current_dir, this_filename = os.path.split(__file__)

pos_lex_path = os.path.join(current_dir, "lexica", "pos lexicon.txt")
pos_lex = {}
with open(pos_lex_path, "r") as f:
    for line in f:
        (key, val) = line.strip().split("\t")
        pos_lex[key] = val
f.close()

neg_lex_path = os.path.join(current_dir, "lexica", "neg lexicon.txt")
neg_lex = {}  
with open(neg_lex_path, "r") as f:
    for line in f:
        (key, val) = line.strip().split("\t")
        neg_lex[key] = val
f.close()

pos_emoticons_path = os.path.join(current_dir, "lexica", "pos emoticons.txt")
pos_emoticons = {}
with open(pos_emoticons_path, "r") as f:
    for line in f:
        (key, val) = line.strip().split("\t")
        pos_emoticons[key] = val
f.close()

neg_emoticons_path = os.path.join(current_dir, "lexica", "neg emoticons.txt")
neg_emoticons = {}
with open(neg_emoticons_path, "r") as f:
    for line in f:
        (key, val) = line.strip().split("\t")
        neg_emoticons[key] = val
f.close()

pos_emojis_path = os.path.join(current_dir, "lexica", "pos emojis.txt")
pos_emojis = {}
with open(pos_emojis_path, "r", encoding="utf-8") as f:
    for line in f:
        (key, val) = line.strip().split("\t")
        pos_emojis[key] = val
f.close()

neg_emojis_path = os.path.join(current_dir, "lexica", "neg emojis.txt")
neg_emojis = {}
with open(neg_emojis_path, "r", encoding="utf-8") as f:
    for line in f:
        (key, val) = line.strip().split("\t")
        neg_emojis[key] = val
f.close()

negators_path = os.path.join(current_dir, "lexica", "negators.txt")
negators = {}
f = open(negators_path, "r")
negators = f.read().split("\n")
f.close()

intensifiers_path = os.path.join(current_dir, "lexica", "intensifiers.txt")
intensifiers = {}
with open(intensifiers_path, "r") as f:
    for line in f:
        (key, val) = line.strip().split("\t")
        intensifiers[key] = val
f.close()

diminishers_path = os.path.join(current_dir, "lexica", "diminishers.txt")
diminishers = {}
with open(diminishers_path, "r") as f:
    for line in f:
        (key, val) = line.strip().split("\t")
        diminishers[key] = val
f.close()

pos_idioms_path = os.path.join(current_dir, "lexica", "pos idioms.txt")
f = open(pos_idioms_path, "r")
pos_idioms = f.read().split("\n")
f.close()

neg_idioms_path = os.path.join(current_dir, "lexica", "neg idioms.txt")
f = open(neg_idioms_path, "r")
neg_idioms = f.read().split("\n")
f.close()

stop_words_path = os.path.join(current_dir, "lexica", "stop words.txt")
stop_words = {}
f = open(stop_words_path, "r")
stop_words = f.read().split("\n")
f.close()




# =============================================================================
# functions
# =============================================================================

# remove punctuation
def remove_punctuation(subsentence):
    return(subsentence.translate(str.maketrans('', '', string.punctuation)))

    
# remove stopwords
def remove_stopwords(tokens):
    custom_stopwords_list = stop_words
    cleansed_tokens = [token for token in tokens if token.lower().strip() not in custom_stopwords_list]
    return(cleansed_tokens)


# get sentences
def get_sentences(input_doc):
    if input_doc[-2:] == "!!": # solve issue of NLTK tokenizer removing last '!'
        input_doc += "!"
    sentences = sent_tokenize(input_doc)
    return(sentences)


# get subsentences
def get_subsentences(sentence):
    # split into subsentences based on contrasting connectors
    subsentences = re.split(r"\s?(?:although|but|however|nevertheless|even though|yet|on the other hand|whereas|despite|conversely|regardless of|otherwise\s?)", sentence)
    subsentences = [s.strip() for s in subsentences if len(s) > 1] # remove empty items
    return(subsentences)


# check subsentence for irrealis markers
def check_irrealis_markers(subsentence):
    irrealis_marker = False
    # check for irrealis marker (interrogative)
    if subsentence[-1] == "?": 
        irrealis_marker = True
        if v: print("Irrealis marker (interrogative) detected. Ignoring subsentence.")
    # check for irrealis marker (conditional)    
    if subsentence[0:2].lower() == "if":
        irrealis_marker = True
        if v: print("Irrealis marker (conditional) detected. Ignoring subsentence.")
    # check for irrealis marker (modal verb)
    modals = {'would', 'could', 'might', 'may'}
    for modal in modals:
        if modal in subsentence.lower():
            irrealis_marker = True
            if v: print("Irrealis marker (modal verb) detected. Ignoring subsentence.")
    return(irrealis_marker)


# check for common idioms and return score +1 or -1
def check_for_idiom(subsentence):
    pos_idiom_score = 0
    neg_idiom_score = 0
    for idiom in pos_idioms:
        if idiom.strip() in subsentence.lower():
            pos_idiom_score += 1
            subsentence = subsentence.replace(idiom.strip(), "")
            if v: print("-> pos idiom: \"{}\" [+1.0]".format(idiom))
    for idiom in neg_idioms:
        if idiom.strip() in subsentence.lower():
            neg_idiom_score += -1
            subsentence = subsentence.replace(idiom.strip(), "")
            if v: print("-> neg idiom: \"{}\" [-1.0]".format(idiom))
    # returns subsentece w/o idiom for further processing
    return(pos_idiom_score, neg_idiom_score, subsentence) 


# check multi exclamation and get score 1.1 - 2.0 depending on num of '!'
def check_emphatic_multi_exclamation(subsentence):
    global exclamation_count
    if "?" not in subsentence:
        exclamation_count = subsentence.count('!')
        if exclamation_count > 10:
            exclamation_count = 10
        exclamation_score = 1 + (0.1 * exclamation_count)
        return(exclamation_score)


# check emphatic uppercasing
def check_emphatic_uppercasing(word):
     return(bool(word.isupper()))


# check if emphatic lengthening present 
def check_emphatic_lengthening(word):
    lengthening = re.compile("([a-zA-Z])\\1{2,}")
    return(bool(lengthening.search(word)))

"""
attempt to check if normalized version of lengthened word exists in WordNet, and if not, attempt to guess normalized version
"""
def replace_lengthened_word(word):
    lengthened = re.compile(r'(\w*)(\w)\2(\w*)')
    replace = r'\1\2\3'
    if wordnet.synsets(word):
        return (word)
    replace_word = lengthened.sub(replace, word)
    if replace_word != word:      
        return(replace_lengthened_word(replace_word))
    else:       
        return(word)


# returns emoticon score for subsentence
def check_emoticons(subsentence):
    emoticon_score = 0.0
    pos_emoticon_count = 0
    neg_emoticon_count = 0
    for emoticon in pos_emoticons:
        score = 0
        count = subsentence.count(emoticon)
        pos_emoticon_count += count
        if count > 0:
            polarity = pos_emoticons[emoticon]
            score = count * float(polarity)
            if v: print("-> {} pos emoticon(s) {} [+{}]".format(count, emoticon, score))  
        emoticon_score += score
    for emoticon in neg_emoticons:
        score = 0
        count = subsentence.count(emoticon)
        neg_emoticon_count += count
        if count > 0:
            polarity = neg_emoticons[emoticon]
            score = count * float(polarity)
            if v: print("-> {} neg emoticon(s) {} [{}]".format(count, emoticon, score))  
        emoticon_score += score
    return(emoticon_score, pos_emoticon_count, neg_emoticon_count)


# returns emoji score for subsentence
def check_emojis(subsentence):
    emoji_score = 0.0
    pos_emoji_count = 0
    neg_emoji_count = 0
    subsentence = TweetTokenizer().tokenize(subsentence)
    for t in subsentence:
        for emoji in pos_emojis:
            if t == emoji:
                pos_emoji_count += 1     
                polarity = pos_emojis[emoji]
                emoji_score += float(polarity)
                if v: print("-> pos emoji {} +{}".format(emoji, polarity))
        for emoji in neg_emojis:
            if t == emoji:
                neg_emoji_count += 1     
                polarity = neg_emojis[emoji]
                emoji_score += float(polarity)
                if v: print("-> neg emoji {} {}".format(emoji, polarity))
    return(emoji_score, pos_emoji_count, neg_emoji_count)




# =============================================================================
# class Sentiment
# =============================================================================

class Sentiment:
    
    # input doc and return polarity score [-1, +1]
    def get_polarity_score(input_doc, subjectivity = False, verbose = False):
        
        global v
        if verbose is True:
            v = True
        else:
            v = False
        
        if v: print("----- Input doc -----")
        if v: print(input_doc)
        
        raw_subsentence_pos_polarity_scores = []
        raw_subsentence_neg_polarity_scores = []
        
        raw_doc_pos_polarity_score = 0.0
        raw_doc_neg_polarity_score = 0.0
        
        raw_doc_polarity_score = 0.0
        
        final_doc_polarity_score = 0.0
        
        word_count = 0
        pos_matches = 0
        neg_matches = 0
        
        # get sentences
        sentences = get_sentences(input_doc)
        
        # get subsentences for each sentence
        for sentence in sentences:
            subsentences = get_subsentences(sentence)
            for subsentence in subsentences:
                if v: print("\n----- Subsentence -----")
                if v: print(subsentence)
                raw_subsentence_polarity_score = 0.0
                
                # check for irrealis marker and bypass current subsentence if True
                irrealis_marker = check_irrealis_markers(subsentence)
                if irrealis_marker == True:
                   continue
                
                # check for idioms and update pos and neg polarity scores
                pos_idiom_score, neg_idiom_score, subsentence = check_for_idiom(subsentence)
                raw_subsentence_polarity_score += (pos_idiom_score + neg_idiom_score)
                # assign 1 match for each idiom 
                pos_matches += pos_idiom_score 
                neg_matches -= neg_idiom_score
                # assume wordcount is 1 for each idiom detected
                word_count += (pos_idiom_score - neg_idiom_score) 
                
                # check multi exclamation and get score (coefficient) 1.1 - 2.0 depending on num of '!'
                exclamation_score = check_emphatic_multi_exclamation(subsentence) 
                
                # check for emoticons and return emoticon score
                emoticon_score, pos_emoticon_count, neg_emoticon_count = check_emoticons(subsentence)
                pos_matches += pos_emoticon_count 
                neg_matches += neg_emoticon_count 
                word_count += pos_emoticon_count + neg_emoticon_count 
                
                # check for emojis and return emoji score
                emoji_score, pos_emoji_count, neg_emoji_count = check_emojis(subsentence)
                pos_matches += pos_emoji_count 
                neg_matches += neg_emoji_count 
                
                # preprocessing (punctuation removal, tokenization, stopwords removal)
                subsentence = remove_punctuation(subsentence) 
                tokens = word_tokenize(subsentence) 
                tokens = remove_stopwords(tokens) 
                
                # get wordcount
                word_count += len(tokens)
    
                # iterate over subsentence tokens
                for i in range(len(tokens)):
                    
                    word = tokens[i]
    
                    # check for emphatic uppercasing and return boolean
                    emphatic_uppercasing = check_emphatic_uppercasing(word)
    
                    # check for emphatic lengthening and return boolean
                    emphatic_lengthening = check_emphatic_lengthening(word) 
                    # if emphatic lengthening detected 
                    if emphatic_lengthening == True: 
                        lengthened_word = word.lower()
                        # normalize if found in dictionary and return word 
                        word = replace_lengthened_word(lengthened_word) 
    
                    # lower case words before checking for match with lexica 
                    word = word.lower() 
    
                        ############################################
                        # handle pos word matches                  #
                        ############################################
                    
                    # derive word_polarity from lexica
                    if word in pos_lex:
                        word_polarity = float(pos_lex[word]) 
                        
                        # if uppercasing is True, boost word_polarity
                        if emphatic_uppercasing == True: 
                            word_polarity = word_polarity * 1.5
                            if v: print("-> uppercasing detected on {}. Word polarity boosted to +{}.".format(word.upper(), word_polarity))
                        # if lengthening is True, boost word_polarity     
                        if emphatic_lengthening == True: 
                            word_polarity = word_polarity * 1.5
                            if v: print("-> lengthening detected on {}. Word normalized to {}. Word polarity boosted to +{}. ".format(lengthened_word, word, word_polarity))
                        
                        # get exclamation score and boost word_polarity
                        if exclamation_score is None:
                            exclamation_score = 1
                        if exclamation_score > 1:
                            word_polarity = word_polarity * exclamation_score
                            if v: print("-> {} exclamations detected near {}. Word polarity boosted to +{}.".format(exclamation_count, word, round(word_polarity, 3)))
                        
                        # handle negation+intensifier+pos word combo 
                        if i > 0 and tokens[i-2].lower() in negators and tokens[i-1].lower() in intensifiers:
                            intensifier = tokens[i-1]
                            intensification = float(intensifiers[intensifier.lower()])
                            # if uppercased, increase coefficient value by 10%
                            if check_emphatic_uppercasing(intensifier) == True: 
                                intensification += intensification * 0.1                           
                            word_polarity = intensification * word_polarity
                            # if score is low, invert polarity
                            if word_polarity <= 0.5: 
                                word_polarity = -(word_polarity)
                            # if score is high, invert+reduce polarity
                            elif word_polarity > 0.5: 
                                word_polarity = -(word_polarity * 0.5)                
                            if v: print("-> neg+int+pos match: {} {} {} [{}]".format(tokens[i-2], intensifier, word, word_polarity))  
                            
                        # handle intensifier on pos word
                        elif i > 0 and tokens[i-1].lower() in intensifiers:
                            intensifier = tokens[i-1]  
                            intensification = float(intensifiers[intensifier.lower()])
                            # if uppercased, increase coefficient value by 10%
                            if check_emphatic_uppercasing(intensifier) == True: 
                                intensification += intensification * 0.1
                            word_polarity = intensification * word_polarity
                            if v: print("-> int+pos match: {} {} [+{}]".format(intensifier, word, word_polarity))
                            
                        # handle diminisher on pos word
                        elif i > 0 and tokens[i-1].lower() in diminishers:
                            diminisher = tokens[i-1]  
                            diminishment = float(diminishers[diminisher.lower()])
                            # if uppercased, reduce coefficient value by 10%
                            if check_emphatic_uppercasing(diminisher) == True: 
                                diminishment -= diminishment * 0.1                           
                            word_polarity = diminishment * word_polarity
                            if v: print("-> dim+pos match: {} {}  [+{}]".format(diminisher, word, word_polarity))                        
    
                        # handle adjacent pos word
                        elif i > 0 and tokens[i-1].lower() in pos_lex:
                            word_polarity = word_polarity * 1.5
                            if v: print("-> dbl pos match: {} {} [+{}]".format(tokens[i-1], word, word_polarity))
    
                        # handle negation (1-4 hops away) on word
                        elif i > 1 and (tokens[i-1].lower() in negators or tokens[i-2].lower() in negators or tokens[i-3].lower() in negators or tokens[i-4].lower() in negators):
                            # if score is low, invert polarity
                            if word_polarity <= 0.5: 
                                word_polarity = -(word_polarity)
                            # if score is high, invert+reduce polarity
                            elif word_polarity > 0.5: 
                                word_polarity = -(word_polarity * 0.5)  
                            if v: print("-> negator applied on {}: [{}]".format(word, word_polarity)) 
                                
                        # pos match
                        else:
                            if v: print("-> pos match: {} [+{}]".format(word, word_polarity))
                        
                        # increment pos/neg matches     
                        if word_polarity > 0: 
                            pos_matches += 1
                        elif word_polarity < 0:
                            neg_matches += 1
                        
                        # add word_polarity    
                        raw_subsentence_polarity_score += word_polarity                    
    
                        ############################################
                        # handle neg word matches                  #
                        ############################################
    
                    # derive word_polarity from lexica        
                    if word in neg_lex:
                        word_polarity = float(neg_lex[word]) # assign word polarity
                        # if uppercasing is True, boost word_polarity
                        if emphatic_uppercasing == True: 
                            word_polarity = word_polarity * 1.5
                            if v: print("-> uppercasing detected on {}. Word polarity boosted to {}.".format(word.upper(), word_polarity))
                        # if lengthening is True, boost word_polarity 
                        if emphatic_lengthening == True: 
                            word_polarity = word_polarity * 1.5
                            if v: print("-> lengthening detected on {}. Word normalized to {}. Word polarity boosted to {}. ".format(lengthened_word, word, word_polarity))
    
                        # get exclamation score and boost word_polarity
                        if exclamation_score is None:
                            exclamation_score = 1        
                        if exclamation_score > 1:
                            word_polarity = word_polarity * exclamation_score
                            if v: print("-> {} exclamations detected near {}. Word polarity boosted to {}.".format(exclamation_count, word, round(word_polarity, 3)))                   
                    
                        # handle negation+intensifier+neg word combo 
                        if i > 0 and tokens[i-2].lower() in negators and tokens[i-1].lower() in intensifiers:
                            intensifier = tokens[i-1]
                            intensification = float(intensifiers[intensifier.lower()])
                            # if uppercased, increase coefficient value by 10%
                            if check_emphatic_uppercasing(intensifier) == True: 
                                intensification += intensification * 0.1                         
                            word_polarity = intensification * word_polarity
                            # if score is low, invert polarity
                            if word_polarity >= -0.5: 
                                word_polarity = -(word_polarity)
                            # if score is high, invert+reduce polarity
                            elif word_polarity < -0.5: 
                                word_polarity = -(word_polarity * 0.5)                
                            if v: print("-> neg+int+neg match: {} {} {} [+{}]".format(tokens[i-2], intensifier, word, word_polarity))
                            
                        # handle intensifier on neg word
                        elif i > 0 and tokens[i-1].lower() in intensifiers:
                            intensifier = tokens[i-1]
                            intensification = float(intensifiers[intensifier.lower()])
                            # if uppercased, increase coefficient value by 10%
                            if check_emphatic_uppercasing(intensifier) == True: 
                                intensification += intensification * 0.1 
                            word_polarity = intensification * word_polarity
                            if v: print("-> int+neg match: {} {} [{}]".format(intensifier, word, word_polarity))
                            
                        # handle diminisher on neg word
                        elif i > 0 and tokens[i-1].lower() in diminishers:
                            diminisher = tokens[i-1]  
                            diminishment = float(diminishers[diminisher.lower()])
                            # if uppercased, reduce coefficient value by 10%
                            if check_emphatic_uppercasing(diminisher) == True: 
                                diminishment -= diminishment * 0.1                         
                            word_polarity = diminishment * word_polarity
                            if v: print("-> dim+neg match: {} {}  [{}]".format(diminisher, word, word_polarity))  
    
                        # handle adjacent neg word
                        elif i > 0 and tokens[i-1].lower() in neg_lex:
                            word_polarity = word_polarity * 1.5
                            if v: print("-> dbl neg match: {} {} [{}]".format(tokens[i-1], word, word_polarity))
    
                        # handle negation (1-4 hops away) on word
                        elif i > 1 and (tokens[i-1].lower() in negators or tokens[i-2].lower() in negators or tokens[i-3].lower() in negators or tokens[i-4].lower() in negators):
                            # if score is low, invert polarity
                            if word_polarity >= -0.5: 
                                word_polarity = -(word_polarity)
                            # if score is high, invert+reduce
                            elif word_polarity < -0.5: 
                                word_polarity = -(word_polarity * 0.5)  
                            if v: ("-> negator applied on {}: [+{}]".format(word, word_polarity))   
    
                        # neg match
                        else:
                            if v: print("-> neg match: {} [{}]".format(word, word_polarity))  
    
                        # increment pos/neg matches     
                        if word_polarity > 0: 
                            pos_matches += 1
                        elif word_polarity < 0:
                            neg_matches += 1
                        
                        # add word_polarty  
                        raw_subsentence_polarity_score += word_polarity           
                
                # add emoticon score to raw_subsentence_polarity_score
                raw_subsentence_polarity_score += emoticon_score 
                
                # add emoji score to raw_subsentence_polarity_score
                raw_subsentence_polarity_score += emoji_score 
                if v: print("Raw subsentence polarity score:", round(raw_subsentence_polarity_score, 4))
    
                if raw_subsentence_polarity_score > 0:
                    # add raw pos subsentence scores to list
                    raw_subsentence_pos_polarity_scores += [raw_subsentence_polarity_score] 
                    # compute overall raw pos doc polarity score
                    raw_doc_pos_polarity_score += raw_subsentence_polarity_score 
                
                elif raw_subsentence_polarity_score < 0:
                    # add raw neg subsentence scores to list
                    raw_subsentence_neg_polarity_scores += [raw_subsentence_polarity_score] 
                    # compute overall raw neg doc polarity score
                    raw_doc_neg_polarity_score += raw_subsentence_polarity_score 
                    
                else:
                    raw_subsentence_polarity_score = 0
        
        # if equal num of pos and neg subsentences
        if len(raw_subsentence_pos_polarity_scores) != 0 and len(raw_subsentence_neg_polarity_scores) != 0:                
            if len(raw_subsentence_pos_polarity_scores) == len(raw_subsentence_neg_polarity_scores): 
                
                # if final subsentence is pos, shift 1/3 of polarity to raw_doc_pos_polarity_score
                if raw_subsentence_polarity_score > 0: 
                    raw_doc_pos_polarity_score = raw_doc_pos_polarity_score + (raw_doc_pos_polarity_score * (1/3) )  
                    raw_doc_neg_polarity_score = raw_doc_neg_polarity_score - (raw_doc_neg_polarity_score * (1/3) )
                    if v: print("Equal num of pos and neg subsentences, prioritizing polarity of final subsentence (pos).") 
                
                # if final subsentence is neg, shift 1/3 of polarity to raw_neg_polarity_score    
                elif raw_subsentence_polarity_score < 0: 
                    raw_doc_pos_polarity_score = raw_doc_pos_polarity_score - (raw_doc_pos_polarity_score * (1/3) )
                    raw_doc_neg_polarity_score = raw_doc_neg_polarity_score + (raw_doc_neg_polarity_score * (1/3) )
                    if v: print("\nEqual num of pos and neg subsentences detected, prioritizing polarity of final subsentence (neg).") 
       
        if v: print("Raw_subsentence_pos_polarity_scores: " + str(raw_subsentence_pos_polarity_scores) + "\n" + "Raw_subsentence_neg_polarity_scores: " + str(raw_subsentence_neg_polarity_scores) + "\n" + "Raw_doc_pos_polarity_score " + str(raw_doc_pos_polarity_score) + "\n" "Raw_doc_neg_polarity_score " + str(raw_doc_neg_polarity_score))
       
        # compute final doc polarity score, confined to -1, 0, +1         
        raw_doc_polarity_score = raw_doc_pos_polarity_score + raw_doc_neg_polarity_score
        final_doc_polarity_score = round(( raw_doc_polarity_score / math.sqrt((raw_doc_polarity_score * raw_doc_polarity_score) + 100) ), 4)
        if final_doc_polarity_score > 1.0:
            final_doc_polarity_score == 1.0
        elif final_doc_polarity_score < -1.0:
            final_doc_polarity_score == -1.0
    
        # compute pos, neg, and neutral portions of doc, all of of which sum up to 1    
        if subjectivity is True:
            if word_count < 1:
                word_count = 1
            pos_portion = round((pos_matches / word_count), 4)
            neg_portion = round((neg_matches / word_count), 4)
            neutral_portion = round(1 - (pos_portion + neg_portion), 4)
            
            # return dict: final_doc_polarity_score, pos_portion, neg_portion, neutral_portion
            polarity_score_dict = {"polarity": final_doc_polarity_score, "pos portion": pos_portion, "neg portion": neg_portion, "neutral portion": neutral_portion}
            
            return(polarity_score_dict)
        
        # return polarity score
        return(final_doc_polarity_score)




# =============================================================================
# main
# =============================================================================

if __name__ == "__main__":
    
    s = Sentiment
    
    text_docs = ["I feel okay",
                 "I feel good.",
                 "I feel great.",
                 "I feel wonderful.",
                 "I feel absolutely wonderful.",
                 "I feel ABSOLUTELY wonderful.",
                 "I feel ABSOLUTELY WONDERFUL.",
                 "I feel ABSOLUTELY WONDERFULLL.",
                 "I feel ABSOLUTELY WONDERFULLL!",
                 "I feel ABSOLUTELY WONDERFULLL!!!",
                 "I feel ABSOLUTELY WONDERFULLL!!!!!!",
                 "I feel ABSOLUTELY WONDERFULLL!!!!!! :)",
                 "I feel ABSOLUTELY WONDERFULLL!!!!!! :D"]
    
    for text_doc in text_docs:
        print(text_doc)
        print(s.get_polarity_score(text_doc))
        
