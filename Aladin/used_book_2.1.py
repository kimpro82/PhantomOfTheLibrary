"""
알라딘(Aladin) 중고상품 크롤링
2023.12.28 (Updated 2026.08.18)

이 스크립트는 알라딘 웹사이트에서 중고 도서 상품 정보를 수집하고,
그 결과를 CSV 파일로 저장하는 목적으로 작성되었습니다.

Usage:
    python3 used_book_2.py <yaml_file_path>
    예시: python3 used_book_2.py 20260818.yaml
"""

import argparse
import datetime
import os
import re
import sys
import pytz
import requests
from bs4 import BeautifulSoup
import pandas as pd
import yaml


def load_item_ids(yaml_path: str) -> list:
    """
    YAML 파일에서 ItemId 목록을 불러오는 함수입니다.
    주석이 포함된 YAML 파일에서 리스트 또는 딕셔너리 형태의 ItemId를 읽어옵니다.

    Args:
        yaml_path (str): YAML 파일 경로

    Returns:
        list: 검색할 ItemId 리스트
    """
    if not os.path.exists(yaml_path):
        print(f"오류: 설정 파일 '{yaml_path}'을(를) 찾을 수 없습니다.", file=sys.stderr)
        sys.exit(1)

    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        print(f"오류: YAML 파일 파싱 중 문제가 발생했습니다: {e}", file=sys.stderr)
        sys.exit(1)

    if data is None:
        print(f"오류: '{yaml_path}' 파일이 비어 있습니다.", file=sys.stderr)
        sys.exit(1)

    # 1. 리스트 형식인 경우 (예: - 13267376)
    if isinstance(data, list):
        item_ids = data
    # 2. 딕셔너리 형식인 경우 (예: item_ids: [...])
    elif isinstance(data, dict):
        for key in ["item_ids", "ItemIds", "items", "ItemId", "item_id"]:
            if key in data and isinstance(data[key], list):
                item_ids = data[key]
                break
        else:
            # 리스트 값을 가진 첫 번째 키 탐색
            list_values = [v for v in data.values() if isinstance(v, list)]
            if list_values:
                item_ids = list_values[0]
            else:
                print(f"오류: '{yaml_path}'에서 ItemId 목록(리스트)을 찾을 수 없습니다.", file=sys.stderr)
                sys.exit(1)
    else:
        print(f"오류: 올바른 YAML 리스트 또는 딕셔너리 형식이 아닙니다.", file=sys.stderr)
        sys.exit(1)

    # None이나 빈 항목 제외하고 리스트 정제
    cleaned_item_ids = [item for item in item_ids if item is not None]
    if not cleaned_item_ids:
        print(f"오류: ItemId 목록이 비어 있습니다.", file=sys.stderr)
        sys.exit(1)

    return cleaned_item_ids


