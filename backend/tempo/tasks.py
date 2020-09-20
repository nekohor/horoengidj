import time
from celery import shared_task
from django.conf import settings

from .exporter.tempo_exporter import TempoExporter


@shared_task
def test_task():
    print("start sleep1")
    time.sleep(10)
    print("end sleep1")
    print("start sleep2")
    time.sleep(20)
    print("end sleep2")
    return "crontab tasks"


@shared_task
def tempo_data_calculation(mill_line_tag, start_time, end_time):
    tps = TempoExporter(mill_line_tag, start_time, end_time)
    df = tps.get_data()
    file_name = "tempo_data_{}_{}_{}.xlsx".format(
        mill_line_tag, start_time, end_time)
    file_path = settings.MEDIA_ROOT + "/" + file_name
    file_url = settings.MEDIA_URL + file_name
    print(file_path)
    print(file_url)
    df.to_excel(file_path)
    return file_url
