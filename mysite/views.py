import datetime
import flot
from django.views.generic import TemplateView
import mysite.model.full_model

class HomeView(TemplateView):
    template_name = 'base.html'

    def get_context_data(self, **kwargs):
        [x, ya, yb, yc] = mysite.model.full_model.main()
        pvp = flot.Series(xpoints = x, ypoints = ya, options = flot.SeriesOptions(label='PV Panel Power'))
        mpp = flot.Series(xpoints = x, ypoints = yb, options = flot.SeriesOptions(label='Max Power'))
        grp = flot.Series(xpoints = x, ypoints = yc, options = flot.SeriesOptions(label='Grid Power'))
        context = {'graph1': flot.Graph(series1 = pvp, series2=mpp),
                   'graph2': flot.Graph(series1 = pvp, series2=grp)}
        return context
