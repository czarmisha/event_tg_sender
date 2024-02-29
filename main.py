import time
import datetime as dt

from telegram_sdk import BotHandler


tg_bot = BotHandler()


def process_line(line):
    ticker, value, volume = line.strip().split(';')
    print(f"Processing {ticker}: Value={value}, Volume={volume}")
    try:
        # tg_bot.send_post(f"{ticker}: {value}({volume})")
        tg_bot.send_message(f"{ticker}  {'+' if float(value) >= 0 else '-'}{value}% ({volume})")
    except Exception as e:
        print('Error: ', e)


def process_file():
    processed_tickers = get_processed_tickers()
    file_path = f'event_{dt.datetime.today().strftime("%d_%m_%Y")}.txt'

    with open(file_path, 'r') as file:
        for line in file:
            ticker = line.strip().split(';')[0]
            if ticker not in processed_tickers:
                processed_tickers.add(ticker)
                add_ticker_to_processes(ticker)
                process_line(line)


def get_processed_tickers():
    file_path = f'processed/processed_{dt.datetime.today().strftime("%d_%m_%Y")}.txt'
    with open(file_path, 'r') as file:
        tickers = set(file.read().split(';'))
    return tickers


def add_ticker_to_processes(ticker):
    file_path = f'processed/processed_{dt.datetime.today().strftime("%d_%m_%Y")}.txt'
    with open(file_path, 'a') as file:
        file.write(f'{ticker};')


def main():
    while True:
        process_file()
        time.sleep(1)

if __name__ == '__main__':
    main()