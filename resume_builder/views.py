from cgitb import text
from sqlite3 import Cursor
from django.db import connection
from django.http.response import HttpResponse
import json
from django.shortcuts import render
import re
from rest_framework.views import APIView
from .models import *
# from rest_framework.decorators import api_view
from resume_builder.models import Candi_Personal
import slate3k as slate
import PyPDF2
import os
import docx2txt
# from pyresparser import ResumeParser
import spacy
nlp = spacy.load("en_core_web_lg")
from spacy.matcher import Matcher
from spacy.matcher import PhraseMatcher
from spacy import displacy
matcher = Matcher(nlp.vocab)
import nltk
import pandas as pd
from . models import *
import csv

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')


from django.db import connection
cur = connection.cursor()
from nltk.corpus import stopwords
# from resume_parser import resumeparse
# \spaCy
# spacy download en_core_web_sm
# load pre-trained model
nlp = spacy.load('en_core_web_sm')

# Grad all general stop words
STOPWORDS = set(stopwords.words('english'))
# nltk
# nltk.downloader stopwords
# nltk.downloader punkt
# nltk.downloader averaged_perceptron_tagger
# nltk.downloader universal_tagset
# nltk.downloader wordnet
# nltk.downloader brown
# nltk.downloader maxent_ne_chunker

path = ('D:\\Backend_parser\\resume_parser\\media\\Resumes')
# Create your views here.

base_path = os.path.dirname(__file__)
print(base_path)
file = os.path.join(base_path,"titles_combined.txt")
file = open(file, "r", encoding='utf-8')
designation_list = [line.strip().lower() for line in file]
designitionmatcher = PhraseMatcher(nlp.vocab)
patterns = [nlp.make_doc(text) for text in designation_list if len(nlp.make_doc(text)) < 10]
designitionmatcher.add("Job title", None, *patterns)
# print(123)
# print(os.getcwd())
# print(123)
class fileupload(APIView):
    # @api_view(['POST'])
    def post(self,request):
        # print(annnishhh)
        self.f=request.FILES['file']
        obj = personal() 
        obj.file = self.f
        obj.save()
        res = fileupload.resumeExtension(request,self.f)
        print("***************",res,type(res))
        
        return HttpResponse(res)

    def resumeExtension(request,f):
        
    
        f1 = str(f)
        
        if(f1.endswith('.pdf')):
            print("*****",f1,type(f1))
            f1=f1.replace(' ','_')
            # f1=f1.replace('(','')
            # f1=f1.replace(')','')
            chars = ['(',')','[',']',',','-']
            for i in chars:
                f1 = f1.replace(i,'')
        
            with open(os.path.join(path, f1),'rb') as txt:
                #print(txt)
                #text = slate.PDF(txt)
                pdfReader = PyPDF2.PdfFileReader(txt)
                pageObject = pdfReader.getPage(0)
                textt = pageObject.extractText()
                text = []
                text.append(textt)
                print(text)
                return resume_extract(request,text)
        
        elif(f1.endswith('.docx')):
            print(f1)
            f1=f1.replace(' ','_')
            txt = docx2txt.process(os.path.join(path, f1))
            txt1 = txt.replace('\n', ' ')
            txt2 = txt1.replace('\t', ' ')
            # if txt:
            #     return txt.replace('\t', ' ')
            text = []
            text.append(txt2)
            print("print text@@@@@@@@@@@@@@@@@@@@@@2", text)
            # data = ResumeParser(f1).get_extracted_data()
            # print("dataaaaaaakjhkhjkhjhkjh",data)
            asd = os.path.join(path, f1)
            print(asd, "asd filename4444444444444444444444444444")
            print(f1, "asd filename3333333333333333333333333333")
            # data1 = resumeparse.read_file(f)
            # print("kjhsdjksahdjahsd", data1)
            #print(txt)
            
            return resume_extract(request,text)
        elif(f1.endswith('.csv')):
            print("printing csv file",f1)
            #txt = csv.reader(os.path.join(path, f1))
            txt = pd.read_csv(os.path.join(path, f1), usecols= ['jobTitle','jobCategory','jobLocation','jobFunctionalArea','salaryMin','salaryMax','experienceMin','experienceMax','primarySkill','secondarySkill','jobDescription','Education','travel','jobType','tag'])
            #print("printing csv", txt)
            pa = os.path.join(path, f1)
            with open(pa, 'r') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                print(csv_reader)
                for line in csv_reader:
                    # print("***************line")
                    # print(line['jobTitle'])
                    # print("***************line")
                    try:
                        query = "insert into  dbo.PostedJobs(jobTitle,jobCategory,jobLocation,jobFunctionalArea,salaryMin,salaryMax,experienceMin,experienceMax,primarySkill,secondarySkill,jobDescription,Education,travel,jobType,tag) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                        values= (line['jobTitle'],line['jobCategory'],line['jobLocation'],line['jobFunctionalArea'],line['salaryMin'],line['salaryMax'],line['experienceMin'],line['experienceMax'],line['primarySkill'],line['secondarySkill'],line['jobDescription'],line['Education'],line['travel'],line['jobType'],line['tag'])
                        cur.execute(query,values)
                        connection.commit()
                    except Exception as e:
                        print(e)
            text = []
            # text.append(txt)
            return doc_extract(request,text)

