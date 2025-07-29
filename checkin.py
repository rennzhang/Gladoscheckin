import requests
import json
import os

# -------------------------------------------------------------------------------------------
# github workflows - 飞书机器人推送版本
# -------------------------------------------------------------------------------------------
def send_feishu_message(webhook_token, title, content):
    """发送消息到飞书机器人"""
    if not webhook_token:
        print("未设置飞书机器人 webhook token")
        return 0
        
    webhook_url = f"https://open.feishu.cn/open-apis/bot/v2/hook/{webhook_token}"
    
    # 组合完整消息
    full_message = f"{title}\n{content}"
    
    payload = {
        "msg_type": "text",
        "content": {
            "text": full_message
        }
    }
    
    try:
        response = requests.post(
            webhook_url,
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload, ensure_ascii=False).encode('utf-8')
        )
        print(f"飞书推送状态码: {response.status_code}")
        return response.status_code
    except Exception as e:
        print(f"飞书推送异常: {str(e)}")
        return 0

if __name__ == '__main__':
    # 飞书机器人webhook token 申请地址 https://open.feishu.cn/
    feishu_token = os.environ.get("FEISHU_WEBHOOK_TOKEN", "")
    if feishu_token == "":
        print('未获取到飞书 token 变量')
        exit(0)
    
    # 推送内容
    success, fail = 0, 0        # 成功账号数量 失败账号数量
    sendContent = ""

    # glados账号cookie 直接使用数组 如果使用环境变量需要字符串分割一下
    cookies = os.environ.get("COOKIES", "").split("&")
    if cookies[0] == "":
        print('未获取到COOKIE变量')
        cookies = []
        exit(0)

    url = "https://glados.rocks/api/user/checkin"
    url2 = "https://glados.rocks/api/user/status"

    referer = 'https://glados.rocks/console/checkin'
    origin = "https://glados.rocks"
    useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
    payload = {
        'token': 'glados.one'
    }

    for cookie in cookies:
        checkin = requests.post(url, headers={'cookie': cookie, 'referer': referer, 'origin': origin,
                                'user-agent': useragent, 'content-type': 'application/json;charset=UTF-8'}, data=json.dumps(payload))
        state = requests.get(url2, headers={
                             'cookie': cookie, 'referer': referer, 'origin': origin, 'user-agent': useragent})
    # --------------------------------------------------------------------------------------------------------#
        if checkin.status_code == 200:
            # 解析返回的json数据
            checkin_result = checkin.json()
            # 获取签到结果
            status = checkin_result.get('message', '')
            
            # 获取账号当前状态
            state_result = state.json()
            print(state_result)
            
            # 获取剩余时间
            leftdays = int(float(state_result['data']['leftDays']))
            # 获取账号email
            email = state_result['data']['email']
            
            # 解析签到详情
            points_earned = "0"
            current_balance = "0"
            
            if checkin_result.get('list') and len(checkin_result['list']) > 0:
                latest_record = checkin_result['list'][0]
                points_earned = latest_record.get('change', '0')
                current_balance = latest_record.get('balance', '0')
                # 格式化积分显示
                points_earned = f"{float(points_earned):.0f}"
                current_balance = f"{float(current_balance):.0f}"

            if "Checkin" in status:
                success += 1
                message_status = "✅ 签到成功"
                status_emoji = "🎉"
            elif "Tomorrow" in status or "Repeats" in status:
                message_status = "⏰ 今日已签到"
                status_emoji = "✨"
            else:
                fail += 1
                message_status = "❌ 签到失败"
                status_emoji = "⚠️"

            if leftdays is not None:
                message_days = f"{leftdays} 天"
            else:
                message_days = "无法获取剩余天数信息"
        else:
            email = ""
            message_status = "❌ 签到请求失败"
            message_days = "获取信息失败"
            points_earned = "0"
            current_balance = "0"
            status_emoji = "⚠️"
            fail += 1

        # 推送内容 - 美化格式
        sendContent += f"""
{status_emoji} 账号信息
📧 邮箱: {email}
🎯 状态: {message_status}
💰 本次获得: +{points_earned} 积分
💎 当前余额: {current_balance} 积分
⏳ 剩余天数: {message_days}
"""
        
     # --------------------------------------------------------------------------------------------------------#
    print("sendContent:" + "\n", sendContent)
    if feishu_token != "":
        # 根据签到结果设置标题
        if fail == 0:
            title = "**✅ Glados 签到成功**\n\n"
        else:
            title = "**❌ Glados 签到失败**\n\n"
        
        send_feishu_message(feishu_token, title, sendContent)
