"""
알라딘(Aladin) 중고상품 크롤링
2023.12.28

이 스크립트는 알라딘 웹사이트에서 중고 도서 상품 정보를 수집하고,
그 결과를 CSV 파일로 저장하는 목적으로 작성되었습니다.

Usage:
1. search_aladin_used_items 함수로 알라딘 중고상품을 검색합니다.
2. save_csv 함수로 결과를 CSV 파일로 저장합니다.

"""


import datetime
import pytz
import pprint
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd


# 알라딘 중고상품 전체 검색
def search_used_item_all(_ItemIds):
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
        _response = requests.get(_url, params=_params)
        _soup = BeautifulSoup(_response.text, "html.parser")

        # 마지막 페이지 번호 가져오기
        _last_page_num = re.sub(r"[^0-9]", "", _soup.find("div", class_="nright_text").text)

        # 모든 페이지에서 상품 정보 가져오기
        for _page_num in range(1, int(_last_page_num) + 1) :

            try :
                # 상품 정보 가져오기
                _params['page'] = _page_num
                _response = requests.get(_url, params=_params)
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

            except :
                print("검색 결과를 가져오지 못 했습니다.")
                _data.append("Failed")

    return _book_data


def save_csv(_data_frame, _filename="aladin_used_book_list"):
    """
    데이터프레임을 CSV 파일로 저장하는 함수입니다.

    Args:
        data_frame (DataFrame): 저장할 데이터프레임
        filename (str): 저장할 파일명 (기본값: aladin_used_book_list)
    """

    _seoul_timezone = pytz.timezone('Asia/Seoul')
    _time_stamp = datetime.datetime.now(_seoul_timezone).strftime("%Y%m%d_%H%M%S")
    _path = f"Data/{_filename}_{_time_stamp}.xlsx"
    _data_frame.to_csv(_path, index = False)
    print("파일 저장을 완료하였습니다. :", _path)


if __name__ == "__main__":
    # 검색할 중고상품 ItemIds
    ItemIds = [
        13267376,       # 주식투자 절대지식, 브렌트 펜폴드, 에디터, 2011
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
    save_csv(df, "aladin_used_book_list.csv")
