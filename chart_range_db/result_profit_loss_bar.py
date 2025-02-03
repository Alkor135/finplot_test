import sqlite3
from pathlib import Path
import numpy as np

import pandas as pd


def determine_trade_results(df):
    """ Векторизированная функция для определения результата сделки """
    results = np.full(len(df), None)  # Инициализация массива результатов
    size_plus_20 = df['size'].values + 20

    open_prices = df['open'].values
    close_prices = df['close'].values
    high_prices = df['high'].values
    low_prices = df['low'].values

    # Предварительные вычисления для оптимизации (кумулятивные максимумы/минимумы)
    high_cummax = np.maximum.accumulate(high_prices)
    low_cummin = np.minimum.accumulate(low_prices)

    # Определение направлений сделок
    long_signals = close_prices[:-1] > open_prices[:-1]  # Сигнал на покупку
    short_signals = close_prices[:-1] < open_prices[:-1]  # Сигнал на продажу

    # Проверка для сделок на покупку (Long)
    long_indices = np.where(long_signals)[0]
    for idx in long_indices:
        entry_price = open_prices[idx + 1]
        tp_price = entry_price + size_plus_20[idx + 1]
        sl_price = entry_price - size_plus_20[idx + 1]

        # Проверка TP и SL на последующих барах
        tp_hit = np.where(high_cummax[idx + 1:] >= tp_price)[0]
        sl_hit = np.where(low_cummin[idx + 1:] <= sl_price)[0]

        if tp_hit.size > 0 and (sl_hit.size == 0 or tp_hit[0] < sl_hit[0]):
            results[idx + 1] = 'profit'
        elif sl_hit.size > 0:
            results[idx + 1] = 'loss'

    # Проверка для сделок на продажу (Short)
    short_indices = np.where(short_signals)[0]
    for idx in short_indices:
        entry_price = open_prices[idx + 1]
        tp_price = entry_price - size_plus_20[idx + 1]
        sl_price = entry_price + size_plus_20[idx + 1]

        tp_hit = np.where(low_cummin[idx + 1:] <= tp_price)[0]
        sl_hit = np.where(high_cummax[idx + 1:] >= sl_price)[0]

        if tp_hit.size > 0 and (sl_hit.size == 0 or tp_hit[0] < sl_hit[0]):
            results[idx + 1] = 'profit'
        elif sl_hit.size > 0:
            results[idx + 1] = 'loss'

    return results


if __name__ == '__main__':
    # Укажите путь к вашей базе данных SQLite
    db_path = Path(r'C:\Users\Alkor\gd\data_quote_db\RTS_Range.db')

    # Установите соединение с базой данных
    conn = sqlite3.connect(db_path)

    query = "SELECT name FROM sqlite_master WHERE type='table'"
    table = pd.read_sql_query(query, conn).iloc[0, 0]
    # print(table)

    # Выполните SQL-запрос и загрузите результаты в DataFrame
    query = f"SELECT * FROM {table}"
    df = pd.read_sql_query(query, conn)

    # Закройте соединение
    conn.close()

    # Фильтрация df
    # Регулярное выражение с незахватывающей группой (?:)
    pattern = r'(?:10:00:00|10:00:01|19:00:00|19:00:01|19:05:00|19:05:01)'
    # Фильтрация строк (удаляем строки с совпадением)
    df = df[~df['datetime'].str.contains(pattern, regex=True)]
    # Сброс индекса (переиндексация)
    df = df.reset_index(drop=True)

    # Добавление новой колонки с результатом сделки
    df['trade_result'] = determine_trade_results(df)

    # Проверьте данные
    print(df)

    # Сохранение в файл
    df.to_csv("result.csv", index=False)
