import subprocess
import os


def convert_to_tiktok_and_YtShorts(input_path):

    """

    Функция для конвертации широкоугольгного видео в портреный вид

    :param input_path: Путь к изначальному видео
    :return: output_path, путь к конечному видео, смонтированому

    """

    # Убедимся, что ffmpeg.exe доступен
    ffmpeg_path = "instaled_instruments/ffmpeg.exe"  # Если ffmpeg в PATH или в папке с скриптом
    output_path = "".join(input_path.split(".")[:-1]) + "_short.mp4"
    # Проверка существования входного файла
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"❌ Входной файл не найден: {input_path}")

    cmd = [
        ffmpeg_path,
        '-i', input_path,
        '-vf', "scale=1080:-2,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black",
        '-c:v', 'libx264',
        '-preset', 'fast',  # Ускорение кодирования
        '-crf', '23',  # Качество (18-28, где меньше = лучше)
        '-c:a', 'copy',  # Без перекодирования аудио
        '-movflags', '+faststart',  # Для быстрой загрузки в браузерах
        '-y',  # Перезаписать выходной файл без подтверждения
        output_path
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ Видео успешно сохранено: {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка FFmpeg:\n{e.stderr}")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")

