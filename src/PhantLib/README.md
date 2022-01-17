# Phantom Of The Library

### \<목록>

- [네이버 도서분류 체계 크롤링 (2022.01.16)](/src/PhantLib#네이버-도서분류-체계-크롤링-20220116)


## [네이버 도서분류 체계 크롤링 (2022.01.16)](#목록)

#### main.py

```python
import os                                                           # 파일 위치 확인
import pandas as pd                                                 # 엑셀 파일 읽기
import requests
from bs4 import BeautifulSoup
import re
```

```python
# 엑셀 파일 존재 확인
def isFile(path) :

    if os.path.isfile(path) :
        print("파일 경로가 정상적으로 확인되었습니다.")
        return True

    else :
        print("파일 경로를 다시 확인해주세요.")
        return False
```
```
파일 경로가 정상적으로 확인되었습니다.
```

```python
# 파일 읽기
def readFile(path) :

    df = pd.read_excel(path, header = 2)
    print(df.head(), '\n')
    return df
```
```
   No.                                                 서명       저자        소장처/자료실             청구기호          등록번호         대출일         반납일
0    1                                      파이썬 증권 데이터 분석      김황후  가양도서관 / 종합자료실     005.135 김95ㅍ  YG0000030528  2021-06-08  2021-06-30
1    2                                  (초보자를 위한)C++ 200제      박준태  가양도서관 / 종합자료실     005.133 박76ㅆ  YG0000023550  2021-06-08  2021-06-30
2    3                                      (금난새의) 클래식 여행      금난새  가양도서관 / 종합자료실     670.99 금192ㅋ  YG0000000948  2021-06-01  2021-06-22
3    4  Paint It Rock : 남무성의 만화로 보는 록의 역사 . 1 = (A)com...      남무성  가양도서관 / 종합자료실  673.53 남36ㅍ v.1  YG0000017408  2021-06-01  2021-06-22
4    5                           (작곡가가 직접 가르쳐주는)작곡 테크닉 99  세가와 에이시  가양도서관 / 종합자료실      671.61 세12ㅈ  YG0000022201  2021-06-01  2021-06-22

```

```python
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
```
```
파이썬 증권 데이터 분석
네이버>책 페이지를 성공적으로 불러왔습니다.
(금난새의) 클래식 여행
네이버>책 페이지를 성공적으로 불러왔습니다.
(작곡가가 직접 가르쳐주는)작곡 테크닉 99
네이버>책 페이지를 성공적으로 불러왔습니다.
```

```python
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
```
```
책 상세 페이지를 성공적으로 불러왔습니다.
책 상세 페이지를 성공적으로 불러왔습니다.
책 상세 페이지를 성공적으로 불러왔습니다.
```

```python
# 테스트
if __name__ == '__main__' :

    if isFile(path) :
        df = readFile(path)
        href = parse1(df)
        sections = parse2(href)

        for section in sections :
            print(section)
```
```
['컴퓨터/IT', 'IT 전문서', '프로그래밍언어']
['예술/대중문화']
['예술/대중문화', '음악', '음악이론/음악사']
```