import os
import time
import datetime as dt
import yfinance as yf
import pytz

from telegram_sdk import BotHandler
from config import config


tg_bot = BotHandler()
utc = pytz.utc
STOCK_DATA = {}


def get_tickers():
    tickers = []
    with open('tickers.txt', 'r') as file:
        tickers = [ticker.strip() for ticker in set(file.read().split('\n'))]

    return tickers


def update_stock_data():
    if dt.datetime.now(utc).hour >= 6:
        return
    
    tickers = get_tickers()
    if not tickers:
        print('No tickers were found to update stock data')
        return
    stock_data = {}
    tickers = yf.Tickers(' '.join(tickers))

    for ticker in tickers.tickers:
        info = tickers.tickers[ticker].info
        if info.get('marketCap'):
            stock_data[ticker] = info.get('marketCap')

        else:
            print('No market cap for ' + ticker)

    global STOCK_DATA
    STOCK_DATA = stock_data


def process_line(line):
    _, ticker, value, volume, adv, average_volume, avg_volume_percent_adv, __ = line.strip().split(';')
    print(f"Processing {ticker}: Value={value}, Volume={volume}")
    try:
        mcap = STOCK_DATA.get(ticker)
        mcap = round(int(mcap) / 1000000, 2) if mcap else '-'
        volume_in_mlns = round(int(volume) / 1000000, 2)
        adv_in_mlns = round(int(adv) / 1000000, 2)
        average_volume_in_mlns = round(int(average_volume) / 1000000, 2)
        tg_bot.send_message(
            f"{ticker}  {'+' if float(value) >= 0 else '-'}{'{:.2f}'.format(float(value))}% "
            f"({mcap} m / {volume_in_mlns} m / {adv_in_mlns}m / {average_volume_in_mlns}m / {'{:.2f}'.format(float(avg_volume_percent_adv))}%)"
        )
    except Exception as e:
        print('Error: ', e)


def process_file():
    processed_tickers = get_processed_tickers()
    file_path = f'events/event_{dt.datetime.today().strftime("%d_%m_%Y")}.txt'

    with open(file_path, 'r') as file:
        for line in file:
            line_list = line.strip().split(';')
            if len(line_list) == 8:
                ticker = line_list[1]
                if ticker not in processed_tickers:
                    processed_tickers.add(ticker)
                    add_ticker_to_processes(ticker)
                    process_line(line)
            else:
                print(f"error in line {line}")


def get_processed_tickers():
    file_path = f'processed/processed_{dt.datetime.today().strftime("%d_%m_%Y")}.txt'
    try:
        with open(file_path, 'r') as file:
            tickers = set(file.read().split(';'))
    except FileNotFoundError:
        tickers = set()
    
    return tickers


def add_ticker_to_processes(ticker):
    file_path = f'processed/processed_{dt.datetime.today().strftime("%d_%m_%Y")}.txt'
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'a') as file:
        file.write(f'{ticker};')


def clear_file(file_path: str):
    print('clearing file...', file_path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    if os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.write('')


def main(start_time=dt.datetime.now()):
    update_stock_data()
    last_clear_time = start_time
    while True:
        if last_clear_time < dt.datetime.now() - dt.timedelta(minutes=config.CLEAR_INTERVAL):
            clear_file(f'processed/processed_{dt.datetime.today().strftime("%d_%m_%Y")}.txt')
            clear_file(f'events/event_{dt.datetime.today().strftime("%d_%m_%Y")}.txt')
            last_clear_time = dt.datetime.now()

        process_file()
        time.sleep(1)

if __name__ == '__main__':
    main()