#********************phone number extraction regular expresion**************************************
PHONE_REG = re.compile(r'[\+\(]?[0-9][0-9 .\-\(\) ( )]{8,}[0-9]')
def extract_phone_number(i):  
    phone = re.findall(PHONE_REG, i[0])
    #print('extract phone num')
    if phone:
        number = ''.join(phone[0])

        if i[0].find(number) >= 0 and len(number) < 16:
            return number
        return None

#*******************email extraction regular expresion******************************************
EMAIL_REG = re.compile(r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+')

def extract_emails(data):
    return re.findall(EMAIL_REG, data[0])
#*****************name**********************************************************************
def extract_name(resume_text):
        nlp_text = nlp(resume_text[0])

        # First name and Last name are always Proper Nouns
        # pattern_FML = [{'POS': 'PROPN', 'ENT_TYPE': 'PERSON', 'OP': '+'}]

        pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
        matcher.add('NAME',[pattern],on_match=None)

        matches = matcher(nlp_text)

        for match_id, start, end in matches:
            span = nlp_text[start:end]
            return span.text
        return ""
#**********************************designation*******************************************************************#

def job_designition(text):
        job_titles = []
        for txt in text:
            __nlp = nlp(txt.lower())
        
            matches = designitionmatcher(__nlp)
            for match_id, start, end in matches:
                span = __nlp[start:end]
                job_titles.append(span.text)
        return job_titles
#*******************************degree*******************************************************************************
# nlp = spacy.load("en_core_web_lg")
# custom_nlp2 = spacy.load(os.path.join(base_path,"degree","model"))
# custom_nlp3 = spacy.load(os.path.join(base_path,"company_working","model"))
# def get_degree(text):
#         doc = custom_nlp2(text)
#         degree = []

#         degree = [ent.text.replace("\n", " ") for ent in list(doc.ents) if ent.label_ == 'Degree']
#         return list(dict.fromkeys(degree).keys()) 





#******************************************* organization *************************************************************
# RESERVED_WORDS = [
#     'company',
#     'organization',
#     'solution',
#     'Limited'
# ]
 
 
# def extract_text_from_docx(docx_path):

#     txt = docx2txt.process(docx_path)
#     if txt:
#         return txt.replace('\t', ' ')
#     return None 
 
 
# def extract_organization(text):
#     organizations = []
 
#     # first get all the organization names using nltk
#     for sent in nltk.sent_tokenize(text):
#         for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
#             if hasattr(chunk, 'label') and chunk.label() == 'ORGANIZATION':
#                 organizations.append(' '.join(c[0] for c in chunk.leaves()))
 
#     # we search for each bigram and trigram for reserved words
#     # (college, university etc...)
#     education = set()
#     for org in organizations:
#         for word in RESERVED_WORDS:
#             if org.lower().find(word) &gt;= 0:
#                 education.add(org)
 
#     return education
 
 
# if __name__ == '__main__':
#     text = extract_text_from_docx('resume.docx')
#     education_information = extract_organization(text)
 
#     print(education_information)  # noqa: T001
#******************************     Skills extraction     ********************************************************
                # SKILLS_DB = [
                #     'machine learning',
                #     'data science',
                #     'python',
                #     'word',
                #     'excel',
                #     'English',
                #     'Html',
                #     'Css',
                #     'Javascript',
                #     'PHP',
                #     'Angular',
                #     'Frontend',
                #     'SQL',
                #     'Mysql',
                #     'React js',
                #     'Angular',
                #     'BP Configuration',
                #     'aATP',
                #     'FSCM-Credit Management',
                #     'Settlement Management',
                #     'Pricing'
                # ]
                # def extract_skills(text):
                #     stop_words = set(nltk.corpus.stopwords.words('english'))
                #     word_tokens = nltk.tokenize.word_tokenize(text)

                #     # remove the stop words
                #     filtered_tokens = [w for w in word_tokens if w not in stop_words]

                #     # remove the punctuation
                #     filtered_tokens = [w for w in word_tokens if w.isalpha()]

                #     # generate bigrams and trigrams (such as artificial intelligence)
                #     bigrams_trigrams = list(map(' '.join, nltk.everygrams(filtered_tokens, 2, 3)))

                #     # we create a set to keep the results in.
                #     found_skills = set()

                #     # we search for each token in our skills database
                #     for token in filtered_tokens:
                #         if token.lower() in SKILLS_DB:
                #             found_skills.add(token)

                #     # we search for each bigram and trigram in our skills database
                #     for ngram in bigrams_trigrams:
                #         if ngram.lower() in SKILLS_DB:
                #             found_skills.add(ngram)

                #     return found_skills
#******************************   school *************************************************
            # Education Degrees
EDUCATION = [
            'BE','B.E.', 'B.E', 'BS', 'B.S', 
            'ME', 'M.E', 'M.E.', 'MS', 'M.S', 
            'BTECH', 'B.TECH', 'M.TECH', 'MTECH', 
            'SSC', 'HSC', 'CBSE', 'ICSE', 'X', 'XII'
        ]

def extract_educations(resume_text):
    nlp_text = nlp(resume_text)

    # Sentence Tokenizer
    nlp_text = [sent.text.strip() for sent in nlp_text.sents]

    edu = {}
    # Extract education degree
    for index, text in enumerate(nlp_text):
        for tex in text.split():
            # Replace all special symbols
            tex = re.sub(r'[?|$|.|!|,]', r'', tex)
            if tex.upper() in EDUCATION and tex not in STOPWORDS:
                edu[tex] = text + nlp_text[index + 1]
    print(edu,'printing edu befor checking with resered words')
    # Extract year
    education = []
    for key in edu.keys():
        year = re.search(re.compile(r'(((20|19)(\d{2})))'), edu[key])
        if year:
            education.append((key, ''.join(year[0])))
        else:
            education.append(key)
    return education


######################################################## organization



RESERVED_WORDS = [
    'school',
    'college',
    'univers',
    'academy',
    'faculty',
    'institute',
    'organization',
    'private',
    'solutions',
    'Pvt',
    'lyceum',
    'lycee',
    'polytechnic',
    'kolej',
    'ünivers',
    'okul',
    'TECHNOLOGIES',
    'Intelligence','Testing',
    'ASAJA TECHNOLOGIES',
    'singularies ',
    'FEDORA',
    'Services',
    'SERVICES',
    'GitHub', 'SINGULARIS', 'CODELEVEN TECHNOLOGIES', 
 'EXLNCE SOLUTIONS',
 'IBM INFO SPHERE DATA'
]


sampletxt = "[This is the first sentence. This is the second one. And this is the last one.ANEESH KUMAR C D  REACT JS/ WEB DEVELOPER  MOBILE:  +91 9746161381   E-MAIL:  aneeshcd92@gmail.com  KERALA, INDIA.    CAREER OBJECTIVE:  Looking for a challenging career opportunity in the field of software engineering in well - established organization to improve my knowledge, skills and utilize my previous work experience, academic background and interpersonal skills.       REACT CERTIFICATION      Language: JavaScript, ES6, CSS, HTML.  React tools: React.js, Redux.  Front-end Development tools: Babel, Webpack, NPM.  Hands-on experience developing front end user interfaces using React JS, Redux.  Strong proficiency in JavaScript and JavaScript object model.  Experience  with RESTful API, Webpack, JSON Web Token  Works:   https://github.com/anishkumar23-01/Netflix-app  (REST API, Axios, TMDB)  https://github.com/anishkumar23-01/todo-app (CRED using functional components)  https://github.com/anishkumar23-01/olx_newapp (UI design)            SKILLS:  HTML, CSS, JAVASCRIPT, ES6, BOOTSTRAP.  REACT JS, PYTHON, ODOO, AWS.    WORK EXPERIENCE    WEB DEVELOPER         (ASAJA TECHNOLOGIES, THENGANA, KERALA)          [ FROM 06 JANUARY 2020 TO TILL DATE]  Work with Odoo Framework, Bootstrap. Troubleshoot and resolve Odoo issues.  Developing E-Commerce website using Odoo and Wordpress.  Developing several UI design for Web app using HTML, CSS, BOOTSTRAP.  Proficient understanding of code versioning tool (GitHub).  Hands-on experience developing front end user interfaces using React JS    DATA SCIENTIST/ TRAINER         (SINGULARIS SOFTWARE TECHNOLOGIES PVT. LTD, KOTTAYAM, KERALA)     [ FROM 5 APRIL 2017 – 27 DECEMBER 2019]  Creating academic Projects for students using Python, Django, Machine Learning, Artificial Intelligence.  Coordinate with internal teams to understand user requirements and provide technical solutions.  Undertaking data collection, preprocessing and analysis.  Building models to address business problems.   ML Projects :  Loan Prediction, Stock Price Prediction, Sentiment Analyzer…  AI Projects :    Attendance system using face detection, Smart AI Chat Bot.  PHP DEVELOPER          (Codeleven Technologies, Thiruvananthapuram, Kerala, India)[ From 2016 Sep to 2017 March 22]                 Project 1- Parents students Association Front end: PHP              Back end:   Mysql_i              http://www.psaweb.org/                Project 2- Online restaurant food ordering system (UK) http://www.getjoo.com/            Responsibilities    Responsible for design and development of the website.   Involving in Database and Server Maintenance.  Performing system testing and bug fixing in the PHP Code.  Environment/Languages: PHP, HTML, MYSQL, Apache Server  Configuring payment gateways for them.    Few websites done:     https://www.yallabeirut.co.uk/                                           http://al-aminkingston.co.uk/                                         https://rajbaripenketh.com/          AWARDS/ACHIEVEMENTS:     Completed 3 months training in ASP.NET at EXLNCE SOLUTIONS Kottayam. (September,2015)      Completed 6 months training in Machine Learning and Artificial Intelligence at singularis software technologies, Kottayam.              ACADEMIC QUALIFICATIONS:    2015  :  BE COMPUTER SCIENCE  from Shree Devi Institute of Technology (VTU), Mangalore.  2010  :\xa0 Higher Secondary from STATE Syllabus.   2008  :  SSLC from STATE syllabus.         MY PROFILE  Nationality                  :  India  Date of birth               :  2/9/1992  Gender                        :  Male  Address                       :  CK Sadanam(H) Thuruthy, Changanacherry,                                                        Kottayam, Kerala. Pin: 686535                   I genuinely declare that all the facts mentioned above are true to my faith, and I                 am answerable for its accuracy"
def extract_education(sampletxt):
    organizations = []

    # first get all the organization names using nltk
    #displacy.serve(sampletxt, style='ent')
    #sampletxt1 = nlp(sampletxt)
    for sent in nltk.sent_tokenize(sampletxt):
        for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
            if hasattr(chunk, 'label') and chunk.label() == 'ORGANIZATION':
                organizations.append(' '.join(c[0] for c in chunk.leaves()))
    print(organizations, "organization333333333333333333333")
    # return organizations
    educations = []
    for org in organizations:
        #for word in RESERVED_WORDS:
        print(org, "org printing.....................")
        res = [i for i in RESERVED_WORDS if org.upper() in i]
        print(res,'printing res')
        if res:
            educations.append(org)
    #     if org == 'ASAJA':
    #         print(RESERVED_WORDS.contains() (org))
    #         print('*************asaja printing****************')
    #     print(org,'printing org****************')
    #     if org.upper() in RESERVED_WORDS :
    #         educations.add(org)
    #         print("inside loop")
    # print(org,"org printing")
    return educations
    
    #print("sent$$$$$$$$$$$$$$$$$$$$$$$$$$$", sent)
    # we search for each bigram and trigram for reserved words
    # (college, university etc...)
    #print("organization@@@@@@@@@@@@@@@@2", organizations)


    #________________________________________________________________________________________________
    # education = []
    # for org in organizations:
    #     for word in RESERVED_WORDS:
    #         if org.lower().find(word):
    #             education.append(org)





    #-----------------------------------------------------------------------------------------------------------
    # print("education##################################3", education)
#     return education
    
    #print("238eeeeeeeeeeeeeeeeeeee", index)
    # print("edu!!!!!!!!!!!!!!1", org)
    # print("edu!!!!!!!!!!!!!!2", edu)
        # if org.lower() in RESERVED_WORDS:
        #     edu.add(org)
    
# if __name__ == '__main__':
#     text = extract_text_from_docx('resume.docx')
#     education_information = extract_education(text)

#     print(education_information)  # noqa: T001



#***********************************skills extraction*******************************
file = os.path.join(base_path,"LINKEDIN_SKILLS_ORIGINAL.txt")
file = open(file, "r", encoding='utf-8')    
skill = [line.strip().lower() for line in file]
skillsmatcher = PhraseMatcher(nlp.vocab)
patterns = [nlp.make_doc(text) for text in skill if len(nlp.make_doc(text)) < 10]
skillsmatcher.add("Job title", None, *patterns)
nlp = spacy.load('en_core_web_sm')
doc = nlp("There is a big dog.")
#noun_ch = nlp.noun_chunks
def extract_skills(resume_text):

        # skills = []

        # __nlp = nlp(text[0].lower())
        # # Only run nlp.make_doc to speed things up

        # matches = skillsmatcher(__nlp)
        # for match_id, start, end in matches:
        #     span = __nlp[start:end]
        #     skills.append(span.text)
        # skills = list(set(skills))
        # return skills
        nlp_text = nlp(str(resume_text))

        # removing stop words and implementing word tokenization
        tokens = [token.text for token in nlp_text if not token.is_stop]
        
        # reading the csv file
        
        # extract values
        
        skillset = []
        
        # check for one-grams (example: python)
        for token in tokens:
            if token.lower() in skill:
                skillset.append(token)
        
        # check for bi-grams and tri-grams (example: machine learning)
        for token in doc.noun_chunks:
            token = token.text.lower().strip()
            if token in skill:
                skillset.append(token)
        
        return [i.capitalize() for i in set([i.lower() for i in skillset])]
#********************sample***********************************************
piano_class_text = ('Great Piano Academy is situated'
     ' in Mayfair or the City of London and has'
   ' world-class piano instructors.')
details = []   
def extract_sample(piano_class_text):
    piano_class_doc = nlp(piano_class_text)
    for ent in piano_class_doc.ents:
        print("HELLOOOOOOOO123",ent.text, ent.start_char, ent.end_char,
        ent.label_, spacy.explain(ent.label_))
        details.append(ent.text)
    print(details,'detailsssssss')
    #displacy.serve(piano_class_doc, style='ent')


#######################################exmpl########################################

# def replace_person_names(token):
#     if token.ent_iob != 0 and token.ent_type_ == 'PERSON':
#          return '[REDACTED]'
#     return token.string

# def redact_names(nlp_doc):
#      for ent in nlp_doc.ents:
#          ent.merge()
#      tokens = map(replace_person_names, nlp_doc)
#      return ''.join(tokens)

# survey_doc = nlp(str(text))
# redact_names(survey_doc)
# print('sdahjasdhjahdkjahsdj', redact_names(survey_doc))



####################################### experience #####################################


# def getExperience(self,text,infoDict,debug=False):
#     experience=[]
#     try:
#         for sentence in self.lines:#find the index of the sentence where the degree is find and then analyse that sentence
#                 sen=" ".join([words[0].lower() for words in sentence]) #string of words in sentence
#                 if re.search('experience',sen):
#                     sen_tokenised= nltk.word_tokenize(sen)
#                     tagged = nltk.pos_tag(sen_tokenised)
#                     entities = nltk.chunk.ne_chunk(tagged)
#                     for subtree in entities.subtrees():
#                         for leaf in subtree.leaves():
#                             if leaf[1]=='CD':
#                                 experience=leaf[0]
#     except Exception as e:
#         print traceback.format_exc()
#         print e 
#     if experience:
#         infoDict['experience'] = experience
#     else:
#         infoDict['experience']=0
#     if debug:
#         print "\n", pprint(infoDict), "\n"
#         code.interact(local=locals())
#     return experience
#***********************************  university *************************************
def extract_university(text, file):
        df = pd.read_csv(file, header=None)
        universities = [i.lower() for i in df[1]]
        college_name = []
        listex = universities
        listsearch = [text.lower()]

        for i in range(len(listex)):
            for ii in range(len(listsearch)):
                
                if re.findall(listex[i], re.sub(' +', ' ', listsearch[ii])):
                
                    college_name.append(listex[i])
        
        return college_name
def doc_extract(request,text):
    
    print("printing rows")

data ={}
def resume_extract(request,text):
    res=extract_phone_number(text)
    print(res)
    email = extract_emails(text)
    print(email)
    email1 = None
    if len(email)==0:
        email1=None
    else:
        email1 = email[0]
    
    try:
        name = extract_name(text)
    except:
        name = None
    # data = resumeparse.read_file(text)
    # print(data)
    design = job_designition(text)
    print("designation initial",design)
    print(type(design))
    designatn = ", ".join(design)
    print(designatn)
    # degre = get_degree(text)
    # print(degre)
    skills = extract_skills(text)
    print("skills array", skills)
    print("1st skill", skills[1])
    skill = ", ".join(skills)
    # print(skill)
    extract_sample(str(text))
    print(extract_sample,"sample textttttttttttttt")
    educat = extract_educations(str(text))
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$111educat",educat)
    education_information = extract_education(str(text))
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$222222222222222",education_information)
    data={'name':name,'email':email1,'phone':res,'designation' : design, 'skills' :skills,'education':educat, 'organization':education_information}
    json_obj = json.dumps(data, indent = 4)
    # print(json_obj)
    insertvalue = Candi_Personal()
    insertvalue.Cname = name
    insertvalue.Cemail = email1
    insertvalue.Cphone = res
    insertvalue.save()
    # sql = "INSERT INTO dbo.resume_builder_candi_personal (Cname,Cemail,Cphone) VALUES (%s, %s, %s)"
    if designatn is not None:
        desig = designation()
        desig.designation_of_cand = designatn
        desig.save()
    if skills is not None:
        for s in skills:
            if Skills.objects.filter(skill_of_cand=s).exists():
                pass
            else:
                sk=Skills()
                sk.skill_of_cand = s
                sk.save()
                if(insertvalue is not None): 
                    obj = Cand_personal_skills()
                    obj.personalid = insertvalue
                    obj.skillid = sk
                    obj.save()
    
    # val = (name, email[0], res)
    # cursor.execute(sql, val)

    # sql = '''MERGE INTO dbo.resume_builder_candi_personal A USING  (select res  Cphone) B
    # ON (A.Cphone = B.Cphone)
    # WHEN MATCHED THEN UPDATE
    # SET Cname = name, Cemail =email[0], Cphone = res
    # WHEN NOT MATCHED THEN
    # INSERT (Cname,	Cemail, Cphone) VALUES (%s, %s, %s)'''

    #sql = 'MERGE INTO dbo.resume_builder_candi_personal A USING  (select res  Cphone) B ON (A.Cphone = B.Cphone) WHEN MATCHED THEN UPDATE SET Cname = name, Cemail = email[0], Cphone = res WHEN NOT MATCHED THEN INSERT (Cname,Cemail, Cphone) VALUES (%s, %s, %s)'
    # val = (name,email[0],res,designatn,skill)
    # print(sql)
    # cursor.execute(sql,val)

    return HttpResponse(json_obj) 
