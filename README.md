# DESCRIPTION

## sentimentr
**sentimentr** is a linguistic-based sentiment analysis model for formal and informal social media-style parlance. It operates at the fine-grained subsentence (clause) level. It is accompanied with strength-assigned sentiment lexica, whereby each word in a subsentence that matches with the lexica is assigned with its prior polarity score (i.e. strength). It employs a series of formal (*contrasting connectors*, *irrealis markers*, _intensification_, _diminishment_ and _negation_) and informal (_emphatic uppercasing_, _lengthening_, _exclamation marks use_, and _adjacent polar words use_) context-aware syntactic rules that refine the polarity scores of matched words. The model is thus highly sensitive to changes in polarity strength at the lexical and syntactic level, and effectively measures the global polarity strength underlying a given text  in the range of [+1, -1]. The model is lightweight, practical and computationally efficient, making it ideal for real-time processing of large-scale text streams.

## Sentiment Lexica and resources
The sentiment lexica contain formal and informal lexical items that are strength-assigned. The formal lexica were automatically boostrapped from WordNet using hand-selected seed words. The informal lexica were  bootstrapped based on their association (PMI) with a set of seed words in a large social media corpus. These were then supplemented with other freely-available lexica and manually assigned with fine-grained polarity strength scores. The informal lexica were also supplemented with common slang words, acronyms, interjections, idioms, utf-8 style emojis and emoticons. 

The resources that accompany the model are included in separate text files for easy modification and translation to other languages. These are as follows:
1. pos lexicon.txt comprises the positive formal and informal lexical items and their manually-assigned polarity scores. 
2. neg lexicon.txt comprises all the negative ones.
3. pos emojis.txt comprises all the utf-8 style positive emojis and their manually-assigned polarity scores. 
4. neg emojis.txt comprises all the negative ones.
5. pos emoticons.txt comprises  all the positive emoticons and their manually-assigned polarity scores. 
6. neg emoticons.txt comprises all the negative ones.
7. pos idioms.txt comprises all the positive idioms and a +1 polarity score for each. 
8. neg idioms.txt comprises all the negative ones, each with a -1 polarity score.
9. intensifiers.txt comprises intensifier words and their manually-assigned coefficient values.
10. diminishers.txt comprises diminisher words and their manually-assigned coefficient values.
11. negators comprises all the negator words such as *not* or *can't*. 
12. stop words.txt comprises all the irrelevant stop words that are used during preprocessing. 

## Formal contextual rules:
**1. Contrasting connectors** 
Any contrasting connectors such as *but* are useful indicators of compound sentences that contain mixed polarity. The model separates these into clauses and treats each one individually. In the case of an equal number of positive and negative subsentences (clauses) in the document, e.g. *"The animated effects were good, but the movie's storyline was bad."*, the model would prioritize the last subsentence (the one to the right of the conjunction), as this typically contains the dominant polarity. In this example, the left clause contains one polar word (good=+0.5), and the right clause contains one polar word (bad=-0.5). Since the number of positive and negative subsentences is equal, a tie breaker is initiated. Since the last subsentence is negative in this example, the positivity of the document would be reduced by 1/3 and the negativity of the document would be increased by 1/3. (see usage example below.)

**2. Irrealis markers**
Irrealis markers that express theoretical non-factual content are bypassed by the model. These typically contain modal verbs (*"I might love the movie if I watch it tomorrow."*), conditional statements (*"If I find a good camera to use, I will buy it immediately."*), and interrogative expressions (*"Do you know a good camera to buy for the trip?"*). 

