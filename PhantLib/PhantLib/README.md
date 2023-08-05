# [Phantom Of The Library](../../README.md#phantom-of-the-library)


### \<목록>

- [네이버 도서분류 체계 크롤링 (2022.01.16)](#네이버-도서분류-체계-크롤링-20220116)  
&nbsp;- [특수문자 포함한 책 제목 검색시 오류 해결 (2022.01.31)](#--특수문자-포함한-책-제목-검색시-오류-해결-20220131)


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


### - [특수문자 포함한 책 제목 검색시 오류 해결 (2022.01.31)](#목록)

#### Mainly changed part 1 : `parse1()`
```python
# 네이버 > 책 에서 책 제목으로 검색한 결과 리스트에서 첫번째 항목 url 얻기
def parse1(df) :

    url = "https://book.naver.com/search/search.naver?"
    params = {}
    href =[]

    # for bookTitle in df.iloc[:, 1] :
    for bookTitle in df.iloc[0:5, 1] :                                      # 테스트 : 1~5행만 실행
        print("책 제목(수정 전) :", bookTitle)                               # 테스트
        bookTitleEncoded = re.sub('[^\s0-9a-zA-Z가-힣]', ' ', bookTitle)
        params['query'] = bookTitleEncoded
        print("책 제목(수정 후) :", params['query'])                         # 테스트 : ok
        response = requests.get(url, params=params)
        soup = BeautifulSoup(response.text, "html.parser")

        try :
            bookUrl = soup.find("div", class_="thumb_type thumb_type2").a["href"]
            print("검색 결과 첫 번째 책 링크 :", soup.find("div", class_="thumb_type thumb_type2").a["href"])   # 테스트
            href.append(bookUrl)
        except :
            print("검색 결과를 가져오지 못 했습니다.")                                                           # 테스트
            href.append("Failed")

    # # 테스트 : response.text 브라우저로 확인하기 (※ 한 케이스만 실행할 것)
    # f = open("../../test/parsing1Test.html", 'w', encoding="UTF-8")
    # f.write(response.text)
    # f.close()

    return href
```

#### Mainly changed part 2 : `parse2()`
```python
# 검색 결과 첫번째 항목의 연결 페이지에서 도서분류 얻기
def parse2(href) :

    sections = []

    for url2 in href :

        if url2 != "Failed" :
            response = requests.get(url2)
            soup = BeautifulSoup(response.text, "html.parser")

            # 테스트
            # print(soup.find("ul", class_="history"))
            # print(soup.find("ul", class_="history").find("li").find_all("a")[0])

            section1 = []
            for sec in soup.find("ul", class_="history").li.find_all("a", class_=re.compile("N=a:bok.category,r:1+")) :
                section1.append(sec.text)
            sections.append(section1)

        else :
            print("책 상세 페이지를 가져오는 데 실패했습니다.")
            sections.append([])

    return sections
```

#### Output
```
파일 경로가 정상적으로 확인되었습니다.
……
책 제목(수정 전) : 파이썬 증권 데이터 분석
책 제목(수정 후) : 파이썬 증권 데이터 분석
검색 결과 첫 번째 책 링크 : http://book.naver.com/bookdb/book_detail.naver?bid=16381920
책 제목(수정 전) : (초보자를 위한)C++ 200제
책 제목(수정 후) :  초보자를 위한 C   200제
검색 결과 첫 번째 책 링크 : http://book.naver.com/bookdb/book_detail.naver?bid=13553653
책 제목(수정 전) : (금난새의) 클래식 여행
책 제목(수정 후) :  금난새의  클래식 여행
검색 결과 첫 번째 책 링크 : http://book.naver.com/bookdb/book_detail.naver?bid=6942964
책 제목(수정 전) : Paint It Rock : 남무성의 만화로 보는 록의 역사 . 1 = (A)comic book of rock history
책 제목(수정 후) : Paint It Rock   남무성의 만화로 보는 록의 역사   1    A comic book of rock history
검색 결과를 가져오지 못 했습니다.
책 제목(수정 전) : (작곡가가 직접 가르쳐주는)작곡 테크닉 99
책 제목(수정 후) :  작곡가가 직접 가르쳐주는 작곡 테크닉 99
검색 결과 첫 번째 책 링크 : http://book.naver.com/bookdb/book_detail.naver?bid=13762116
책 상세 페이지를 가져오는 데 실패했습니다.
['컴퓨터/IT', 'IT 전문서', '프로그래밍언어']
['컴퓨터/IT', 'IT 전문서', '프로그래밍언어']
['예술/대중문화']
[]
['예술/대중문화', '음악', '음악이론/음악사']
```