import csv
import requests, json
import re

date = 1
time = 2
addr = 3

def split_data_into_date(split_year):
    ### 초기 데이터셋 (illegal_park_info.csv) 년도별로 파일 나눠서 저장.

    with open('./illegal_park_info.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)

        csv_file = open(split_year+'.csv', 'w', newline='', encoding='utf-8-sig')
        writer = csv.writer(csv_file)

        for row in reader:
            # print(row)
            year = row[1][:4]
            if year == split_year:
                writer.writerow(row)

def get_geocode(address):
    ### 네이버 API로 주소 -> 좌표 리턴


    url = "https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode?"
    client_id = "1g2av434tn"
    client_secret = "N4S7F8ie2frva4wOBNnsFmHfvlxZrhUeDQTHN0TX"
    query = "query=" + address
    header = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret
    }

    r = requests.get(url + query, headers=header)
    result = r.json()
    # print(result)

    if r.status_code == 200:
        if result['meta']['totalCount'] != 0:
            long, lat = result['addresses'][0]['x'], result['addresses'][0]['y']
            return long, lat
        else:
            return None
    else:
        # print("Error :", r.status_code)
        return False
    
def remove_overlap(file_name):
    ### 데이터셋에 중복되는 주소들 제거 후 주소만 txt로 저장
    addresses = {}

    with open(file_name+'.csv', 'r', encoding='UTF8') as cf:
        
        ill_park = csv.reader(cf)

        for row in ill_park:
            if not row[3] in addresses:
                addresses[row[3]] = 1
                # print(row[3])
        
        cf.close()

    with open(file_name+'.txt', 'w', encoding='UTF-8') as f:

        for key in addresses.keys():
            
            key = normalization(key)

            f.write(key + '\n')
        
        f.close

def normalization(address):
    ### 검색 안되는 주소 전처리 ###

    # 앞뒤 공백 지우기
    address = address.strip()

    # 첫 단어가 "북구"라면 제거
    if address[:2] == "북구":
        address = address[3:]
    
    address = "대구 북구 " + address

    # 끝 단어 이상한거 제거
    if address[-1] == "부" or address[-1] == "소" or address[-1] == "장":
        address = address[:-1]

    # 검색에 방해되는 단어 지우기
    ban_words = ["부근", "건너", "사거리", "횡단보도", "횡단번호", "모퉁이", "소화전", "육교밑", "버스정류", "버스정류장", "어린이보호구역", "인도"]

    for word in ban_words:
        address = re.sub(word, '', address)

    # 괄호와 포함된 단어 지우기
    address = re.sub(r'\([^)]*\)', '', address)
    address = address.strip()

    '''
    splited_addr = address.split(" ")
    if len(splited_addr)>1:
        if splited_addr[1].endswith("로"):
            del splited_addr[0]
            address = " ".join(splited_addr)
    '''

    #return "대구 북구 " + address

    address = gil_to_doro(address)

    return address

# normalization("복현동 대학로 142")
def gil_to_doro(addr):
    ### 동과 도로명 주소가 같이 있다면 제거함
    
    temp = addr.split(' ')
    
    if len(temp) < 4:
        return addr

    if temp[2][-1] == "동" or temp[2][-1] == "가":
        if temp[3][-1] == "로" or temp[3][-1] == "길":
            del temp[3]

    print(temp)
    return " ".join(temp)


def refactoring_file(file_name):
    ### 데이터셋 전처리 작업 후 저장

    f = open(file_name+'.csv', 'r', encoding='utf-8')
    new_f = open(file_name+'_refacted.csv', 'w', newline='', encoding='utf-8-sig')

    writer = csv.writer(new_f)
    reader = csv.reader(f)

    lists = []

    for row in reader:
        row[addr] = normalization(row[addr])
        lists.append(row)
    
    writer.writerows(lists)
        
def check_ok(file_name):
    ### 검색 안 되는 주소 리스트 뽑기 ###

    f = open(file_name+'.txt', 'r', encoding='utf-8-sig')
    result = open(file_name+'_checked.csv', 'w', newline='', encoding='utf-8-sig')

    writer = csv.writer(result)

    ok_lists = []
    no_lists = []

    cnt = 0

    for row in f.readlines():
        row = row.strip()
        response = get_geocode(row)

        if response != False:
            if response != None:
                ok_lists.append(['ok', row])
            else:
                no_lists.append(['no', row])
        else:
            no_lists.append(row)

        print(cnt, end='\r')
        cnt += 1

    writer.writerows(no_lists)
    


if "__main__":

    remove_overlap('2021')
    # remove_overlap('illegal_park_info')
   # check_ok('2021')

    pass
