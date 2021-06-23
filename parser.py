import requests
from bs4 import BeautifulSoup
import xlsxwriter
import json
class data_example:
    question_text=""
    answer_text=""
    status=""
    bank_name=""
    created_at=""
    updated_at=""
    def __str__(self):
        return self.question_text+"    "+self.answer_text+"     "+self.status+"     "+self.bank_name+"      "+self.created_at+"     "+self.updated_at

class Parser:
    
    workbook = xlsxwriter.Workbook('result.xlsx', {'constant_memory': True})
    worksheet = workbook.add_worksheet()
    row_num=0
    url = 'https://www.banki.ru/services/questions-answers/hotline/bank/sberbank/?questionPage=' #url с указанием банка
    answer_url='https://www.banki.ru/services/questions-answers/question/' #url ответов
    #парсинг ответа
    def parse_answer(self, id):

        answer = data_example() 
        #headers_dict = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"}
        res = requests.get(self.answer_url+str(id))#, headers=headers_dict)
        print(self.answer_url+str(id))
        
        temp =  BeautifulSoup(res.text)
        temp=  temp.select("div[data-module*='//cdn.banki.ru/static/bundles/ui-2018/FaqBundle/question/questio']")
        temp = (temp[0]["data-module-options"])
        temp= temp.replace("&quot;", '"')        
        temp = json.loads(temp)
        temp = temp["question"]
        
        if(self.row_num > 1000000):
            self.worksheet = self.workbook.add_worksheet()
            self.row_num=0

        answer.question_text = str(temp["questionText"])
        self.worksheet.write(self.row_num, 0, str(temp["questionText"]))
        # print("answer:"+ temp["answerText"])
        if("answerText" in temp):
            answer.answer_text = str(temp["answerText"])
            self.worksheet.write(self.row_num, 1, str(temp["answerText"]))

        answer.status = str(temp["status"])
        self.worksheet.write(self.row_num, 2, str(temp["status"]))

        answer.bank_name = str(temp["hotLine"]["bank"]["code"])
        self.worksheet.write(self.row_num, 3, str(temp["hotLine"]["bank"]["code"]))

        answer.created_at = str(temp["createdAt"])
        self.worksheet.write(self.row_num, 4, str(temp["createdAt"]))

        if("updatedAt" in temp):
            answer.updated_at = str(temp["updatedAt"])
            self.worksheet.write(self.row_num, 5, str(temp["updatedAt"]))
        self.row_num+=1        
    #получение всех вопросов со страницы и вызов парсинга по каждому ответу отдельно
    def parse_page(self, html):
        temp = html.split("questionList&quot;:")[1]
        temp = temp.split("topicList")[0]
        temp= temp.replace("&quot;", '"')
        temp = temp[:-2]
        temp = json.loads(temp)
        for x in temp["data"]:
            self.parse_answer(x["id"])
        if(len(temp["data"])>0):
            return 0
        else:
            return 1
    def start(self):
        page=1
        while True:
            #headers_dict = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"}
            r = requests.get(self.url+str(page))#, headers=headers_dict)
            print(self.url+str(page))
            if(self.parse_page(r.text)==1):                
                break                 
            page+=1            
        self.workbook.close()
parse = Parser()
parse.start()