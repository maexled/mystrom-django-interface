import os 

def export_vars(request):
    data = {}
    data['CHART_TYPE'] = os.getenv('CHART_TYPE', 'apexcharts')
    if data['CHART_TYPE'] != 'apexcharts' and data['CHART_TYPE'] != 'uplot':
        data['CHART_TYPE'] = 'apexcharts'
    return data