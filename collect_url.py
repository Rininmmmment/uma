import time

from selenium import webdriver
from selenium.webdriver.support.ui import Select,WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def submit_form():
    global year, month
    # 期間を選択
    start_year_element = driver.find_elements(By.NAME, 'start_year')
    start_year_select = Select(start_year_element[0])
    start_year_select.select_by_value(str(year))
    start_mon_element = driver.find_elements(By.NAME, 'start_mon')
    start_mon_select = Select(start_mon_element[0])
    start_mon_select.select_by_value(str(month))
    end_year_element = driver.find_elements(By.NAME, 'end_year')
    end_year_select = Select(end_year_element[0])
    end_year_select.select_by_value(str(year))
    end_mon_element = driver.find_elements(By.NAME, 'end_mon')
    end_mon_select = Select(end_mon_element[0])
    end_mon_select.select_by_value(str(month))

    # 中央競馬場をチェック
    for i in range(1,11):
        # check_Jyo_01〜check_Jyo_10までが中央競馬場
        terms = driver.find_element(By.ID, "check_Jyo_"+ str(i).zfill(2))  
        terms.click()

    # 表示件数を選択(20,50,100の中から最大の100へ)
    list_element = driver.find_element(By.NAME, 'list')
    list_select = Select(list_element)
    list_select.select_by_value("100")

    # フォームを送信
    frm = driver.find_element(By.CSS_SELECTOR, "#db_search_detail_form > form")
    frm.submit()
    time.sleep(5)
    wait.until(EC.presence_of_all_elements_located)


def collect_url():
    global year, month
    with open("html/"+str(year)+"/"+str(year)+"-"+str(month)+".txt", mode='w') as f:
        while True:
            time.sleep(1)
            wait.until(EC.presence_of_all_elements_located)
            all_rows = driver.find_element(By.CLASS_NAME, 'race_table_01').find_elements(By.TAG_NAME, "tr")
            for row in range(1, len(all_rows)):
                race_href=all_rows[row].find_elements(By.TAG_NAME, "td")[4].find_element(By.TAG_NAME, "a").get_attribute("href")
                f.write(race_href+"\n")
            try:
                target = driver.find_elements(By.LINK_TEXT, "次")[0]
                driver.execute_script("arguments[0].click();", target) #javascriptでクリック処理
            except IndexError:
                break


# 準備
options = Options()
options.add_argument('--headless')    # ヘッドレスモードに
driver = webdriver.Chrome(options=options) 
wait = WebDriverWait(driver,10)

URL = "https://db.netkeiba.com/?pid=race_search_detail"
driver.get(URL)
time.sleep(1)
wait.until(EC.presence_of_all_elements_located)  # 全DOMが現れるまで待つ
print("準備完了")

# ここでURL取得
print("取得中...")
year_list = range(2024, 2025)
month_list = range(1, 10)
for year in year_list:
    for month in month_list:
        # フォーム送信
        submit_form()
        print(f"{year}/{month}のフォーム送信完了")

        # 全レース（指定した期間）のレースURLを取得し、txtファイルに書く
        collect_url()
        print(f"{year}/{month}の記録完了")