# 알라딘 중고상품 전체 검색
def search_used_item_all(_ItemIds: list) -> list:
    """
    요청한 도서의 알라딘 중고상품 전체를 검색하여 정보를 수집하는 함수입니다.

    Args:
        _ItemIds (list): 검색할 중고상품 ItemIds

    Returns:
        list: 중고상품 정보 리스트
    """

    # URL 설정
    _url = "https://www.aladin.co.kr/shop/UsedShop/wuseditemall.aspx?"
    _params = {}

    _book_data = []

    for _ItemId in _ItemIds:
        print(f"검색 진행 중: ItemId={_ItemId}")
        # response 수신
        _params['ItemId'] = _ItemId
        try:
            _response = requests.get(_url, params=_params, timeout=5)
            _soup = BeautifulSoup(_response.text, "html.parser")

            # 마지막 페이지 번호 가져오기
            _nright = _soup.find("div", class_="nright_text")
            if _nright:
                _digits = re.sub(r"[^0-9]", "", _nright.text)
                _last_page_num = int(_digits) if _digits else 1
            else:
                _last_page_num = 1

            # 모든 페이지에서 상품 정보 가져오기
            for _page_num in range(1, _last_page_num + 1):
                try:
                    # 상품 정보 가져오기
                    _params['page'] = _page_num
                    _response = requests.get(_url, params=_params, timeout=5)
                    _soup = BeautifulSoup(_response.text, "html.parser")
                    _table_div = _soup.find("div", class_="Ere_usedsell_table")
                    if not _table_div:
                        continue
                    _books_table = _table_div.find_all("tr")

                    # 상품 정보 저장
                    for _one_book_row in _books_table[1:]:
                        _one_book_cols = _one_book_row.find_all("td")
                        if len(_one_book_cols) < 5:
                            continue

                        # 상품 정보 추출 : 상품명, 등급, 판매가, 할인률, 배송비, 판매자, 판매등급
                        _title_li = _one_book_cols[1].find_all("li")
                        _title = _title_li[0].text.split(",")[0].replace(" ", "") if _title_li else ""
                        _grade = _one_book_cols[2].text.replace('\n', "")

                        _price_li = _one_book_cols[3].find_all("li")
                        _price = re.sub(r"[^0-9]", "", _price_li[0].text) if len(_price_li) > 0 else ""
                        _discount = re.sub(r"[^0-9%]", "", _price_li[1].text) if len(_price_li) > 1 else ""
                        _delivery = re.sub(r"[^0-9]", "", _price_li[2].text) if len(_price_li) > 2 else ""

                        _seller_li = _one_book_cols[4].find_all("li")
                        _seller_raw = _seller_li[0].text if _seller_li else ""

                        if _seller_raw == " 알라딘 직접 배송 ":
                            _seller = "알라딘"
                            _seller_grade = " "
                        elif _seller_raw == " 이 광활한 우주점 ":
                            _sub_seller = _seller_li[1].text.replace(" ", "") if len(_seller_li) > 1 else ""
                            _seller = "우주점 " + _sub_seller
                            _seller_grade = " "
                        else:
                            _seller = _seller_raw.strip()
                            _seller_grade = _seller_li[1].text.replace(" ", "") if len(_seller_li) > 1 else " "

                        _one_book_data = [_title, _grade, _price, _discount, _delivery, _seller, _seller_grade]
                        _book_data.append(_one_book_data)

                except Exception as e:
                    print(f"페이지({_page_num}) 검색 결과를 가져오지 못 했습니다:", e)

        except Exception as e:
            print(f"ItemId({_ItemId}) 검색 요청 중 오류 발생:", e)

    return _book_data


def save_csv(_data_frame, _filename="aladin_used_book_list"):
    """
    데이터프레임을 CSV 파일로 저장하는 함수입니다.

    Args:
        _data_frame (DataFrame): 저장할 데이터프레임
        _filename (str): 저장할 파일명 (기본값: aladin_used_book_list)
    """
    os.makedirs("Data", exist_ok=True)
    _seoul_timezone = pytz.timezone('Asia/Seoul')
    _time_stamp = datetime.datetime.now(_seoul_timezone).strftime("%Y%m%d_%H%M%S")
    _path = f"Data/{_filename}_{_time_stamp}.csv"
    _data_frame.to_csv(_path, index=False, encoding='utf-8-sig')
    print("파일 저장을 완료하였습니다. :", _path)


def main():
    parser = argparse.ArgumentParser(
        description="알라딘 중고상품 크롤링 프로그램",
        epilog="예시: python3 used_book_2.py 20260818.yaml"
    )
    parser.add_argument(
        "yaml_file",
        help="검색할 ItemId 목록이 저장된 YAML 파일 경로 (예: 20260818.yaml)"
    )
    args = parser.parse_args()

    # YAML 파일에서 ItemId 로드
    item_ids = load_item_ids(args.yaml_file)
    print(f"불러온 ItemId 목록 ({len(item_ids)}개): {item_ids}")

    # 크롤링 수행
    result = search_used_item_all(item_ids)

    columns = ['상품명', '등급', '판매가', '할인률', '배송비', '판매자', '판매등급']
    df = pd.DataFrame(data=result, columns=columns)
    print("\n[수집 결과 미리보기]")
    print(df)

    save_csv(df, "aladin_used_book_list")


if __name__ == "__main__":
    main()
