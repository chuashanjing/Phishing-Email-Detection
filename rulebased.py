import ipaddress
import re
from difflib import get_close_matches
from urllib.parse import urlparse
from distance import distance_checker

def keyword(subject, body):
    """
    1. Open keyword.txt and reads it
    2. Splits the words by \n, keyword is now in array
    3. For every keyword, check it to the subject and body of email
    4. If it exist in subject, append to an array for counting

    Number of times word appear in Subject : Score
    0 : 0
    lesser than 2 more than 0 : 0.3
    lesser than 4 more than 2 : 0.6
    more than 4 : 1.0

    Number of times word appear in Body : Score
    0 : 0
    lesser than 2 more than 0 : 0.3
    lesser than 4 more than 2 : 0.6
    more than 4 : 1.0

    5. Add both scores and divide by 2 to get the average.
    """
    with open("data/keywords.txt", encoding="utf-8") as f:
        keywords = f.read()
    keywords = keywords.split("\n")

    detect_subj = []
    detect_body = []

    sscore = 0
    bscore = 0

    for i in keywords:
        if i in subject:
            detect_subj.append(i)
            subject_len = len(detect_subj)
            if subject_len == 0:
                sscore = 0
            elif 0 < subject_len <= 2:
                sscore = 0.3
            elif 2 < subject_len <=4:
                sscore = 0.6
            else:
                sscore = 1.0

        if i in body:
            detect_body.append(i)
            body_len = len(detect_body)
            if body_len == 0:
                bscore = 0
            elif 0 < body_len <= 2:
                bscore = 0.3
            elif 2 < body_len <=4:
                bscore = 0.6
            else:
                bscore = 1.0

    return bscore, sscore

def keyword_positioning(text, bscore, sscore):
    """
    Body Score:
    1. Reads keywords.txt
    2. Loop through all the keywords to check if keyword appeared in text
    3. Use find() to locate the position of the keyword in the text
    4. append the found keyword in an array
    5. Output: -1 or a positive number. -1 means that it is not found, a positive number means its location
    6. Use min(array) to get the lowest value. 
    7. Location of keyword = (min(array) / length of text) x 100
    8. If its less than or equal to 20, means it appeared at the first 20% of the text
    9. bscore x 1.3 (if appear), bscore * 1.0 (if appear later than 20% of text. bscore x 1 = bscore, no change)
    Subject Score:
    1. Since sscore is already calculated in keyword()
       the value of sscore itself determines if keyword is in subject.
       if sscore = 0.0, means no keyword, if sscore > 0 keyword is in subject
    2. If sscore dont exist, 0 score. if it exist x 1.5.
    3. 0.0 x 1.5 = 0.0, and sscore x 1.5 = 1.5sscore, hence multiply_sscore = sscore x 1.5
    Final Step:
    keyword_positioning_score = sscore + bscore / 2 
    """
    with open("data/keywords.txt", encoding="utf-8") as f:
        keywords = f.read()
    keywords = keywords.split("\n")
    score = 0
    all_position = []
    multiply_bscore = 0.0
    multiply_sscore = 0.0

    for i in keywords:
        position = text.find(i)
        if position != -1:
            all_position.append(position)
    
    if len(all_position) > 0:
        first_appearance = min(all_position)
        percent = first_appearance/len(text) * 100

        if percent <= 20.0:
            multiply_bscore = bscore * 1.3
        else:
            multiply_bscore = bscore * 1.0

        #if keyword appear in sscore it has 0.1 and more
        # if keyword doesnt appear in sscore it is 0.0
        # since 0 x 1.5 is still 0, it doesnt require any check
        if sscore:
            multiply_sscore = sscore * 1.5

        score = (multiply_bscore + multiply_sscore) / 2
    
    else:
        if sscore:
            multiply_sscore = sscore * 1.5
        multiply_bscore = bscore * 1.0
        score = (multiply_bscore + multiply_sscore) / 2
    
    return score

