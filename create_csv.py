import os
import csv
import requests
import time
from bs4 import BeautifulSoup

# HTMLデータからレース情報を抽出する関数
def get_race_data(html, race_id):
    soup = BeautifulSoup(html, 'html.parser')

    # レース情報（5 R 3歳未勝利 / 2019年1月27日）
    date_element = soup.find('p', class_='smalltxt').text.split(' ')[0]
    dl_element = soup.find('dl', class_='racedata')
    race_num = dl_element.find('dt').text.replace('\n','')
    race_name = dl_element.find('h1').text.split(' ')[0]

    # レースの詳細情報（芝左1600m / 天候 : 晴 / 芝 : 良 / 発走 : 12:30）
    description = dl_element.select_one('diary_snap_cut > span').text.split("/")
    ground = description[0].replace('\xa0','')[0]
    direction = description[0].replace('\xa0','')[1]
    distance = description[0].replace('\xa0','')[2:].replace('m', '')
    
    if ground == 'ダ':
        return []

    weather = description[1].replace('\xa0','').split(' : ')[1]
    condition = description[2].replace('\xa0','').split(' : ')[1]

    return [race_id, date_element, race_num, race_name, ground, direction, distance, weather, condition]

# HTMLデータから馬情報を抽出する関数
def get_hource_data(html, race_id):
    soup = BeautifulSoup(html, 'html.parser')

    table = soup.find('table', class_='race_table_01')
    rows = table.find_all('tr')
    hource_data = []
    for row in rows[1:]:
        cells = row.find_all('td')
        data_row = [cell.text.strip() for cell in cells]

        # データの整形
        del data_row[9]  # ﾀｲﾑ指数を削除（課金コンテンツのため）
        del data_row[14:17]  # 調教ﾀｲﾑ, 厩舎ｺﾒﾝﾄ, 備考を削除（課金コンテンツのため）
        del data_row[16]  # 賞金を削除
        data_row[14] = data_row[14].replace('\n','')

        hource_data.append([race_id] + data_row)

    return hource_data

# year_listディレクトリ内の全ファイルに対して処理を行う
year_list = list(range(2024, 2025))
for year in year_list:
    html_dir = "html"+"/"+str(year)

    if os.path.isdir(html_dir):
        file_list = os.listdir(html_dir)
        
        for file_name in file_list:

            # 各ファイルについて処理
            with open(html_dir+"/"+file_name, "r") as f:
                url_list = f.read().split("\n")  # 各レースのURL

                # 1レースごとにデータ取得
                for url in url_list:
                    try:
                        # htmlの準備
                        response = requests.get(url)
                        response.encoding = 'euc_jp'
                        html = response.text

                        # レース・馬情報を取得
                        race_id = url.split("/")[-2]
                        race_data = get_race_data(html, race_id)

                        # ダートなら飛ばす
                        if len(race_data) == 0:
                            print('ダートなので飛ばしました')
                            continue

                        hource_data = get_hource_data(html, race_id)

                        # レース情報をcsvに記録する
                        with open('race_data-'+str(year)+'.csv', 'a', newline='') as file:
                            writer = csv.writer(file)
                            writer.writerow(race_data)
                        
                        # 馬の情報をcsvに記録する
                        with open('hource_data-'+str(year)+'.csv', 'a', newline='') as file:
                            writer = csv.writer(file)
                            for data in hource_data:
                                writer.writerow(data)
                        
                        print(f"{url}を記録しました")

                    except:
                        with open("error.txt", mode='a') as f:
                            f.write(url + "\n")
                            print(f'{url}はエラーでした')

                    time.sleep(2)