# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import pandas as pd
from datetime import datetime
import os, pdfplumber
import regex as re

def convert_pdf_to_csv(filepath):
    dirname = os.path.dirname(filepath)
    
    with pdfplumber.open(filepath) as pdf:
    #Total number of pages
        statement = {}
        totalpages = len(pdf.pages)
        for i in range(0 ,totalpages):
            pageobj = pdf.pages[i]
            statement.update({i: pageobj.extract_text()})
            
    pg = {'start':{'text':'NEW TRANSACTIONS '},
          'end':{'text':'GRAND TOTAL FOR ALL CARD ACCOUNTS'}
          }
    for location in pg.keys():
        i=0
        found=False
        while found == False:
            if pg[location]['text'] in statement[i]:
                found = True
                pg[location].update({'location':i})
            i+=1
        
    pgdeets = {}
    for p in range(pg['start']['location'], pg['end']['location']+1):
        stringfull = statement[p]
        pgdeets.update({p:{}})
        for i in range (0, statement[p].count('\n')):
            newlinetxt = stringfull[:stringfull.find('\n')]
            pgdeets[p].update({i: newlinetxt})
            stringfull = stringfull[stringfull.find('\n')+1:]
    
    patterndate = '^(([0-9])|([0-2][0-9])|([3][0-1]))\s(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)'
    patterncost = "[-+]?\d*\.\d+|\d+"
    
    df = {}
    for p in range(pg['start']['location'], pg['end']['location']+1):
        for i in range(0,len(pgdeets[p].keys())):
            indexkey = len(df)
            text = pgdeets[p][i]
            stringdate = re.search(patterndate, text)
            if not stringdate:
                continue
            stringdate = re.search(patterndate, text).group(0)
            stringcost = re.findall(patterncost,text)[-1]
            stringdesc = text[text.rfind(stringdate)+7:text.find(stringcost)-1]
            if 'PAYMENT - DBS INTERNET/WIRELESS' in stringdesc:
                continue
            
            if text[-2:] == 'CR':   numbercost = float(stringcost) * -1
            else:                    numbercost = float(stringcost)
            
            df.update({indexkey:{}})
            df[indexkey].update({'DATE':stringdate,
                         'DESCRIPTION': stringdesc,
                         'AMOUNT':numbercost})        
            
    summary = pd.DataFrame.from_dict(df, orient='index')
    summary['DATE'] = summary['DATE'].apply(lambda x: datetime.strptime(x+' '+str(datetime.now().year), '%d %b %Y'))
    
    statement_date = datetime.strftime(summary['DATE'].max(),'%b %Y').upper()

    summary.to_csv(os.path.join(dirname,'Credit Card Statement '+statement_date+'.csv'),index=False)
    
    return print(f"Done! Your file will be in the same folder, titled 'Credit Card Statement {statement_date}.csv'")

print("Hello! Welcome to DBS Bank Statement Reader.")
print("Press shift + right click on the downloaded credit card statement, and click 'Copy as Path'. \n\
Paste below!")
filepath = input("Paste the path to your file: ")[1:-1]

convert_pdf_to_csv(filepath)

# =============================================================================
# def define_cat(x):
#     i = 0
#     while i <= len(cat.keys()):
#         for category in cat.keys():
#             if category in x: return cat[category]
#             else: i+=1
#         return 'OTHERS'     
# 
# #then need to highlight if spending is a business or not kek        
# 
# summary['CATEGORY'] = summary['DESCRIPTION'].apply(lambda x: define_cat(x))
# summary['DATE_WEEK'] = summary['DATE'].apply(lambda x: datetime.strftime(x, '%Y-%W'))
# weekly_summary = pd.pivot_table(summary, values='AMOUNT', index='DATE_WEEK', columns='CATEGORY', aggfunc='sum', fill_value=0)
# weekly_summary['SUM'] = weekly_summary.sum(axis=1)
# =============================================================================


