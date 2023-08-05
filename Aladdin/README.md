# [Aladdin Open API](/README.md#목록)

  [알라딘(Aladdin)](https://www.aladin.co.kr/)에서 제공하는 Open API를 이용하여 도서 구매 등에 실제로 활용할 수 있는 유용한 프로그램을 만들고자 함.


### \<참고 자료>

  - [알라딘 Open API 블로그](https://blog.aladin.co.kr/openapi/)
    - [예제 코드](https://blog.aladin.co.kr/openapi/5353301)
  - [알라딘 Open API 매뉴얼 (Google Docs)](https://docs.google.com/document/d/1mX-WxuoGs8Hy-QalhHcvuV17n50uGI2Sg_GHofgiePE/edit)


### \<목록>

  - [중고상품 보유 매장 검색 (2023.08.05)](#중고상품-보유-매장-검색-20230805)


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
