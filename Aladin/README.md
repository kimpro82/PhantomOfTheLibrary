# [Aladin Open API](/README.md#목록)

  [알라딘(Aladin)](https://www.aladin.co.kr/) Open API 및 크롤링을 활용하여 도서 구매 등에 실제로 유용한 편의를 제공하는 프로그램을 만들고자 함.


### \<참고 자료>

  - [알라딘 Open API 블로그](https://blog.aladin.co.kr/openapi/)
    - [예제 코드](https://blog.aladin.co.kr/openapi/5353301)
  - [알라딘 Open API 매뉴얼 (Google Docs)](https://docs.google.com/document/d/1mX-WxuoGs8Hy-QalhHcvuV17n50uGI2Sg_GHofgiePE/edit)


### \<목록>

  - [전체 중고상품 정보 조회 (2023.12.28)](#전체-중고상품-정보-조회-20231228)
  - [중고상품 보유 매장 검색 (2023.08.05)](#중고상품-보유-매장-검색-20230805)


## [전체 중고상품 정보 조회 (2023.12.28)](#목록)

  - `ItemId`(알라딘 고유 상품코드)를 기준으로 전체 중고상품 정보를 CSV 파일로 저장
    - `ItemId`(알라딘 고유 상품코드) 및 `page`를 파라미터로 request를 발송
      - URL : `https://www.aladin.co.kr/shop/UsedShop/wuseditemall.aspx?`
    - 상품 조회 API(`ItemLookUp`)는 위의 URL를 반환할 뿐이므로 직접 크롤링 수행
    - 저장 항목(7) : `상품명` `등급` `판매가` `할인률` `배송비` `판매자` `판매등급`

  - 코드 및 실행 결과
    <details>
      <summary>코드 : used_book_2.py</summary>

    ```py
    import datetime
    import re
    import pytz
    import requests
    from bs4 import BeautifulSoup
    import pandas as pd
    ```
    ```py
    # 알라딘 중고상품 전체 검색
    def search_used_item_all(_ItemIds:list) -> list:
        """
        요청한 도서의 알라딘 중고상품 전체를 검색하여 정보를 수집하는 함수입니다.

        Args:
            ItemIds (list): 검색할 중고상품 ItemIds

        Returns:
            list: 중고상품 정보 리스트
        """

        # URL 설정
        _url = "https://www.aladin.co.kr/shop/UsedShop/wuseditemall.aspx?"
        _params = {}

        _book_data = []

        for _ItemId in _ItemIds :
            # response 수신
            _params['ItemId'] = _ItemId
            _response = requests.get(_url, params=_params, timeout=1)
            _soup = BeautifulSoup(_response.text, "html.parser")

            # 마지막 페이지 번호 가져오기
            _last_page_num = re.sub(r"[^0-9]", "", _soup.find("div", class_="nright_text").text)

            # 모든 페이지에서 상품 정보 가져오기
            for _page_num in range(1, int(_last_page_num) + 1) :

                try :
                    # 상품 정보 가져오기
                    _params['page'] = _page_num
                    _response = requests.get(_url, params=_params, timeout=1)
                    _soup = BeautifulSoup(_response.text, "html.parser")
                    _books_table = _soup.find("div", class_="Ere_usedsell_table").find_all("tr")

                    # 상품 정보 저장
                    for _one_book_row in _books_table[1:]:

                        _one_book_cols = _one_book_row.find_all("td")
                        # 상품 정보 추출 : 상품명, 등급, 판매가, 할인률, 배송비, 판매자, 판매등급
                        _title = _one_book_cols[1].find_all("li")[0].text.split(",")[0].replace(" ", "")
                        _grade = _one_book_cols[2].text.replace('\n', "")
                        _price = re.sub(r"[^0-9]", "", _one_book_cols[3].find_all("li")[0].text)
                        _discount = re.sub(r"[^0-9%]", "", _one_book_cols[3].find_all("li")[1].text)
                        _delivery = re.sub(r"[^0-9]", "", _one_book_cols[3].find_all("li")[2].text)
                        _seller = _one_book_cols[4].find_all("li")[0].text
                        if _seller == " 알라딘 직접 배송 ":
                            _seller = "알라딘"
                            _seller_grade = " "
                        elif _seller == " 이 광활한 우주점 ":
                            _seller = "우주점 " + _one_book_cols[4].find_all("li")[1].text.replace(" ", "")
                            _seller_grade = " "
                        else:
                            _seller_grade = _one_book_cols[4].find_all("li")[1].text.replace(" ", "")
                        _one_book_data = [_title, _grade, _price, _discount, _delivery, _seller, _seller_grade]
                        _book_data.append(_one_book_data)

                except Exception as e:
                    print("검색 결과를 가져오지 못 했습니다:", e)
                    _book_data.append("Failed")

        return _book_data
    ```
    ```py
    def save_csv(_data_frame, _filename="aladin_used_book_list"):
        """
        데이터프레임을 CSV 파일로 저장하는 함수입니다.

        Args:
            data_frame (DataFrame): 저장할 데이터프레임
            filename (str): 저장할 파일명 (기본값: aladin_used_book_list)
        """

        _seoul_timezone = pytz.timezone('Asia/Seoul')
        _time_stamp = datetime.datetime.now(_seoul_timezone).strftime("%Y%m%d_%H%M%S")
        _path = f"Data/{_filename}_{_time_stamp}.csv"
        _data_frame.to_csv(_path, index = False, encoding = 'utf-8-sig')
        print("파일 저장을 완료하였습니다. :", _path)
    ```
    ```py
    if __name__ == "__main__":
        # 검색할 중고상품 ItemIds
        ItemIds = [
            13267376,       # 주식투자 절대지식, 브렌트 펜폴드, 에디터, 2011
            131765156,      # 주식투자 ETF로 시작하라, systrader79 외, 이레미디어, 2018
            219394356,      # 아웃퍼포머, 모튼 한센, 김영사, 2019
            259247,         # 크랙, Sky Hacker 외, 파워북, 2000
            260084          # 데미안, 헤르만 헤세, 민음사, 2000
        ]

        result = search_used_item_all(ItemIds)
        # print("\nresult : ")
        # pprint.pprint(result)

        columns = ['상품명', '등급', '판매가', '할인률', '배송비', '판매자', '판매등급']
        df = pd.DataFrame(data = result, columns=columns)
        print(df)
        save_csv(df, "aladin_used_book_list")
    ```
    </details>
    <details open="">
      <summary>실행 결과</summary>

    ```py
                  상품명  등급    판매가  할인률   배송비     판매자  판매등급
    0    [중고]주식투자절대지식   상  17000  37%  3300    라일락책  파워셀러
    1    [중고]주식투자절대지식   상  17990  33%  3300   최저가북스  파워셀러
    2    [중고]주식투자절대지식  최상  19400  28%  3300  소독한 책만  전문셀러
    3    [중고]주식투자절대지식  최상  19400  28%  4900  haisui  골드셀러
    4    [중고]주식투자절대지식  최상  20700  23%  2500    책속의책  전문셀러
    ..            ...  ..    ...  ...   ...     ...   ...
    249       [중고]데미안  최상   8980   0%  6000    깨끗한책  파워셀러
    250       [중고]데미안  최상   8990   0%  6000    깨끗한책  파워셀러
    251       [중고]데미안  최상   9000   0%  3300    시온북스  실버셀러
    252       [중고]데미안  최상   9900   0%  2500     송설북  전문셀러
    253       [중고]데미안  최상  10000   0%  3300    별바라기  골드셀러

    [254 rows x 7 columns]
    파일 저장을 완료하였습니다. : Data/aladin_used_book_list_20231228_221155.csv
    ```
    ```csv
    상품명,등급,판매가,할인률,배송비,판매자,판매등급
    [중고]주식투자절대지식,상,17000,37%,3300,라일락책,파워셀러
    [중고]주식투자절대지식,상,17990,33%,3300,최저가북스,파워셀러
    [중고]주식투자절대지식,최상,19400,28%,3300,소독한 책만,전문셀러
    ……
    [중고]데미안,최상,10000,0%,3300,별바라기,골드셀러
    ```
    </details>


## [중고상품 보유 매장 검색 (2023.08.05)](#목록)

  - ISBN13 코드를 담은 튜플 `books`(테스트용)를 순회하며 request를 발송 (`ItemOffStoreList`)
  - 사용성 제한적으로 판단
    - 오프라인 매장의 보유 중고상품만을 조회  
      (온라인 중고 / 이 광활한 우주점 / 판매자 중고 카테고리 미조회)
    - 단지 보유지점명만을 제공 (가격, 재고권수, 책 상태 등 미제공)
  - 코드 및 실행 결과
    <details>
      <summary>코드 : key.py</summary>

    ```py
    TTBKEY = {Open API 인증키}
    ```
    </details>
    <details>
      <summary>코드 : used_book.py</summary>

    ```py
    import time
    import pprint
    import requests
    import key
    ```
    ```py
    # 알라딘 API 엔드포인트 URL
    URL = 'http://www.aladin.co.kr/ttb/api/ItemOffStoreList.aspx'

    # 조회할 도서 ISBN13 리스트 (테스트)
    books = (
        '9788957825945',                                        # 전설로 떠나는 월가의 영웅 (2021)
        '9788990872449',                                        # 피터 린치의 이기는 투자 (2008)
    )

    # API 요청에 사용할 데이터
    data = {
        'TTBKey'    : key.TTBKEY,                               # 알라딘 API 키
        'ItemId'    : '',                                       # 도서 아이템 ID
        'ItemIdType': 'ISBN13',                                 # 도서 아이템 ID 타입 (ISBN13)
        'Output'    : 'js',                                     # 출력 형식 (JSON)
    }
    ```
    ```py
    def search_used_stores(_book_isbn13):
        """
        주어진 ISBN13 도서에 대한 중고상품 보유 매장을 검색하는 함수입니다.

        Args:
            _book_isbn13 (str)  : 조회할 도서의 ISBN13

        Returns:
            dict                : 중고상품 보유 매장 정보를 담은 JSON 데이터
        """
        data['ItemId']  = _book_isbn13
        response        = requests.post(URL, data=data, timeout=1)
        json_data       = response.json()
        return json_data
    ```
    ```py
    if __name__ == "__main__":
        # 주어진 도서 목록에 대해 중고상품 보유 매장 검색 수행
        for book_isbn13 in books:
            store_info  = search_used_stores(book_isbn13)
            pprint.pprint(store_info)
            if len(store_info['itemOffStoreList']) > 0:
                offNames = []
                for itemOffStore in store_info['itemOffStoreList']:
                    offNames.append(itemOffStore['offName'])
                print(offNames)

            time.sleep(1)                                       # API 요청 사이에 1초 딜레이
            print()
    ```
    </details>
    <details open="">
      <summary>실행 결과</summary>

    ```py
    {'itemOffStoreList': [],
    'link': 'http://www.aladin.co.kr/search/wsearchresult.aspx?SearchTarget=UsedStore&amp;SearchWord=K172834409&amp;partner=openAPI',
    'pubDate': 'Sat, 05 Aug 2023 07:42:07 GMT',
    'query': 'isbn13=9788957825945',
    'version': '20131101'}
    ```
    ```py
    {'itemOffStoreList': [{'link': 'http://www.aladin.co.kr/usedstore/wproduct.aspx?ItemId=2133101&amp;OffCode=SangIn&amp;partner=openAPI',
                          'offCode': 'SangIn',
                          'offName': '대구상인점'},
                          ……
                          {'link': 'http://www.aladin.co.kr/usedstore/wproduct.aspx?ItemId=2133101&amp;OffCode=Hapjeong&amp;partner=openAPI',
                          'offCode': 'Hapjeong',
                          'offName': '합정점'}],
    'link': 'http://www.aladin.co.kr/search/wsearchresult.aspx?SearchTarget=UsedStore&amp;SearchWord=8990872448&amp;partner=openAPI',
    'pubDate': 'Sat, 05 Aug 2023 07:42:08 GMT',
    'query': 'isbn13=9788990872449',
    'version': '20131101'}
    ```
    ```py
    ['대구상인점', '이수역점', '인천송도점', '일산점', '잠실새내역점', '합정점']
    ```
    </details>
