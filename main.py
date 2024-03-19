import os
import time
import datetime as dt

from telegram_sdk import BotHandler
from config import config


tg_bot = BotHandler()


def process_line(line):
    _, ticker, value, volume = line.strip().split(';')
    print(f"Processing {ticker}: Value={value}, Volume={volume}")
    try:
        volume_in_mlns = round(int(volume) / 1000000, 2)
        # tg_bot.send_post(f"{ticker}: {value}({volume})")
        tg_bot.send_message(f"{ticker}  {'+' if float(value) >= 0 else '-'}{'{:.2f}'.format(float(value))}% ({volume_in_mlns} mln.)")
    except Exception as e:
        print('Error: ', e)


def process_file():
    processed_tickers = get_processed_tickers()
    # print(f'Processed tickers: {processed_tickers}')
    file_path = f'events/event_{dt.datetime.today().strftime("%d_%m_%Y")}.txt'

    with open(file_path, 'r') as file:
        for line in file:
            line_list = line.strip().split(';')
            if len(line_list) == 4:
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


def clear_processed():
    print('clearing processed file...')
    file_path = f'processed/processed_{dt.datetime.today().strftime("%d_%m_%Y")}.txt'
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    if os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.write('')


def main(start_time=dt.datetime.now()):
    last_clear_time = start_time
    while True:
        if last_clear_time < dt.datetime.now() - dt.timedelta(minutes=config.CLEAR_INTERVAL):
            clear_processed()
            last_clear_time = dt.datetime.now()

        process_file()
        time.sleep(1)

if __name__ == '__main__':
    main()