import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from lxml import etree
import json

def save_to_json(data_list, file_name="output_words_data.json"):
    """
    将数据列表保存为 JSON 文件。

    参数:
    - data_list (list): 要保存的数据列表。
    - file_name (str): 输出的 JSON 文件名称，默认为 "output_words_data.json"。
    """
    try:
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(data_list, f, ensure_ascii=False, indent=4)
        print(f"Data saved to {file_name} successfully.")
    except Exception as e:
        print("An error occurred while saving to JSON:", e)




# 目标 URL
url = "https://www.oxfordlearnersdictionaries.com/wordlists/oxford3000-5000"

# 请求头，模拟浏览器访问
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
    )
}

# 创建会话
session = requests.Session()

# 配置重试机制
retry = Retry(
    total=5,               # 重试次数
    backoff_factor=0.5,    # 失败后等待时间，指数增长
    status_forcelist=[500, 502, 503, 504]  # 针对这些状态码重试
)
adapter = HTTPAdapter(max_retries=retry)
session.mount("http://", adapter)
session.mount("https://", adapter)

content = ''

try:
    # 发送 GET 请求，禁用代理
    response = session.get(url, headers=headers, proxies={"http": None, "https": None})
    response.raise_for_status()  # 检查请求是否成功

    # 打印响应内容
    content = response.text

except requests.exceptions.RequestException as e:
    print("An error occurred:", e)


# 使用 lxml 解析网页
html = etree.HTML(content)

# 查找指定路径的所有 <li> 元素
li_elements = html.xpath("/html/body/div[1]/div[3]/div[2]/div[2]/div/div/div[1]/div[4]/ul/li")


data = {
    "base_url": "https://www.oxfordlearnersdictionaries.com"
}

words = []


# 遍历并打印每个 <li> 元素的属性和子元素
for li in li_elements:

     # 查找 mp3 音频数据
    audio_uk = li.xpath('.//div[@class="sound audio_play_button icon-audio pron-uk"]')[0].attrib
    audio_us = li.xpath('.//div[@class="sound audio_play_button icon-audio pron-us"]')[0].attrib
    row = {
        "word": li.attrib.get('data-hw'),
        "level_ox3000": li.attrib.get('data-ox3000'),
        "level_ox5000": li.attrib.get('data-ox5000'),
        "audio_uk_mp3": audio_uk.get('data-src-mp3'),
        "audio_uk_ogg": audio_uk.get('data-src-ogg'),
        "audio_us_mp3": audio_uk.get('data-src-mp3'),
        "audio_us_ogg": audio_uk.get('data-src-ogg')
    }
    words.append(row)
data['words'] = words

print("out_words_len", len(words))

save_to_json(data)
