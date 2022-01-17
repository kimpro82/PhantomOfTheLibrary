import os                                                           # 파일 위치 확인
import pandas as pd                                                 # 엑셀 파일 읽기
import requests
from bs4 import BeautifulSoup
import re


# 전역변수 : 위치는 추후 조정
path = "../../rsc/myloan_hist.xls"                                     # 상대 경로 : '.'으로 시작


# 엑셀 파일 존재 확인
def isFile(path) :

    if os.path.isfile(path) :
        print("파일 경로가 정상적으로 확인되었습니다.")
        return True

    else :
        print("파일 경로를 다시 확인해주세요.")
        return False


# 파일 읽기
def readFile(path) :

    df = pd.read_excel(path, header = 2)
    print(df.head(), '\n')
    return df


# 네이버>책 에서 책 제목으로 검색한 결과 리스트에서 첫번째 항목 url 얻기
def parse1(df) :

    url = "https://book.naver.com/search/search.naver?"
    params = {}
    href =[]

    # for bookTitle in df.iloc[:, 1] :
    for bookTitle in df.iloc[[0, 2, 4], 1] :                        # 테스트 : [1, 3] 에러 발생 - 추후 해결
        print(bookTitle)                                            # 테스트 : ok
        # params['query'] = requests.utils.quote(bookTitle)         # 한글 책 제목 인코딩 O
        params['query'] = bookTitle                                 # 한글 책 제목 인코딩 X
        # print(params['query'])                                    # 테스트 : ok
        response = requests.get(url, params=params)
        if response.status_code == 200 :
            print("네이버>책 페이지를 성공적으로 불러왔습니다.")
            soup = BeautifulSoup(response.text, "html.parser")

        # 테스트
        # print(soup.find("div", class_="thumb_type thumb_type2"))
        # print(soup.find("div", class_="thumb_type thumb_type2").a["href"])

        href.append(soup.find("div", class_="thumb_type thumb_type2").a["href"])

    # # 테스트 : response.text 브라우저로 확인하기
    # f = open(".//test/parsing1Test.html", 'w', encoding="UTF-8")
    # f.write(response.text)
    # f.close()

    return href


# 검색 결과 첫번째 항목의 연결 페이지에서 도서분류 얻기
def parse2(href) :

    sections = []

    for url2 in href :
        response = requests.get(url2)
        if response.status_code == 200 :
            print("책 상세 페이지를 성공적으로 불러왔습니다.")
            soup = BeautifulSoup(response.text, "html.parser")

        # 테스트
        # print(soup.find("ul", class_="history"))
        # print(soup.find("ul", class_="history").find("li").find_all("a")[0])

        section1 = []
        for sec in soup.find("ul", class_="history").li.find_all("a", class_=re.compile("N=a:bok.category,r:1+")) :
            section1.append(sec.text)
        sections.append(section1)

    return sections


# 테스트
if __name__ == '__main__' :

    if isFile(path) :
        df = readFile(path)
        href = parse1(df)
        sections = parse2(href)

        for section in sections :
            print(section)