import pyaudio # Библиотека для работы с аудио в реальном времени.
import wave
import json
import noisereduce as nr # Библиотека для снижения шума в аудиозаписях.
from scipy.io import wavfile
from vosk import Model, KaldiRecognizer # Библиотека для распознавания речи.
import os
import librosa # Библиотека для анализа аудио и музыки.
import soundfile as sf #Библиотека для чтения и записи звуковых файлов.

# Таблица команд.
table = {
    "отказ": 0,
    "отмена": 1,
    "подтверждение": 2,
    "начать осаживание": 3,
    "продолжаем осаживание": 5,
    "зарядка тормозной магистрали": 6,
    "вышел из межвагонного пространства": 7,
    "продолжаем роспуск": 8,
    "растянуть автосцепки": 9,
    "отцепка": 11,
    "назад на башмак": 12,
    "захожу в межвагонное пространство": 13,
    "остановка": 14,
    "вперед на башмак": 15,
    "сжать автосцепки": 16,
    "назад с башмака": 17,
    "тише": 18,
    "вперед с башмака": 19,
    "прекратить зарядку тормозной магистрали": 20,
    "тормозить": 21,
    "отпустить": 22
}
# Таблица для преобразования числительного в число

table2 = {
    "один" : 1,
    "два": 2,
    "три": 3,
    "четыре": 4,
    "пять": 5,
    "шесть": 6,
    "семь": 7,
    "восемь": 8,
    "девять": 9,
    "десять": 10,
    "одинадцать": 11,
    "двенадцать": 12,
    "тринадцать": 13,
    "четырнадцать": 14,
    "пятнадцать": 15,
    "шестнадцать": 16,
    "семнадцать": 17,
    "восемнадцать": 18,
    "девятнадцать": 19,
    "двадцать": 20,
    "тридцать": 30,
    "сорок": 40,
    "пятьдесят": 50,
    "шестьдесят": 60,
    "семьдесят": 70,
    "восемьдесят": 80,
    "девяносто": 90
}

# Предполагает атрибут команд 4 и 10.
def spisok(query,attribute = 0):
    eror = False
    query = query.split(" ")
    number1 = query[2]
    # print(number1, len(query)) отладка
    number1 = table2.get(number1, " ")
    # print("number1",number1) отладка
    # измеряем сколько токенов
    if (number1 <= 19 and len(query) == 4):  # От 1 до 19 - первый случай
        attribute = number1
    elif (number1 > 19 and len(query) == 4):  # 20 30 ... 90 - второй случай
        attribute = number1
    elif (number1 > 19 and len(query) == 5):  # От 21 до 99 - третий случай
        number2 = query[3]
        number2 = table2.get(number2, " ")
        if number2 < 10:
            attribute = number1 + number2
        else:
            eror = True
    # допущена ошибка при произношении числа
    else:
        eror = True

    # print("error",eror) отладка
    # print(attribute) отладка
    if eror == True: attribute = 0
    return attribute


# Анализирует строку que,
def get_attribute(que):
    query = str(que)
    label = -1
    attribute = -1


    #Определение команды 4 или 10
    osad1 = query.startswith("осадить на ")
    kon1 = query.endswith("вагон")
    kon2 = query.endswith("вагона")
    kon3 = query.endswith("вагонов")
    protyn = query.startswith("протянуть на ")
    
    # Чтобы определить, соответствует ли она определенной команде.
    if (osad1 == True and (kon1 == True or kon2 == True or kon3 == True)):
        label = 4
        attribute = spisok(query)
    elif (protyn == True and (kon1 == True or kon2 == True or kon3 == True)):
        label = 10
        attribute = spisok(query)
    else:
        label = table.get(query, "Ошибка")

    if label == "Ошибка":
        print("Ошибка распознавания")
        attribute = 0
    else:
        print("Команда: ", query)
    return attribute, label

# Модель распознавания речи Vosk.
model = Model('vosk-model-small-ru-0.22')
rec = KaldiRecognizer(model, 16000)

def listen_offline():
    input_file = '3a1fb1e8-76ff-11ee-9242-c09bf4619c03.mp3'
    output_file = "output_audio.wav"
    
    # Загрузка аудиофайла и удаление шума
    audio, sample_rate = librosa.load(input_file, sr=16000)
    reduced_noise_audio = nr.reduce_noise(y=audio, sr=sample_rate)

    # Сохранение обработанного аудиофайла
    sf.write(output_file, reduced_noise_audio, 16000)

    with wave.open(output_file, 'rb') as f:
        data = f.readframes(f.getnframes())

    if rec.AcceptWaveform(data) and len(data) > 0:
        query = rec.Result()
        return json.loads(query)['text']
    
    return None

def main():
    query = listen_offline()
    
    attribute, label = get_attribute(query)
    
     # Открываем JSON файл
    with open("keeys.json", "rb") as f:
        l = json.load(f)
    
     # Проверяем наличие ключа в словаре
    found_key = None
    for key, phrases in l.items():
        print(key)
        if any(phrase in query for phrase in phrases):
            found_key = key
            break
    
    # #ключ для определенного атрибута
    print(query)
    if found_key:
        print("Запрос:", query)
        attribute, label = get_attribute(found_key)
        print("Метка:", label,"Атрибут:", attribute)
    else:
         print("Запрос не распознан.")

# Запущен ли файл как основная программа.
if __name__ == '__main__':
    main()
