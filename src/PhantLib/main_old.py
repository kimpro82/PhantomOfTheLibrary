# parse1() 舊 버전 (2022.01.16)


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