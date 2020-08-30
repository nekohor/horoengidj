from django.shortcuts import render
from django.views import View

import json
from .charts import ChartDataSerializer
# Create your views here.


class KanBanView(View):

    def get(self, request):
        cds = ChartDataSerializer()

        context = {}

        context["mci_1v1_2250_bar_data"] = json.dumps(
            cds.get_bar_data("1v1", "MG2250"))
        context["mci_1v1_1580_bar_data"] = json.dumps(
            cds.get_bar_data("1v1", "MG1580"))
        context["mci_bvb_bar_data"] = json.dumps(
            cds.get_bar_data("bvb"))

        context["mci_1v1_2250_radar_data"] = json.dumps(
            cds.get_radar_data("1v1", "MG2250"))
        context["mci_1v1_1580_radar_data"] = json.dumps(
            cds.get_radar_data("1v1", "MG1580"))
        context["mci_bvb_radar_data"] = json.dumps(
            cds.get_radar_data("bvb"))

        return render(request, 'mci/kanban.html', context)
