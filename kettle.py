import logging
import sqlite3
import time

import settings


sqlite_conn: sqlite3.Connection
sqlite_cursor: sqlite3.Cursor


def sqlite_message(message: str):
    sqlite_cursor.execute('INSERT INTO logs(message) VALUES (?);', [message])
    sqlite_conn.commit()


class Kettle:
    max_water_level = settings.max_water_level
    t_water = settings.t_water_beginning
    t_water_stop = settings.t_water_stop if settings.t_water_stop <= 100 else 100
    boil_time = int(settings.boil_time)

    def start(self):
        """Запуск чайника с автоматическим выключением.

        Нагрев воды от t_water до t_water_stop за boil_time сек."""
        print(f'\nЧайник включён.\nДля выключения нажмите ctrl+c.\n\n'
              f'Температура воды:\n{self.t_water:.0f}°C')
        logging.info('Kettle is turned on')
        logging.info(f't water: {self.t_water:.0f}°C')
        sqlite_message('Kettle is turned on')
        sqlite_message(f't water: {self.t_water:.0f}°C')
        t_step = (self.t_water_stop - self.t_water) / self.boil_time
        is_kettle_boiled = False
        for x in range(self.boil_time):
            time.sleep(1)
            self.t_water += t_step
            print(f'{self.t_water:.0f}°C')
            logging.info(f't water: {self.t_water:.0f}°C')
            sqlite_message(f't water: {self.t_water:.0f}°C')
            if not is_kettle_boiled and round(self.t_water) >= 100:
                is_kettle_boiled = True
                print('Чайник вскипел.')
                logging.info('Kettle is boiled')
                sqlite_message('Kettle is boiled')
        self.stop()

    def stop(self):
        """Остановка и выключение чайника."""
        print('\nЧайник остановлен.')
        logging.info('Kettle is stopped')
        sqlite_message('Kettle is stopped')
        print('\nЧайник выключен.')
        logging.info('Kettle is turned off')
        sqlite_message('Kettle is turned off')

    def pour_water(self, water_level: float):
        """Налитие воды в чайник."""
        self.water_level = water_level


if __name__ == '__main__':
    logging.basicConfig(
        filename='logs.txt',
        format='[%(asctime)s][%(levelname)s] %(message)s',
        datefmt='%d.%m.%y %H:%M:%S',
        level=logging.DEBUG
    )
    sqlite_conn = sqlite3.connect('orders.db')
    sqlite_cursor = sqlite_conn.cursor()
    sqlite_cursor.execute(
        'CREATE TABLE IF NOT EXISTS logs ('
        'id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,'
        'message VARCHAR(64),'
        'datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL );'
    )
    sqlite_conn.commit()

    kettle = Kettle()
    print(f'Программа Чайник.\n\nСколько наливаете воды? (0 - '
          f'{kettle.max_water_level}): ' , end='')
    # обработка ввода пользователя
    while True:
        try:
            water_level = float(input())
            if 0 <= water_level <= kettle.max_water_level:
                kettle.pour_water(water_level)
                break
        except ValueError:
            ...
        print(f'Введите число от 0 до {kettle.max_water_level}: ', end='')

    input('\nЧтобы включить чайник - нажмите Enter')
    kettle.start()
