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
from pyresparser import ResumeParser
import spacy
nlp = spacy.load("en_core_web_lg")
from spacy.matcher import Matcher
from spacy.matcher import PhraseMatcher
matcher = Matcher(nlp.vocab)
import nltk
import pandas as pd
from . models import *

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
            text = []
            text.append(txt)
            # data = resumeparse.read_file(os.path.join(path, f1))
            # print(data)
            #print(txt)
            return resume_extract(request,text)


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
                    # RESERVED_WORDS = [
                    #     'school',
                    #     'college',
                    #     'univers',
                    #     'academy',
                    #     'faculty',
                    #     'institute',
                    #     'faculdades',
                    #     'Schola',
                    #     'schule',
                    #     'lise',
                    #     'lyceum',
                    #     'lycee',
                    #     'polytechnic',
                    #     'kolej',
                    #     'ünivers',
                    #     'okul',
                    # ]
                    # def extract_education(input_text):
                    #     organizations = []

                    #     # first get all the organization names using nltk
                    #     for sent in nltk.sent_tokenize(input_text):
                    #         for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
                    #             if hasattr(chunk, 'label') and chunk.label() == 'ORGANIZATION':
                    #                 organizations.append(' '.join(c[0] for c in chunk.leaves()))

                    #     # we search for each bigram and trigram for reserved words
                    #     # (college, university etc...)
                    #     education = set()
                    #     for org in organizations:
                    #         for word in RESERVED_WORDS:
                    #             if org.lower().find(word) >= 0:
                    #                 education.add(org)

                    #     return education

#***********************************skills extraction****************************


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
    print(design)
    print(type(design))
    designatn = ", ".join(design)
    print(designatn)
    # degre = get_degree(text)
    # print(degre)
    skills = extract_skills(text)
    # print(skills)
    skill = ", ".join(skills)
    # print(skill)
    # education_information = extract_education(text)

    # print(education_information)
    data={'name':name,'email':email1,'phone':res,'designation' : designatn, 'skills' :skill}
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
