#views.py
from django.http import HttpResponse
from django.shortcuts import render_to_response,get_object_or_404, render
from django.template import RequestContext
from django.core import serializers
import flot
import random
from math import sin, pi

random.seed()
x = range(100)
yran = [random.random() for i in x]
 
def index(request, template_name="index.html"):
    sRan = flot.Series(xpoints = x, ypoints = yran, options = flot.SeriesOptions(label='y=sin'))
    myGraph = flot.Graph(series1 = sRan)
    return render(request, template_name, {'my_graph': myGraph, })

def getGraph(request,template_name="index.html"):
#    yran = yran[1:]+[random.random()]
    yran = [random.random() for i in x]
    sRan = flot.Series(xpoints = x, ypoints = yran, options = flot.SeriesOptions(label='y=random'))
    myGraph = flot.Graph(series1 = sRan)

    response=HttpResponse()
    response['Content-Type']="text/javascript"
    response.write(myGraph.json_data)
    return response


