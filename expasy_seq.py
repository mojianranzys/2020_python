#-*- coding: UTF-8 -*-
import sys
import time
import urllib
import requests
import numpy as np
from bs4 import BeautifulSoup
from openpyxl import workbook
import io
import re
import csv
import pandas as pd

def getHTMLText(url,kv):
    try:
        r = requests.request('POST',url,data=kv)
        #print(r.url)
        #print(r.status_code) # 状态码,是200表示成功，其余都是失败
        #print(type(r)) #返回r的类型
        #print(r.headers) #返回headers
        #print(r.encoding) #r.encoding:从header中charset猜测内容编码方式
        #print(r.apparent_encoding) #r.apparent_encoding:从内容中分析出编码方式（备选编码）
        #r.encoding = "utf-8" # 修改网页编码
        return(r.text)
        # # r.text:响应内容的字符串形式
        # # r.content:响应内容的二进制形式
    except:
        return "ERROR"

if __name__=="__main__":
    filename = "C:\\Users\\Administrator\\Desktop\\sequence_infor_all.csv"
    df = pd.read_csv(filename)
    nrow = df.shape[0]
    a = range(nrow)
    tmp = []
    for i in range(nrow):
        Plate = df.iloc[i,0]
        Num = df.iloc[i,1]
        Peptide_lib = df.iloc[i,2]
        Type = df.iloc[i,4]
        seq = df.iloc[i,3]
        kv = {'sequence':seq}
        url = "https://web.expasy.org/cgi-bin/protparam/protparam"
        plain_text = getHTMLText(url,kv)
        soup = BeautifulSoup(plain_text,"lxml")
        list_soup = soup.find('div', {'id':"sib_body"})

        g1 = list_soup.findAll('pre')[1]
        g1_split = str(g1).split("\n\n")
        Num_aa = re.findall(r"\d+\.?\d*", g1_split[0])[0]
        #print("Number of amino acids:%s" %(Num_aa))
        MW = re.findall(r"\d+\.?\d*", g1_split[1])[0]
        #print("Molecular weight:%s" %(MW))
        PI = re.findall(r"\d+\.?\d*", g1_split[2])[0]
        #print("Theoretical pI:%s" %(PI))
        num = []
        result = []
        for line in list_soup:
            #print("ONE ROW")
            g2 = re.search("Ext. coefficient",str(line))
            if g2:
                #print(str(line))
                str_line = str(line)
                E_split1 = str_line.split("\n\n")[1]
                Ext_coefficient1 = E_split1.split("\n")[0].split(" ")[-1]
                #print("Ext.coefficient1:%s" %(Ext_coefficient1))
                E1 = E_split1.split(",")[0].split(" ")[-1]
                #print("The E1 is assuming all pairs of Cys residues form cystines:%s"%(E1))
                E_split2 = str_line.split("\n\n")[2]
                Ext_coefficient2 = E_split2.split("\n")[1].split(" ")[-1]
                #print("Ext.coefficient2:%s" %(Ext_coefficient2))
                E2 = E_split2.split(",")[0].split(" ")[-1]
                #print("The E2 is assuming all Cys residues are reduced:%s"%(E2))
            g3 = re.search("The instability index",str(line))
            if g3:
                str_line = str(line)
                instability_index = re.findall(r"\d+\.?\d*", str_line)[0]
                #print("The instability index:%s" %(instability_index))
            g4 = re.search("The N-terminal",str(line))
            if g4:
                str_line = str(line)
                estimated_half_life = str_line.split("\n\n")[2].split("\n")
                Ehl_mammalian_reticulocytes_vitro = estimated_half_life[0].split(":")[1].split("(")[0].lstrip().strip()
                #print("The estimated half-life is : %s (mammalian reticulocytes in vitro)" %(Ehl_mammalian_reticulocytes_vitro))
                Ehl_yeast_vivo = estimated_half_life[1].split("(")[0].lstrip().strip()
                #print("The estimated half-life is : %s (yeast n vivo)" %(Ehl_yeast_vivo))
                Ehl_Escherichia_coliz_vivo = estimated_half_life[2].split("(")[0].split(">")[1].strip()
                #print("The estimated half-life is : %s (Escherichia coli in vivo)" %(Ehl_Escherichia_coliz_vivo))
            g5 = re.search("Carbon",str(line))
            if g5:
                str_line = str(line)
                str_line = re.sub(' +', ' ', str(line))
                str_line = re.sub('\t', '', str_line)
                atoms = str_line.split("\n")
                Formula = ""
                for i in atoms:
                    if i:
                        atoms_num = i.split(" ")[1] + i.split(" ")[2]
                        Formula = Formula + atoms_num
                #print("The Formula is:%s" %Formula)
            else:
                str_line = str(line).strip()
                if((str_line.split(".")[0]).isdigit() or str_line.isdigit() or  (str_line.split('-')[-1]).split(".")[-1].isdigit()):
                    num.append(str_line)
                else:
                    next 
        Total_negatively_DE = num[0]
        #print("Total number of negatively charged residues (Asp + Glu):%s" %(Total_negatively_DE))
        Total_positively_RK = num[1]
        #print("Total number of positively charged residues (Arg + Lys):%s" %(Total_positively_RK))
        Total_atomes = num[2]
        #print("Total number of atoms:%s" %(Total_atomes))
        Aliphatic_ndex = num[3]
        #print("The Aliphatic index:%s" %(Aliphatic_ndex))
        GRAVY = num[4]
        #print("Grand average of hydropathicity (GRAVY):%s" %(GRAVY))
        result=[Plate,Num,Peptide_lib,seq,Type,Num_aa,MW,PI,Total_negatively_DE,Formula,Total_atomes,
                Ext_coefficient1,E1,Ext_coefficient2,E2,Aliphatic_ndex,Ehl_mammalian_reticulocytes_vitro,
                Ehl_yeast_vivo,Ehl_Escherichia_coliz_vivo,instability_index,GRAVY]
        tmp.append(result)
        #print(tmp)

    w = open('C:\\Users\\Administrator\\Desktop\\sequence_infor_all_result.csv','wb')
    writer = csv.writer(w)
    writer.writerow(['Plate','Num','Peptide_lib','Sequence','Type','Num_aa','MW','PI','Total_negatively_DE',
            'Formula','Total_atomes','Ext_coefficient1','E1','Ext_coefficient2','E2','Aliphatic_ndex',
            'Ehl_mammalian_reticulocytes_vitro','Ehl_yeast_vivo','Ehl_Escherichia_coliz_vivo','instability_index','GRAVY'])
    writer.writerows(tmp)
    w.close()


            
    
    
            
                
            

            
            
        



