from django.db import models

# Create your models here.


class MciDataOneToOne(models.Model):

    calendar_work_rate = models.FloatField(verbose_name='日历作业率')
    rolling_interval = models.FloatField(verbose_name='轧制间隔')
    hourly_tonnage = models.FloatField(verbose_name='小时产量吨位')
    finished_product_rate = models.FloatField(verbose_name='成材率')
    blockade_rate = models.FloatField(verbose_name='封闭率')

    fuel_consumption = models.FloatField(verbose_name='燃耗')
    power_consumption = models.FloatField(verbose_name='电耗')
    roll_consumption = models.FloatField(verbose_name='辊耗')

    thickness_precision = models.FloatField(verbose_name='厚度精度')
    width_precision = models.FloatField(verbose_name='宽度精度')
    coiling_temperature_precision = models.FloatField(verbose_name='卷取温度精度')

    base_tag = models.CharField(max_length=20, verbose_name='基地标签')
    base_name = models.CharField(max_length=20, verbose_name='基地名称')
    bmk_tag = models.CharField(max_length=50, verbose_name='对标标签')
    bmk_name = models.CharField(max_length=50, verbose_name='对标名称')

    effective_mci = models.FloatField(verbose_name='有效MCI')
    uniform_mci = models.FloatField(verbose_name='均匀MCI')
    mill_line_mci = models.FloatField(verbose_name='产线MCI')

    month_tag = models.CharField(max_length=20, verbose_name='月份标签')
    month_tag_name = models.CharField(max_length=20, verbose_name='月份名称')
    quarter_tag = models.CharField(max_length=20, verbose_name='季度标签')
    quarter_tag_name = models.CharField(max_length=20, verbose_name='季度名称')
    year_tag = models.CharField(max_length=20, verbose_name='年度标签')
    year_tag_name = models.CharField(max_length=20, verbose_name='年度名称')

    class Meta:
        verbose_name = '一对一制造能力指数'
        db_table = 'mci_data_one_to_one'


class MciDataBestToBest(models.Model):

    calendar_work_rate = models.FloatField(verbose_name='日历作业率')
    rolling_interval = models.FloatField(verbose_name='轧制间隔')
    hourly_tonnage = models.FloatField(verbose_name='小时产量吨位')
    finished_product_rate = models.FloatField(verbose_name='成材率')
    blockade_rate = models.FloatField(verbose_name='封闭率')

    fuel_consumption = models.FloatField(verbose_name='燃耗')
    power_consumption = models.FloatField(verbose_name='电耗')
    roll_consumption = models.FloatField(verbose_name='辊耗')

    thickness_precision = models.FloatField(verbose_name='厚度精度')
    width_precision = models.FloatField(verbose_name='宽度精度')
    coiling_temperature_precision = models.FloatField(verbose_name='卷取温度精度')

    base_tag = models.CharField(max_length=20, verbose_name='基地标签')
    base_name = models.CharField(max_length=20, verbose_name='基地名称')
    bmk_tag = models.CharField(max_length=50, verbose_name='对标标签')
    bmk_name = models.CharField(max_length=50, verbose_name='对标名称')

    effective_mci = models.FloatField(verbose_name='有效MCI')
    uniform_mci = models.FloatField(verbose_name='均匀MCI')
    mill_line_mci = models.FloatField(verbose_name='产线MCI')

    month_tag = models.CharField(max_length=20, verbose_name='月份标签')
    month_tag_name = models.CharField(max_length=20, verbose_name='月份名称')
    quarter_tag = models.CharField(max_length=20, verbose_name='季度标签')
    quarter_tag_name = models.CharField(max_length=20, verbose_name='季度名称')
    year_tag = models.CharField(max_length=20, verbose_name='年度标签')
    year_tag_name = models.CharField(max_length=20, verbose_name='年度名称')

    class Meta:
        verbose_name = '优对优制造能力指数'
        db_table = 'mci_data_best_to_best'


class MciDataOverall(models.Model):

    base_tag = models.CharField(max_length=20, verbose_name='基地标签')
    base_name = models.CharField(max_length=20, verbose_name='基地名称')

    overall_mci = models.FloatField(verbose_name='综合MCI')

    month_tag = models.CharField(max_length=20, verbose_name='月份标签')
    month_tag_name = models.CharField(max_length=20, verbose_name='月份名称')
    quarter_tag = models.CharField(max_length=20, verbose_name='季度标签')
    quarter_tag_name = models.CharField(max_length=20, verbose_name='季度名称')
    year_tag = models.CharField(max_length=20, verbose_name='年度标签')
    year_tag_name = models.CharField(max_length=20, verbose_name='年度名称')

    class Meta:
        verbose_name = '综合制造能力指数'
        db_table = 'mci_data_overall'
