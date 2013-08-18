# -*- coding: utf-8 -*-

# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wger Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
import logging
import datetime

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy

from django.views.generic import DeleteView
from django.views.generic import UpdateView

from wger.nutrition.models import NutritionPlan
from wger.nutrition.models import MEALITEM_WEIGHT_GRAM
from wger.nutrition.models import MEALITEM_WEIGHT_UNIT

from reportlab.lib.pagesizes import A4, cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table
from reportlab.lib import colors

from wger import get_version
from wger.utils.generic_views import WgerFormMixin
from wger.utils.generic_views import YamlDeleteMixin
from wger.utils.pdf import styleSheet
from wger.utils.language import load_language


logger = logging.getLogger('wger.custom')


# ************************
# Plan functions
# ************************


@login_required
def overview(request):
    template_data = {}
    template_data.update(csrf(request))

    plans = NutritionPlan.objects.filter(user=request.user)
    template_data['plans'] = plans

    return render_to_response('plan/overview.html',
                              template_data,
                              context_instance=RequestContext(request))


@login_required
def add(request):
    '''
    Add a new nutrition plan and redirect to its page
    '''

    plan = NutritionPlan()
    plan.user = request.user
    plan.language = load_language()
    plan.save()

    return HttpResponseRedirect(reverse('wger.nutrition.views.plan.view', kwargs={'id': plan.id}))


class PlanDeleteView(YamlDeleteMixin, DeleteView):
    '''
    Generic view to delete a nutritional plan
    '''

    model = NutritionPlan
    success_url = reverse_lazy('wger.nutrition.views.plan.overview')
    title = ugettext_lazy('Delete nutritional plan?')
    form_action_urlname = 'nutrition-delete'
    messages = ugettext_lazy('Nutritional plan was successfully deleted')


class PlanEditView(WgerFormMixin, UpdateView):
    '''
    Generic view to update an existing nutritional plan
    '''

    model = NutritionPlan
    title = ugettext_lazy('Add a new nutritional plan')
    form_action_urlname = 'nutrition-edit'


@login_required
def view(request, id):
    '''
    Show the nutrition plan with the given ID
    '''
    template_data = {}

    plan = get_object_or_404(NutritionPlan, pk=id, user=request.user)
    template_data['plan'] = plan

    # Load the language and pass it to the template
    language = load_language()
    template_data['language'] = language
    template_data['MEALITEM_WEIGHT_GRAM'] = MEALITEM_WEIGHT_GRAM
    template_data['MEALITEM_WEIGHT_UNIT'] = MEALITEM_WEIGHT_UNIT

    # Get the nutrional info

    template_data['nutritional_data'] = plan.get_nutritional_values()

    return render_to_response('plan/view.html',
                              template_data,
                              context_instance=RequestContext(request))


@login_required
def copy(request, pk):
    '''
    Copy the nutrition plan
    '''

    plan = get_object_or_404(NutritionPlan, pk=pk, user=request.user)

    # Copy plan
    meals = plan.meal_set.all()

    plan_copy = plan
    plan_copy.pk = None
    plan_copy.save()

    # Copy the meals
    for meal in meals:
        meal_items = meal.mealitem_set.all()

        meal_copy = meal
        meal_copy.pk = None
        meal_copy.plan = plan_copy
        meal_copy.save()

        # Copy the individual meal entries
        for item in meal_items:
            item_copy = item
            item_copy.pk = None
            item_copy.meal = meal_copy
            item.save()

    # Redirect
    return HttpResponseRedirect(reverse('wger.nutrition.views.plan.view', kwargs={'id': plan.id}))


