import os
import numpy as np
import requests
import json
import gpt
import yaml
import openai

#获取access_token,有效期为30天
def token_get():
    url = "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=Z30MfIarj8EWHrRL8xo4aeyg&cl" \
          "ient_secret=5dcg2cYUUNmgIYu6oOsNrtwffg04ZEH4"
    payload = {}
    headers = {}

    r = requests.request("POST", url, headers=headers, data=payload)
    token=json.loads(r.text)['access_token']
    return token

# l_id:定位对话;     t_id:定位用户id;     s_id：定位上下文联系对话
# 用unit回答问题的基本函数
def ask_q(token,t_id,s_id,l_id,query):
    url = "https://aip.baidubce.com/rpc/2.0/unit/service/v3/chat?access_token="+token
    payload = json.dumps({
        "service_id": "S78545",
        "log_id": ""+l_id,
        "session_id": ""+s_id,
        "request": {
            "query": ""+query,
            "terminal_id": ""+t_id,
            "query_info": {
                "type": "TEXT"
            }
        },
        "version": "3.0"
    })
    headers = {
        'Content-Type': 'text/plain'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text

# 检索关键字，对应特殊回答
def key_word(x):
    word_list = ['威海校区地图','山大新闻','山大头条','学术新闻','山大要闻']
    record = np.zeros(len(word_list))
    for i in word_list:
        if x.find(i)== -1:
            pass
        else:
            record[word_list.index(i)] = 1+word_list.index(i)
    return record

# 对新闻的进一步细分与回答
def news_answer(x):
    answer=[]
    if 1 in x:
        print("这是山大头条新闻")
        files=os.walk("news/headlines")
        file_list=[]
        #遍历新闻目录下的文件夹，寻找最新的爬取到的新闻
        for root,dirs, files in files:
            for d in dirs:
                file_list.append(d)
        #print(file_list)
        path="news/headlines/"+file_list[-1]
        #print(path)
        news=[]
        for root,dirs, files in os.walk(path):
            for f in files:
                newspath=path+'/'+f
                with open(newspath, "r", encoding='utf-8') as f:
                  news.append(f.read())
        answer=answer+news



    if 2 in x:
        print("这是山大学术新闻")
        files = os.walk("news/academic")
        file_list = []
        # 遍历新闻目录下的文件夹，寻找最新的爬取到的新闻
        for root, dirs, files in files:
            for d in dirs:
                file_list.append(d)
        # print(file_list)
        path = "news/academic/" + file_list[-1]
        # print(path)
        news = []
        for root, dirs, files in os.walk(path):
            for f in files:
                newspath = path + '/' + f
                with open(newspath, "r", encoding='utf-8') as f:
                    news.append(f.read())
        answer=answer+news


    if 3 in x:
        print("这是山大要闻")
        files = os.walk("news/highlights")
        file_list = []
        # 遍历新闻目录下的文件夹，寻找最新的爬取到的新闻
        for root, dirs, files in files:
            for d in dirs:
                file_list.append(d)
        # print(file_list)
        path = "news/highlights/" + file_list[-1]
        # print(path)
        news = []
        for root, dirs, files in os.walk(path):
            for f in files:
                newspath = path + '/' + f
                with open(newspath, "r", encoding='utf-8') as f:
                    news.append(f.read())
        answer=answer+news
    return answer


# l_id:定位对话;     t_id:定位用户id;     s_id：定位上下文联系对话
def answer1(x,question,token,t_id='001', s_id="", l_id="S001"):
    if 1 in x and 2 not in x:
        #单独询问地图，返回列表，一个元素：地图地址
        print("这是山东大学威海校区的地图")
        map=["/root/Dev/ALGO/map/map.jpg"]
        return map

    elif 2 in x and 1 not in x:
     #单独询问新闻，先获取新闻进一步细分，最后以列表的形式返回所需新闻
        a=["请问您需要哪方面的新闻呢？山大头条、学术新闻、山大要闻？"]
        return a


    elif 1 in x and 2 in x:
    # 同时询问地图和新闻时，返回列表，列表第一个元素为地图地址
        a=["/root/Dev/ALGO/map/map.jpg","请问您需要哪方面的新闻呢？山大头条、学术新闻、山大要闻？"]
        print("这是您所需要的地图和新闻")
        return a

    else :
        #没有关键词时，调用unit回答问题
        response = json.loads(ask_q(token, t_id, s_id, l_id, question))
        # print(response)
        answer=[]
        try:
          a = response["result"]["context"]['SYS_PRESUMED_HIST'][1]
        except Exception as exc:
          a = "broken:" + "error-log:" + str(exc)
        answer.append(a)
        # print(answer)
        return answer

def answer2(query):

    word_list=['山大头条','学术新闻','山大要闻']
    record = np.zeros(len(word_list))
    for i in word_list:
           if query.find(i)==-1:
              pass
           else:
               record[word_list.index(i)] = 1+word_list.index(i)
    news=news_answer(record)
    # 如果列表为空，返回原问题，如何不为空，返回新闻
    return news

def answer(x,question,token,t_id='001', s_id="", l_id="S001"):
    if 3 not in x and 4 not in x and 5 not in x:
         a=answer1(x,question,token,t_id, s_id, l_id)
         if "我不知道该怎样答复您。" in a:
             A=gpt.chat(question, 0.3)
             return A
         else:
          return a
    elif 1 not in x and 2 not in x:
         a=answer2(question)
         return a
    else:
        a1=answer1(x,question,token,t_id, s_id, l_id)
        if "我不知道该怎样答复您。" in a1:
            A = gpt.chat(question, 0.3)
            a2 = answer2(question)
            a = A + a2
            return a
        else:
            a2 = answer2(question)
            a = a1 + a2
            return a




if __name__ == "__main__":
    #爬取新闻
    # destdir1 = "news/headlines"
    # destdir2 = "news/highlights"
    # destdir3 = "news/academic"
    # sdu_news.download_academic(destdir3)
    # sdu_news.download_headlines(destdir1)
    # sdu_news.download_heghlights(destdir2)

    # 先读取token
    with open("token.txt", "r") as f:  #
     token = f.read()
     # print(token)
    question=input("您好，智能校园问答系统为您服务，请问您有什么想问的呢？")
    with open(os.path.expanduser("config.yaml"), "r") as config:
        code = yaml.load(config, Loader=yaml.FullLoader)
        openai.api_key = code["OPENAI_API_KEY"]


    #获取关键词
    key=key_word(question)

    #return 返回答案，文字答案均为列表格式，还需进一步处理
    a = answer(key,question,token)

    print(a)


