"""
알라딘 API / 중고상품 보유 매장 검색
2023.08.05

알라딘 API를 사용하여 중고상품 보유 매장을 검색하는 스크립트입니다.
"""

import time
import pprint
import requests
import key

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