@login_required
def export_pdf(request, id):
    '''
    Generates a PDF with the contents of a nutrition plan

    See also
    * http://www.blog.pythonlibrary.org/2010/09/21/reportlab
    * http://www.reportlab.com/apis/reportlab/dev/platypus.html
    '''

    #Load the workout
    plan = get_object_or_404(NutritionPlan, pk=id, user=request.user)

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(mimetype='application/pdf')

    # Translators: translation can only have ASCII characters
    response['Content-Disposition'] = 'attachment; filename=%s.pdf' % _('nutritional-plan')

    # Create the PDF object, using the response object as its "file."
    doc = SimpleDocTemplate(response,
                            pagesize=A4,
                            title=_('Workout'),
                            author='wger Workout Manager',
                            subject=_('Nutritional plan %s') % request.user.username)

    # Background colour for header
    # Reportlab doesn't use the HTML hexadecimal format, but has a range of
    # 0 till 1, so we have to convert here.
    header_colour = colors.Color(int('73', 16) / 255.0,
                                 int('8a', 16) / 255.0,
                                 int('5f', 16) / 255.0)

    # container for the 'Flowable' objects
    elements = []

    data = []

    # Iterate through the Plan
    meal_markers = []
    ingredient_markers = []

    # Meals
    i = 0
    for meal in plan.meal_set.select_related():
        i += 1

        meal_markers.append(len(data))

        if not meal.time:
            P = Paragraph('<para align="center"><strong>%(meal_nr)s</strong></para>' %
                          {'meal_nr': i},
                          styleSheet["Normal"])
        else:
            P = Paragraph('<para align="center"><strong>%(meal_nr)s - '
                          '%(meal_time)s</strong></para>' %
                          {'meal_nr': i,
                           'meal_time': meal.time.strftime("%H:%M")},
                          styleSheet["Normal"])
        data.append([P])

        # Ingredients
        for item in meal.mealitem_set.select_related():
            ingredient_markers.append(len(data))

            P = Paragraph('<para>%s</para>' % item.ingredient.name,
                          styleSheet["Normal"])

            if item.get_unit_type() == MEALITEM_WEIGHT_GRAM:
                unit_name = 'g'
            else:
                unit_name = ' ' + item.weight_unit.unit.name
            data.append([u"{0}{1}".format(item.amount, unit_name), P])

    # Set general table styles

    #('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
    #('BOX', (0,0), (-1,-1), 0.25, colors.black)
    table_style = []

    # Set specific styles, e.g. background for title cells
    for marker in meal_markers:
        # Set background colour for headings
        table_style.append(('BACKGROUND', (0, marker), (-1, marker), header_colour))
        table_style.append(('BOX', (0, marker), (-1, marker), 1.25, colors.black))

        # Make the headings span the whole width
        table_style.append(('SPAN', (0, marker), (-1, marker)))

    # has the plan any data?
    if data:
        t = Table(data, style=table_style)

        # Manually set the width of the columns
        t._argW[0] = 2 * cm

    # There is nothing to output
    else:
        t = Paragraph(_('<i>This is an empty plan, what did you expect on the PDF?</i>'),
                      styleSheet["Normal"])

    # Set the title (if available)
    if plan.description:
        P = Paragraph('<para align="center"><strong>%(description)s</strong></para>' %
                      {'description': plan.description},
                      styleSheet["Normal"])
        elements.append(P)

        # Filler
        P = Paragraph('<para> </para>', styleSheet["Normal"])
        elements.append(P)

    # append the table to the document
    elements.append(t)

    # Footer, add filler paragraph
    P = Paragraph('<para> </para>', styleSheet["Normal"])
    elements.append(P)

    # Print date and info
    created = datetime.date.today().strftime("%d.%m.%Y")
    url = reverse('wger.nutrition.views.plan.view', kwargs={'id': plan.id})
    P = Paragraph('''<para align="left">
                        %(date)s -
                        <a href="%(url)s">%(url)s</a> -
                        %(created)s
                        %(version)s
                    </para>''' %
                  {'date': _("Created on the <b>%s</b>") % created,
                   'created': "wger Workout Manager",
                   'version': get_version(),
                   'url': request.build_absolute_uri(url), },
                  styleSheet["Normal"])
    elements.append(P)
    doc.build(elements)

    return response
