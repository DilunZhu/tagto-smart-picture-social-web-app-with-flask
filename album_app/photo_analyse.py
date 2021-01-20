import requests
import json


def photo_tag(image_url):
    """图像分类 API"""
    endpoint = "Your endpoint"  # 自行填写
    subscription_key = "Your subscription key"  # 自行填写
    # base url
    analyze_url = endpoint + "vision/v3.1/analyze"
    headers = {'Ocp-Apim-Subscription-Key': subscription_key}
    # 参数
    params = {'visualFeatures': 'Categories,Description,Color'}
    # 请求主体body
    data = {'url': image_url}  # 将image_url设置为想要分析的图像的URL
    response = requests.post(analyze_url, headers=headers, params=params, json=data)
    response.raise_for_status()
    analysis = response.json()
    detail = json.dumps(analysis)
    tag = json.loads(detail)['categories'][0]['name']  # 取首个标签值
    return tag
