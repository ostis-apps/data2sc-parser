from trans import json_to_scs
from bs4 import BeautifulSoup
import requests
import re
import os
from googletrans import Translator
import json
from jinja2 import Environment, FileSystemLoader
import codecs

#import pdb; pdb.set_trace()

elements=["registration_number","supplement","condition","type_of_registration_procedure","holder__country","indication_group","expiration","filing","dispensing_medicine","administration","the_legal_basis_of_the_request","released","pediatric_indication","pediatric_dosage","safety_feature","data_update"]

#--------------------------------------------------------------------------------------------
def getRec(url):
    print(f'getRec->{url}')
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')
    return soup.findAll('tr')
#--------------------------------------------------------------------------------------------
def getOBJ(url,ndir,lang):

    rdir=os.path.dirname(os.path.realpath(__file__))
    aR=[]

    cdir=f'{rdir}/out/'

    html=requests.get(url.format(1)).text
    bs=BeautifulSoup(html,'html.parser')

    pages=bs.findAll('li',{'class':'page-item page-item-number'})
    max_pages= int(pages[len(pages)-1].text)

    if not os.path.exists(cdir):
       try:
          os.mkdir(cdir)
       except FileExistsError:
          pass

    for page_count in range(1,max_pages):
        print(f'get data from page # {page_count}...')
        url_next=url.format(page_count)
        print(f'getOBJ->{url_next}')
        aR=getData(url_next,cdir,rdir)
    return 0

def getData(url,cdir,rdir):

    rec=getRec(url)
    print(url)
    lenR=len(rec)
    cntR=0

    for i in range(1,lenR):
        col=rec[i].findAll('td')
        if len(col) > 0:
          cntR+=1
          aRC_sk={}
          aRC_en={}
          print(f'start # {cntR}')

          nCod=col[1].find('span', {'class': 'result-cell__value'}).text.strip()
          nDrug=col[2].find('span', {'class': 'result-cell__value'}).text.strip()
          nUrl=col[2].find('a',href=True)

          if not os.path.exists(f'{cdir}{nCod}/'):
               try:
                  os.mkdir(f'{cdir}{nCod}/')
               except FileExistsError:
                  pass
               #os.chdir(save_dir)

          with open(f'{cdir}{nCod}/html.ref', 'w', encoding='utf8') as file:
               html_ref=nUrl['href']
               file.write(f'Reference drug-->{html_ref}\n')
          file.close()

          for rep in [',','.','/','\\']:
               nDrug=nDrug.replace(rep,'_')

          tDrug=f"{nDrug}_cod_{nCod}"


          rect=getRec(nUrl['href'])
          lrec=len(rect)
          cntR_tbl=0

          for j in range(1,lrec):
               colt=rect[j].findAll('td')
               if len(colt) > 0:
                   cntR_tbl+=1
                   name_c=colt[0].text.strip()
                   if name_c is not None:
                      # new code from this to else
                      value_c=colt[1].text.strip()
                      a_ATC=[]
                      if name_c == 'ATC:' : 
                          a_ATC=value_c.replace('\r\n','').replace('\n\n','').split("\n")
                          for i in range(0,len(a_ATC),2):
                            nm_sk=a_ATC[i].replace(' ','_').replace('|','_').replace('-','_').replace('\n','').replace('/','|').replace('\\','|').replace('.','_').replace(',','_').replace(':','').replace(' ','_').lower()
                            #val_sk = a_ATC[i+1].replace('\n','').replace('|','_').replace('-','_').replace(' ', '_').replace('/', '|').replace('\\', '|').replace('.', '_').replace(',','_').replace(':', '').lower()
                            val_sk = a_ATC[i + 1].replace('/', '|').lower()

                            res=tr.translate(nm_sk,dest = 'en')
                            nm_en=res.text

                            #array of elements
                            #if nm_en in elements:
                            res=tr.translate(val_sk,dest = 'en')
                            val_en=res.text.replace(' ','_')
                            aRC_sk[f'{nm_en}']=val_sk
                            aRC_en[f'{nm_en}']=val_en
                      else:
                          nm_sk=name_c.replace(' ','_').replace('|','_').replace('-','_').replace('\n','').replace('/','|').replace('\\','|').replace('.','_').replace(',','_').replace(':','').replace(' ','_').lower()
                          #val_sk = value_c.replace('\n','').replace('|','_').replace('-','_').replace(' ', '_').replace('/', '|').replace('\\', '|').replace('.', '_').replace(',','_').replace(':', '').lower()
                          val_sk = value_c

                          res=tr.translate(nm_sk,dest = 'en')
                          nm_en=res.text.replace(' ','_')

                          #array of elements
                          if nm_en in elements:
                            res=tr.translate(val_sk,dest = 'en')
                            val_en=res.text
                            aRC_sk[f'{nm_en}']=val_sk
                            aRC_en[f'{nm_en}']=val_en

          cnt_link=0
          for lnk in rect:
              icon=lnk.find('img',{'class':'drug-detail__document-icon'})
              if icon is not None:
                 cnt_link+=1
                 flink_d=lnk.find('a',href=True)
                 with open(f'{cdir}{nCod}/html.ref', 'a', encoding='utf8') as file:
                      html_ref=flink_d['href']
                      file.write(f'Referense doc-->{html_ref}\n')
                 file.close()

          print(f'save reference doc...')

          #aR={}
          aP={"identifier":tDrug}
          aL={}
          aL["sk"]=tDrug
          aL["en"]=tDrug
          aP["label"]=aL
          aP['dsk']=aRC_sk
          aP['den']=aRC_en
          aP['html_ref']=f'{cdir}{nCod}/html.ref'
          #aR['sk']=aRC_sk
          #aR['en']=aRC_en
          #aP['desc']=aR
          aQ={}
          aQ[f'{tDrug}']=aP
          aF={"entities": aQ}



          res = str(aF)

          print(f'get drug {tDrug}')




          with open(f'{cdir}{nCod}/{nCod}.json', 'w', encoding='utf8') as fo:
               fo.write(json.dumps(res,ensure_ascii=False).replace('\"{','{').replace('}}\"','}}').replace('\'','\"'))
          fo.close()

          json_to_scs(f'{cdir}{nCod}/{nCod}.json',f'{cdir}',f'{rdir}/templates')

          print(f'save json...')
          print(f'stop # {cntR}')
    #delete [] from arrays
    #this is working -->{* for key in aResCol[1].keys(): print('{}'.format(aResCol[1][key])) *}
    #print(aR)
    return 
#--------------------------------------------------------------------------------------------
if __name__=="__main__":
    #for linux path
    path='/home/x/work/out/'
    #for windows path
    #path='d:/out/'

    #init translator
    tr=Translator()
    url='https://www.sukl.sk/hlavna-stranka/slovenska-verzia/databazy-a-servis/vyhladavanie-liekov-zdravotnickych-pomocok-a-zmien-v-liekovej-databaze/vyhladavanie-v-databaze-registrovanych-liekov?page_id=242&&page={}&undefined'
    getOBJ(url,'..','en')


