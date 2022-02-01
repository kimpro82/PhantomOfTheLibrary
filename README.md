# Phantom Of The Library

## Phantom Of The Library란?

도서관 대출 이력 데이터에 도서 분류 체계 정보를 추가하여 아래와 같은 집계 표를 얻기 위한 코드입니다.

![도서관 대출 이력 집계(예시)](image/도서관%20대출이력%20집계_2017-2019.png)


## 개요 Outline

| 구분 | 개요 | 상세내용 |
|:-:|:-:|:--|
| **As-Is** | **엑셀 수기 작업** | ① 도서관 사이트에서 대출내역 엑셀 파일 다운로드 |
|   |   | **② 포털/서점 사이트 등 도서분류 체계를 참고하여 수기 분류** |
|   |   | ③ 엑셀 Pivot Table 작성 |
| **To-Be** | **자동화** | ① 상동 (추후 자동화 포함) |
|   |   | **② 도서분류 체계 웹 크롤링으로 삽입** |
|   |   | ③ 상동 (추후 자동화 포함) |


## 사전검토사항 Pre-review

- 도서분류 체계 퀄리티는 수기 작업시 더 높음 (복수 카테고리 존재시 주관적 판단 개입)  
  → 자동화에 따른 작성 편의성 증대의 반대 급부로 퀄리티 하향은 감수
- 크롤링 대상 사이트(잠정) : [Naver](https://www.naver.com)  
  · 도서관 사이트 : 정확한 ISBN 코드를 얻을 수 있으나, 책 제목 검색에 비해 특별히 더 효율적이진 않음  
  · 대형서점 사이트 : Bot 접근 이슈 및 단일 사이트 크롤링시 검색 실패 가능성 존재  
  · Naver : 책 제목으로 검색시 일부 불일치하더라도 Robust한 검색 결과를 얻을 수 있음
- 유사한 제목의 책 여러 권이 검색되더라도, 같은 카테고리의 도서일 가능성이 높음  
  → 정확하게 일치하는 책을 가려내지 않아도 됨 (난이도 하락 요인)


## 개발 진행 상황 Development Progress

- [네이버 도서분류 체계 크롤링 (2022.01.16)](/src/PhantLib#네이버-도서분류-체계-크롤링-20220116)  
&nbsp;- [특수문자 포함한 책 제목 검색시 오류 해결 (2022.01.31)](/src/PhantLib#--특수문자-포함한-책-제목-검색시-오류-해결-20220131)


## 개발 예정 사항 To-do

- 기존 엑셀 파일이 아닌 신규 파일 생성 : 잘못된 덮어쓰기로 인한 데이터 손실 예방
- 자동 피벗 테이블 생성
- 복수 분류 체계 중 콤보박스로 선택 가능하도록 구현