def distance_check(domain):
    """
    1. Create an array of real domains (Can be self made for testing purposes)
    2. use difflib.get_close_matches(a,b,threshold) to compare a and b. The threshold is to 70%
       so if a and b are similar by 70% it will then be added into an array

    Getting Similarity Score
    Loop through the array and use levenshtein.distance to calculate
    the difference.
    Distance is the difference between a and b.
    Distance / length of the domain = percentage of difference
    Similarity = 1 - percentage of difference

    3. Using similarity to get distance score
    Similarity : Score
    1.0 : 0.0
    less than 1.0, more than 0.75 : 0.8
    less than 0.75, more than 0.5 : 0.5
    less than 0.5 : 0.0
    """

    if not domain:
        return None

    distance_score = 0.0
    real = [
        "calxp.com", "anincons.com", "yahoo.com", "multexinvestornetwork.com",
        "coair.rsc01.com", "anchordesk.com", "intelligencepress.com", "feedback.iwon.com",
        "mailman.enron.com", "sportsline.com", "grandecom.com", "austinenergy.com",
        "austintx.com", "lpl.com", "keyad.com", "accenture.com",
        "earnings.com", "amazon.com", "ftenergy.com", "info.iwon.com",
        "concureworkplace.com", "ubspw.com", "state-bank.com", "about-cis.com",
        "integrityrs.com", "open2win.oi3.net", "swbell.net", "hotmail.com",
        "conectiv.com", "bankofamerica.com", "nymex.com", "oceanenergy.com",
        "energyargus.com", "briefing.com", "site59.rsc03.com", "flash.net",
        "buy.com", "dell.com", "am.sony.com", "sparesfinder.com",
        "aol.com", "yahoo.com", "citi.com", "att.net",
        "mediawest.com", "newsbyemail.ft.com", "gs.com", "vsnl.com",
        "netvigator.com", "db.com", "velaw.com", "tibco.com",
        "teachco.com", "satyam.net.in", "owen2002.vanderbilt.edu", "idt.net",
        "caiso.com", "us.pwcglobal.com", "americas-us.intl.pwcglobal.com", "avenueb2e.com",
        "kingstonmortgage.com", "zenax.com", "g7group-ny.com", "orbitz.com",
        "popswin.com", "casinosweeps.com", "carrfut.com", "cendantmobility.com"
    ]
    #keep those with 70% similarity
    matches = get_close_matches(domain, real, cutoff=0.7)

    if not matches:
        return 0.0
   
    for i in matches:

        length = len(i)
        distance = distance_checker(i, domain)

        similarity = 1 - distance/length

        if similarity == 1.0:
            distance_score = 0.0
        elif 0.75 <= similarity < 1.0:
            distance_score = 0.8
        elif 0.5 <= similarity < 0.75:
            distance_score = 0.5
        else:
            distance_score = 0.0

    return distance_score

def url_detection(body_of_email, email):
    """
    1. Finds URL based of http:// or https:// within the email
    2. urlparse to split the url into scheme, netloc, path, query and fragment
    3. Gets the hostname E.g 192.168.1.1 or www.google.com
    URL contains IP
    4. Check if hostname is an IP using ipaddress module. If is IP, score +0.5
    5. Check if sender domain is in URL. If it isn't, score +0.3
    URL no IP
    6. Check if sender domain is in URL. If it isn't, score +0.3
    7. Get the total score, max is 1.0
    """
    #http or https -> s?
    #[^... anything inside is accepted
    #stops before . or ,
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, body_of_email)
    score = 0

    for i in urls:
        #splits them up into scheme, netloc, path, query, fragment
        #hostname is referring to netloc
        url = urlparse(i).hostname
        try:
            #checks if its ip address
            ipaddress.ip_address(url)
            score += 0.6

            #if its an ip, check if the email is in url
            if email not in url:
                score += 0.4

        except ValueError:
            #this means its not an ip
            if email not in url:
                score += 0.3

    score = min(score, 1)


    return score
