import os
import json

from openai import OpenAI
import pyupbit
from dotenv import load_dotenv

load_dotenv()
def ai_trading():
	# 기능 1. 30일치의 KRW-BTC 업비트 차트 데이터 가져오기
	df = pyupbit.get_ohlcv("KRW-BTC", interval="day", count=30)

	# 기능 2. OpenAI에게 데이터 제공하고 투자 판단 받기
	client = OpenAI()

	response = client.responses.create(
		model="gpt-4.1",
		input=[
			{
				"role": "system",
				"content": [
					{
						"type": "input_text",
						"text": "You are a Bitcoin investment expert. Based on the provided chart data, please analyze the current situation and respond strictly in JSON format as shown below.\n\nRespond in one of the following formats:\n{ \"decision\": \"buy\", \"reason\": \"your reasoning here\" }\n{ \"decision\": \"sell\", \"reason\": \"your reasoning here\" }\n{ \"decision\": \"hold\", \"reason\": \"your reasoning here\" }\n\nMake sure to use the exact JSON structure with the keys \"decision\" and \"reason\"."
					}
				]
			},
			{
				"role": "user",
				"content": [
					{
						"type": "input_text",
						"text": df.to_json()
					}
				]
			},
		],
		text={
			"format": {
				"type": "json_object"
			}
		},
	)

	# 기능 3. 투자 판단에 따라 업비트 거래
	access = os.getenv("UPBIT_ACCESS_KEY")
	secret = os.getenv("UPBIT_SECRET_KEY")
	upbit = pyupbit.Upbit(access, secret)

	result = json.loads(response.output_text)

	print('### AI Decision', result['decision'].upper(), '###')
	print('### Reason', result['reason'], '###')

	if result["decision"] == "buy":
		# 매수

		# 원화 거래 수수로율과 최소 매도 금액을 고려한 비즈니스 로직
		KRW_FEE = 0.05
		MINIMUM_BUY_AMOUNT = 5000
		my_krw_balance = upbit.get_balance("KRW")

		if my_krw_balance * (1 - KRW_FEE) > MINIMUM_BUY_AMOUNT:
			print("### Buy Order Executed ###")
			print(upbit.buy_market_order("KRW-BTC", my_krw_balance * (1 - KRW_FEE)))
		else:
			print("### Buy Order Failed: Insufficient KRW Balance (less than 5,000₩) ###")
	
	elif result["decision"] == "sell":
		# 매도
		MINIMUM_SELL_AMOUNT = 5000
		my_btc_balance = upbit.get_balance("KRW-BTC")
		btc_current_price = pyupbit.get_orderbook(ticker="KRW-BTC")["orderbook_units"][0]["ask_price"]

		if my_btc_balance * btc_current_price > MINIMUM_SELL_AMOUNT:
			print("### Sell Order Executed ###")
			print(upbit.sell_market_order("KRW-BTC", my_btc_balance))
		else:
			print("### Sell Order Failed: Insufficient BTC Balance (less than 5,000₩) ###")
	elif result["decision"] == "hold":
		print("### Hold Order ###")

if __name__ == "__main__":
	import time

	while True:
		ai_trading()
		time.sleep(10)
