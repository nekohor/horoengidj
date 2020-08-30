import pandas as pd
from .models import MciDataOneToOne
from .models import MciDataBestToBest
from .models import MciDataOverall
from django_pandas.io import read_frame
import collections


class ChartDataSerializer():
    '''
    ===================== 如下所示chartjs bar图的结构 =====================
    var ctx = document.getElementById("oto2250bar").getContext("2d");
    var myChart = new Chart(ctx, {
      type: "bar",
      data: {
        labels: ["202001", "202002", "202003", "202004", "202005", "202006"],
        datasets: [
          {
            label: "马钢",
            data: [12, 19, 3, 5, 2, 3],
            backgroundColor: "#06f0ab",
          },
        ],
      },
      options: defaultOptions,
    });
    ===================== 如下所示chartjs radar图的结构 =====================

    '''

    def __init__(self):

        self.df = {}
        self.read_df_from_db()

        self.bar_colors = [
            "#06f0ab",
            "#06dcab",
            "#06c8ab",
            "#06b4ab",
            "#06a0ab",
            "#0696ab",
            "#0682ab",
            "",
        ]

        self.radar_colors = [
            "#FDFDFD",
            "#06F0AB",
            "#ED793C",
            "#F8D754",
            "#FD5995",
        ]

        self.index_names = collections.OrderedDict()

        self.index_names["blockade_rate"] = "封闭率"
        self.index_names["calendar_work_rate"] = "日历作业率"
        self.index_names["finished_product_rate"] = "成材率"
        self.index_names["hourly_tonnage"] = "小时产量吨位"
        self.index_names["rolling_interval"] = "轧制间隔"

        self.index_names["fuel_consumption"] = "燃耗"
        self.index_names["power_consumption"] = "电耗"
        self.index_names["roll_consumption"] = "辊耗"

        self.index_names["thickness_precision"] = "厚度精度um"
        self.index_names["width_precision"] = "宽度精度mm"
        self.index_names["coiling_temperature_precision"] = "卷取温度精度℃"

    def read_df_from_db(self):

        qs = MciDataOneToOne.objects.all()
        self.df["1v1"] = read_frame(qs)

        qs = MciDataBestToBest.objects.all()
        self.df["bvb"] = read_frame(qs)

        qs = MciDataOverall.objects.all()
        self.df["overall"] = read_frame(qs)

    def get_time_period_tag_names(self, df, time_period_tag_name_col):
        time_period_tags = list(set(df[time_period_tag_name_col]))
        time_period_tags.sort()
        return time_period_tags[-6:]

    def get_bmk_names(self, mci_mode, mg_line_tag=None):
        bmk_names = []
        if mci_mode == "1v1":
            bmk_names = self.get_bmk_names_1v1(mg_line_tag)
        elif mci_mode == "bvb":
            bmk_names = self.get_bmk_names_bvb()
        return bmk_names

    def get_bmk_names_1v1(self, mg_line_tag):
        bmk_names = []
        if mg_line_tag == "MG2250":
            bmk_names = [
                "马钢2250_浦项G3H2080",
                "宝山2050_浦项G3H2080",
                "青山2250_浦项G3H2080",
                "东山2250_浦项G3H2080",
            ]
        elif mg_line_tag == "MG1580":
            bmk_names = [
                "马钢1580_浦项P1H1422",
                "宝山1580_浦项P1H1422",
                "青山1580_浦项P1H1422",
                "梅山1422_浦项P1H1422",
            ]
        else:
            raise Exception("Wrong mg_line_tag in get_bmk_names()")

        return bmk_names

    def get_bmk_names_bvb(self):
        bmk_names = [
            "马钢_浦项POSCO",
            "宝山_浦项POSCO",
            "东山_浦项POSCO",
            "青山_浦项POSCO",
            "梅山_浦项POSCO",
        ]

        return bmk_names

    def get_bar_data(self, mci_mode, mg_line_tag=None):

        time_tag_name_col = "month_tag_name"
        df = self.df[mci_mode]

        time_period_tag_names = self.get_time_period_tag_names(
            df, time_tag_name_col)
        df = df.loc[df[time_tag_name_col].isin(time_period_tag_names)]

        res = {}
        res["labels"] = time_period_tag_names
        res["datasets"] = []

        bmk_names = self.get_bmk_names(mci_mode, mg_line_tag)
        for i, bmk_name in enumerate(bmk_names):
            data = {}
            data["label"] = bmk_name
            data["data"] = list(
                df.loc[df["bmk_name"] == bmk_name]["mill_line_mci"])
            data["backgroundColor"] = self.bar_colors[i]

            res["datasets"].append(data)
        return res

    def get_radar_data(self, mci_mode, mg_line_tag=None):

        time_tag_name_col = "month_tag_name"
        df = self.df[mci_mode]

        res = {}
        res["labels"] = [v for k, v in self.index_names.items()]
        res["datasets"] = []

        bmk_names = self.get_bmk_names(mci_mode, mg_line_tag)

        for i, bmk_name in enumerate(bmk_names):
            data = {}
            data["label"] = bmk_name
            data["data"] = self.get_radar_data_in_datasets(df, bmk_name)
            data["borderColor"] = self.radar_colors[i]
            data["pointBackgroundColor"] = self.radar_colors[i]
            data["pointHoverBorderColor"] = self.radar_colors[i]
            res["datasets"].append(data)

        return res

    def get_radar_data_in_datasets(self, df_src, bmk_name):

        df = df_src.loc[df_src["bmk_name"] == bmk_name]

        data = []
        for index_name in self.index_names.keys():
            data.append(round(df[index_name].mean(), 2))

        return data