**3. Dynamic negation detection**
The scope of negation was defined as a static text window of four hops after the negator word. The degree of impact a negator word is a function of the polarity score of the affected polar word. If the word has a low polarity score (<= +0.5 for positive words; >= -0.5 for negative words), the polarity is flipped (e.g. _not bad_ is flipped from -0.5 to +0.5). However, if the affected word has a high score (> +0.5 for positive words; < -0.5 for negative words), the polarity is flipped, but then the score is also decreased by ½ (e.g. _not terrible_ is first inverted from -1.0 to +1.0, and then reduced to ½ to become +0.5. Intensifier + polar word combos are treated as one lexical item by this negation algorithm.  

**4. Intensification**
Intensifiers such as *extremely* that precede polar words boost their score. E.g. *extremely good* will get a higher polarity score than *good* alone. The manually-annotated coefficient values of intensifiers vary [1.1-2.0] based on the degree that they affect the strength of the word they modify, e.g. *surpassingly=1.8*, *really=1.4*. 

**5. Diminishment**
Diminishers such as *somewhat* that precede polar words down tone their score. E.g. *somewhat good* will get a lower polarity score than *good* alone. The manually-annotated coefficient values of intensifiers vary [0.1-0.9] based on the degree that the affect the strength of the word they modify, e.g. *moderately=0.5*, *barely=0.1*. 

## Informal contextual rules:

**1. Emphatic uppercasing**
The polarity score of a polar word in all-caps is boosted by 50%. For example, _happy_ is +0.8, but _HAPPY_ is boosted by 50% to +1.2. This rule also applies for intensifier words and diminisher words. Their coefficient is increased or decreased by 10% if they are detected in all-caps.

**2. Emphatic lengthening**
In emphatically lengthened words (e.g. greattt), repeated letters are reduced to two letters (_greatt_) and to one letter (_great_), and both reduced versions are checked for availability in the lexica. In the case of formal words, WordNet is used to check whether the elongated letter in the word should be reduced to one or to two letters. If a shortened original form of the word is available in the lexica, the elongated word is boosted in score by 50%. For example, greattt is boosted by 50% from +0.8 to become +1.2.  

**3. Emphatic exclamation use**
The model boosts the score of polar words in a clause that ends with one or multiple (max of 10) exclamation symbols by 10% to 100% respectively. For example, _happy!_ is boosted by 10% from +0.8 to become +0.88, and _happy!!!_ is boosted by 30% to become +1.04.

**4. Adjacent polar word use**
When two polar words are used side-by-side (e.g. stellar joy), the second word is boosted by 50%. For example, in _stellar joy_, _stellar_ is assigned with its prior polarity score of +1.0, while the  score of _joy_ (+0.7) is boosted by 50% to become +1.05.

## Polarity score assignment
The polarity score of each matched word is refined after checking the contextual rules. The polarity score of each subsentence is the summation of the scores of all the matched words in it. The global polarity score for a document is the summation of all positive subsentence polarity scores (the raw pos polarity score) and all the negative subsentence polarity scores (the raw neg polarity score). This is normalized so as to be forcefully confined within the range [+1, -1]. 

## Future releases and improvement
The sentimentr code is far from being pythonic and efficient, and is undergoing continuous improvement. New releases will be added soon. Any collaboration and recommendations for improving the code is more than welcome.
 


# INSTALLATION

To install the sentimentr Python module from pypi.org, simple use pip:

    pip install sentimentr

The module is also available on [GitHub](https://github.com/modarwish1/sentimentr). 


# USAGE
Using sentimentr is very easy:

    from sentimentr.sentimentr import Sentiment
    
    s = Sentiment
    text = "The movie was totally awesome!! I loveeee it."
    print(s.get_polarity_score(text))
    
The output would be a numerical value representative of the global polarity score (i.e. strength) of the document:

    0.3633


The **`subjectivity`** argument is set to False by default. If set to True, it will output a dictionary that contains the **`polarity`**, and **`pos portion`**, **`neg portion`** and **`neutral portion`**, which are the percentages of the document that are positive, negative and neutral respectively. The following is an example:

    s = Sentiment
    text = "The movie was totally awesome!! I loveeee it."
    print(s.get_polarity_score(text, subjectivity=True))
The output would be the following dictionary:

    {'polarity': 0.3633, 'pos portion': 0.5, 'neg portion': 0.0, 'neutral portion': 0.5}

The **`verbose`** argument is set to False by default. This can be set to True to allow some useful details of the scoring for development purposes. The following is an example:

    s = Sentiment 
    text = "The movie was totally awesome!! I loveeee it." 
    print(s.get_polarity_score(text, verbose=True))

The output would be some details about the polarity scores and how they are refined according to the rules, followed by the global polarity score of the document. 

    ----- Input doc -----
    The movie was totally awesome!! I loveeee it.
    
    ----- Subsentence -----
    The movie was totally awesome!!
    -> 2 exclamations detected near awesome. Word polarity boosted to +1.2.
    -> int+pos match: totally awesome [+2.4]
    Raw subsentence polarity score: 2.4
    
    ----- Subsentence -----
    I loveeee it.
    -> lengthening detected on loveeee. Word normalized to love. Word polarity boosted to +1.5. 
    -> pos match: love [+1.5]
    Raw subsentence polarity score: 1.5
    Raw_subsentence_pos_polarity_scores: [2.4, 1.5]
    Raw_subsentence_neg_polarity_scores: []
    Raw_doc_pos_polarity_score 3.9
    Raw_doc_neg_polarity_score 0.0
    0.3633


# USAGE EXAMPLES

**Examples of polarity score of formal words:**

    s = Sentiment
    
    text_docs = ["okay movie", # weakly positive
                 "good movie", # strong positive
                 "great movie", # stronger
                 "amazing movie", # even stronger
                 "stellar movie", # strongest
                 "bad movie", # weakly negative
                 "poor movie", # strong negative
                 "boring movie", # stronger
                 "disgusting movie", # even stronger
                 "horrible movie"] # strongest
    
    for text_doc in text_docs:
        print(text_doc)
        print(s.get_polarity_score(text_doc))      
Output:

    okay movie
    0.01
    good movie
    0.0499
    great movie
    0.0698
    amazing movie
    0.0896
    stellar movie
    0.0995
    bad movie
    -0.0599
    poor movie
    -0.0698
    boring movie
    -0.0797
    disgusting movie
    -0.0896
    horrible movie
    -0.0995
**Examples of polarity score of informal words:**
    
    s = Sentiment
    
    text_docs = ["the og", # positive informal words
                 "gr8 movie", 
                 "delish cake", 
                 "kickass time", 
                 "diggin it", 
                 "adorbs baby", 
                 
                 "yayyy", # positive interjections
                 "woohoo",
                 "woot",
                 
                 "lmao", # positive acronyms
                 "rofl",
                 
                 "stoopid movie", # negative informal words
                 "dammit man", 
                 "what a bummer", 
                 "you are so fussy",
                 
                 "booo", # negative interjections
                 "yuck",
                 "ugh",
                 "ouch",
                 
                 "fml", # negative acronyms
                 "wth"] 
    
    for text_doc in text_docs:
        print(text_doc)
        print(s.get_polarity_score(text_doc))    
 Output:

    the og
    0.0995
    gr8 movie
    0.0896
    delish cake
    0.1435
    kickass time
    0.0995
    diggin it
    0.0995
    adorbs baby
    0.0995
    yayyy
    0.1483
    woohoo
    0.0797
    woot
    0.0995
    lmao
    0.0995
    rofl
    0.0995
    stoopid movie
    -0.0995
    dammit man
    -0.0797
    what a bummer
    -0.0797
    you are so fussy
    -0.0748
    booo
    -0.1044
    yuck
    -0.0698
    ugh
    -0.0995
    ouch
    -0.0797
    fml
    -0.0995
    wth
    -0.0698

 
   **Emoticons examples:**

    s = Sentiment
    
    text_docs = ["I am feeling :) :) :D", # positive emoticons
                 "I am feeling :( :'( :/"] # negative emoticons
    
    for text_doc in text_docs:
        print(s.get_polarity_score(text_doc, verbose=True))
Output:

    ----- Input doc -----
    I am feeling :) :) :D
    
    ----- Subsentence -----
    I am feeling :) :) :D
    -> 2 pos emoticon(s) :) [+1.6]
    -> 1 pos emoticon(s) :D [+1.0]
    Raw subsentence polarity score: 2.6
    Raw_subsentence_pos_polarity_scores: [2.6]
    Raw_subsentence_neg_polarity_scores: []
    Raw_doc_pos_polarity_score 2.6
    Raw_doc_neg_polarity_score 0.0
    0.2516
    ----- Input doc -----
    I am feeling :( :'( :/
    
    ----- Subsentence -----
    I am feeling :( :'( :/
    -> 1 neg emoticon(s) :( [-0.8]
    -> 1 neg emoticon(s) :/ [-0.8]
    -> 1 neg emoticon(s) :'( [-1.0]
    Raw subsentence polarity score: -2.6
    Raw_subsentence_pos_polarity_scores: []
    Raw_subsentence_neg_polarity_scores: [-2.6]
    Raw_doc_pos_polarity_score 0.0
    Raw_doc_neg_polarity_score -2.6
    -0.2516
    
 **Emojis examples:**

        s = Sentiment
        
        text_docs = ["I am feeling 🙂😀😎👍", # positive emojis
                     "I am feeling 😡😠😢💔"] # negative emojis
        
        for text_doc in text_docs:
            print(s.get_polarity_score(text_doc, verbose=True)) 
    
   
   Output:
    
    ----- Input doc -----
    I am feeling 🙂😀😎👍
    
    ----- Subsentence -----
    I am feeling 🙂😀😎👍
    -> pos emoji 🙂 +0.6
    
    -> pos emoji 😀 +0.9
    
    -> pos emoji 😎 +1
    
    -> pos emoji 👍 +1
    
    Raw subsentence polarity score: 3.5
    Raw_subsentence_pos_polarity_scores: [3.5]
    Raw_subsentence_neg_polarity_scores: []
    Raw_doc_pos_polarity_score 3.5
    Raw_doc_neg_polarity_score 0.0
    0.3304
    ----- Input doc -----
    I am feeling 😡😠😢💔
    
    ----- Subsentence -----
    I am feeling 😡😠😢💔
    -> neg emoji 😡 -1
    
    -> neg emoji 😠 -0.8
    
    -> neg emoji 😢 -0.7
    
    -> neg emoji 💔 -0.6
    
    Raw subsentence polarity score: -3.1
    Raw_subsentence_pos_polarity_scores: []
    Raw_subsentence_neg_polarity_scores: [-3.1]
    Raw_doc_pos_polarity_score 0.0
    Raw_doc_neg_polarity_score -3.1
    -0.2961
 **Idioms examples:**

    s = Sentiment
    
    text_docs = ["kill two birds with one stone", # positive idiom
                 "bite the dust"] # negative idiom
    
    for text_doc in text_docs:
        print(text_doc)
        print(s.get_polarity_score(text_doc))  
Output:

    kill two birds with one stone
    0.0995
    bite the dust
    -0.0995


**Negation examples**
    
    s = Sentiment
    
    text_docs = ["the movie was bad", 
                 "the movie was not bad", # simple local negator
                 "the movie was NOT bad", # all-caps negator
                 "the movie was not at all that bad", # remote negator 4 hops away
                 "the movie was not very bad", # negator on intensifier + polar word combo
                 "the movie was not terrible"] # negator on strongly polar word

    for text_doc in text_docs:
        print(text_doc)
        print(s.get_polarity_score(text_doc))   
Output:

    the movie was bad
    -0.0599
    the movie was not bad
    0.03
    the movie was NOT bad
    0.03
    the movie was not at all that bad
    0.03
    the movie was not very bad
    0.0479
    the movie was not terrible
    0.0499
**Intensification examples:**
    
    s = Sentiment
    
    text_docs = ["the movie was good", 
                 "the movie was really good", # weak intensifier
                 "the movie was REALLY good", # all-caps intensifier
                 "the movie was exceptionally good", # strong intensifier
                 "the movie was extraordinarily good", # stronger intensifier
                 "the movie perfectly good", # strongest intensifier
                 "the movie was hella good", # American slang intensifier
                 "the movie was bloody good"] # British slang intensifier
    
    for text_doc in text_docs:
        print(text_doc)
        print(s.get_polarity_score(text_doc))

Output:

    the movie was good
    0.0499
    the movie was really good
    0.0698
    the movie was REALLY good
    0.0768
    the movie was exceptionally good
    0.0847
    the movie was extraordinarily good
    0.1676
    the movie perfectly good
    0.1772
    the movie was hella good
    0.0896
    the movie was bloody good
    0.0896
**Diminishment examples:**
    
    s = Sentiment
    
    text_docs = ["the movie was good", 
                 "the movie was quite good", # weak diminisher
                 "the movie was QUITE good", # all-caps diminisher
                 "the movie was partially good", # strong diminisher
                 "the movie was nearly good", # stronger diminisher
                 "the movie barely good", # strongest diminisher
                 "the movie was kinda good", # slang diminisher
                 "the movie was sorta good"] # slang diminisher

    for text_doc in text_docs:
        print(text_doc)
        print(s.get_polarity_score(text_doc))  

Output:

    the movie was good
    0.0499
    the movie was quite good
    0.04
    the movie was QUITE good
    0.036
    the movie was partially good
    0.03
    the movie was nearly good
    0.02
    the movie barely good
    0.005
    the movie was kinda good
    0.03
    the movie was sorta good
    0.03
    
**Contrasting connector example (with verbose enabled):**
 

       s = Sentiment
        
        text_doc = "The animated effects were good, but the movie's storyline was bad."
    
        print(s.get_polarity_score(text_doc, verbose=True))  

  Output:

      ----- Input doc -----
    The animated effects were good, but the movie's storyline was bad.
    
    ----- Subsentence -----
    The animated effects were good,
    -> pos match: good [+0.5]
    Raw subsentence polarity score: 0.5
    
    ----- Subsentence -----
    the movie's storyline was bad.
    -> neg match: bad [-0.5]
    Raw subsentence polarity score: -0.5
    
    Equal num of pos and neg subsentences detected, prioritizing polarity of final subsentence (neg).
    Raw_subsentence_pos_polarity_scores: [0.5]
    Raw_subsentence_neg_polarity_scores: [-0.5]
    Raw_doc_pos_polarity_score 0.33333333333333337
    Raw_doc_neg_polarity_score -0.6666666666666666
    -0.0333
**Irrealis markers examples:**


    s = Sentiment
    
    text_docs = ["I might love the movie if I watch it tomorrow.", # modal verb 
                 "If I find a good camera to use, I will buy it immediately.", # conditional statement
                 "Do you know a good camera to buy for the trip?"] # interrogative expression
    
    for text_doc in text_docs:
        print(text_doc)
        print(s.get_polarity_score(text_doc)) 
Output:

    I might love the movie if I watch it tomorrow.
    0.0
    If I find a good camera to use, I will buy it immediately.
    0.0
    Do you know a good camera to buy for the trip?
    0.0
    
**Emphatic uppercasing examples:**

    s = Sentiment
    
    text_docs = ["the movie was good", 
                 "the movie was GOOD", # uppercasing
                 "the movie was very GOOD",
                 "the movie was VERY GOOD"] # intensifier uppercasing
    
    for text_doc in text_docs:
        print(text_doc)
        print(s.get_polarity_score(text_doc)) 

 Output:

    the movie was good
    0.0499
    the movie was GOOD
    0.0748
    the movie was very GOOD
    0.1191
    the movie was VERY GOOD
    0.1309

**Emphatic lengthening examples:**
   
    s = Sentiment
    
    text_docs = ["the movie was great", 
                 "the movie was ggggggreat", # lengthening of first letter
                 "the movie was greatttttt", # lengthening of last letter
                 "the movie was greaaaaaat", # lengthening of internal letter
                 "the movie was grrrrrreat", # lengthening of internal letter
                 "the movie was greaaaattt", # lengthening of two letters
                 "the movie was good",
                 "the movie was gooddddddd",
                 "the movie was gooooooood",
                 "the movie was amazing",
                 "the movie was amazingggggggg",
                 "the movie was amaaaaaaaazing"]

    for text_doc in text_docs:
        print(text_doc)
        print(s.get_polarity_score(text_doc))
Output:

    the movie was great
    0.0698
    the movie was ggggggreat
    0.1044
    the movie was greatttttt
    0.1044
    the movie was greaaaaaat
    0.1044
    the movie was grrrrrreat
    0.1044
    the movie was greaaaattt
    0.1044
    the movie was good
    0.0499
    the movie was gooddddddd
    0.0748
    the movie was gooooooood
    0.0748
    the movie was amazing
    0.0896
    the movie was amazingggggggg
    0.1338
    the movie was amaaaaaaaazing
    0.1338
**Emphatic exclamation use examples:**
   
    s = Sentiment
    
    text_docs = ["the movie was great", 
                 "the movie was great!", # one exclamation
                 "the movie was great!!!", # multiple
                 "the movie was great!!!!!", # some more
                 "the movie was great!!!!!!!!!!"] # ten

    for text_doc in text_docs:
        print(text_doc)
        print(s.get_polarity_score(text_doc)) 
Output:
 
    the movie was great
    0.0698
    the movie was great!
    0.0768
    the movie was great!!!
    0.0906
    the movie was great!!!!!
    0.1044
    the movie was great!!!!!!!!!!
    0.1386
**Emphatic adjacent word use examples:**
    
    s = Sentiment
    
    text_docs = ["happy",
                 "happy happy", # double positive
                 "amazingly happy", # adverb-adjective positive
                 "bad",
                 "bad bad", # double negative
                 "dangerously furious"] #adverb-adjective negative
    
    for text_doc in text_docs:
        print(text_doc)
        print(s.get_polarity_score(text_doc)) 
 Output:

    happy
    0.0797
    happy happy
    0.1961
    amazingly happy
    0.2149
    bad
    -0.0499
    bad bad
    -0.124
    dangerously furious
    -0.0797
**Various combinations of informal rules examples:**
    
    s = Sentiment
    
    text_docs = ["awesome", # positive word
                 "hella awesome", # intensifier + pos word
                 "HELLA awesome", # uppercased intensifier only
                 "HELLA AWESOME", # uppercased intensifier + pos word
                 "HELLA AWESOMEEEEE", # + lengthened pos word
                 "HELLA AWESOMEEEEE!", # + !
                 "HELLA AWESOMEEEEE!!!!!", # + multi !
                 "HELLA AWESOMEEEEE!!!!!!!!!!", # + max !
                 "HELLA AMAZINGLY AWESOMEEEEE!!!!!!!!!!"] # + adjacent polar word
    
    for text_doc in text_docs:
        print(text_doc)
        print(s.get_polarity_score(text_doc)) 
Output:

    awesome
    0.0995
    hella awesome
    0.1772
    HELLA awesome
    0.1942
    HELLA AWESOME
    0.2847
    HELLA AWESOMEEEEE
    0.4069
    HELLA AWESOMEEEEE!
    0.4401
    HELLA AWESOMEEEEE!!!!!
    0.5556
    HELLA AWESOMEEEEE!!!!!!!!!!
    0.6652
    HELLA AMAZINGLY AWESOMEEEEE!!!!!!!!!!
    0.7854

🖤🖤🖤
