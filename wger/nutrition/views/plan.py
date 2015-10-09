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

import six
import logging
import datetime

from django.shortcuts import render, get_object_or_404
from django.http import (
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseRedirect
)
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy, ugettext as _
from django.views.generic import DeleteView, UpdateView

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Table,
    Spacer
)

from wger.nutrition.models import (
    NutritionPlan,
    MEALITEM_WEIGHT_GRAM,
    MEALITEM_WEIGHT_UNIT
)
from wger import get_version
from wger.utils.generic_views import WgerFormMixin, WgerDeleteMixin
from wger.utils.helpers import check_token, make_token
from wger.utils.pdf import styleSheet
from wger.utils.language import load_language


logger = logging.getLogger(__name__)


# ************************
# Plan functions
# ************************


@login_required
def overview(request):
    template_data = {}
    template_data.update(csrf(request))

    plans = NutritionPlan.objects.filter(user=request.user)
    template_data['plans'] = plans

    return render(request, 'plan/overview.html', template_data)


@login_required
def add(request):
    '''
    Add a new nutrition plan and redirect to its page
    '''

    plan = NutritionPlan()
    plan.user = request.user
    plan.language = load_language()
    plan.save()

    return HttpResponseRedirect(reverse('nutrition:plan:view', kwargs={'id': plan.id}))


class PlanDeleteView(WgerDeleteMixin, DeleteView):
    '''
    Generic view to delete a nutritional plan
    '''

    model = NutritionPlan
    success_url = reverse_lazy('nutrition:plan:overview')
    form_action_urlname = 'nutrition:plan:delete'
    messages = ugettext_lazy('Successfully deleted')

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        context = super(PlanDeleteView, self).get_context_data(**kwargs)
        context['title'] = _(u'Delete {0}?').format(self.object)
        return context


class PlanEditView(WgerFormMixin, UpdateView):
    '''
    Generic view to update an existing nutritional plan
    '''

    model = NutritionPlan
    fields = '__all__'
    form_action_urlname = 'nutrition:plan:edit'

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        context = super(PlanEditView, self).get_context_data(**kwargs)
        context['title'] = _(u'Edit {0}').format(self.object)
        return context


def view(request, id):
    '''
    Show the nutrition plan with the given ID
    '''
    template_data = {}

    plan = get_object_or_404(NutritionPlan, pk=id)
    user = plan.user
    is_owner = request.user == user

    if not is_owner and not user.userprofile.ro_access:
        return HttpResponseForbidden()

    uid, token = make_token(user)

    # Load the language and pass it to the template
    language = load_language()
    template_data['language'] = language
    template_data['MEALITEM_WEIGHT_GRAM'] = MEALITEM_WEIGHT_GRAM
    template_data['MEALITEM_WEIGHT_UNIT'] = MEALITEM_WEIGHT_UNIT

    # Get the nutritional info
    template_data['plan'] = plan
    template_data['nutritional_data'] = plan.get_nutritional_values()

    # Tokens for the links
    template_data['uid'] = uid
    template_data['token'] = token
    template_data['owner_user'] = user
    template_data['is_owner'] = is_owner
    template_data['show_shariff'] = is_owner

    return render(request, 'plan/view.html', template_data)


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
    return HttpResponseRedirect(reverse('nutrition:plan:view', kwargs={'id': plan.id}))


def export_pdf(request, id, uidb64=None, token=None):
    '''
    Generates a PDF with the contents of a nutrition plan

    See also
    * http://www.blog.pythonlibrary.org/2010/09/21/reportlab
    * http://www.reportlab.com/apis/reportlab/dev/platypus.html
    '''

    # Load the plan
    if uidb64 is not None and token is not None:
        if check_token(uidb64, token):
            plan = get_object_or_404(NutritionPlan, pk=id)
        else:
            return HttpResponseForbidden()
    else:
        if request.user.is_anonymous():
            return HttpResponseForbidden()
        plan = get_object_or_404(NutritionPlan, pk=id, user=request.user)

    plan_data = plan.get_nutritional_values()

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')

    # Create the PDF object, using the response object as its "file."
    doc = SimpleDocTemplate(response,
                            pagesize=A4,
                            title=_('Nutrition plan'),
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
            p = Paragraph(u'<para align="center"><strong>{nr} {meal_nr}</strong></para>'
                          .format(nr=_('Nr.'), meal_nr=i),
                          styleSheet["Normal"])
        else:
            p = Paragraph(u'<para align="center"><strong>'
                          u'{nr} {meal_nr} - {meal_time}'
                          u'</strong></para>'
                          .format(nr=_('Nr.'), meal_nr=i, meal_time=meal.time.strftime("%H:%M")),
                          styleSheet["Normal"])
        data.append([p])

        # Ingredients
        for item in meal.mealitem_set.select_related():
            ingredient_markers.append(len(data))

            p = Paragraph(u'<para>{0}</para>'.format(item.ingredient.name), styleSheet["Normal"])
            if item.get_unit_type() == MEALITEM_WEIGHT_GRAM:
                unit_name = 'g'
            else:
                unit_name = ' ' + item.weight_unit.unit.name

            data.append([Paragraph(u"{0}{1}".format(item.amount, unit_name), styleSheet["Normal"]),
                         p])

    # Set general table styles
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
        t._argW[0] = 2.5 * cm

    # There is nothing to output
    else:
        t = Paragraph(_('<i>This is an empty plan, what did you expect on the PDF?</i>'),
                      styleSheet["Normal"])

    # Set the title (if available)
    if plan.description:
        p = Paragraph('<para align="center"><strong>%(description)s</strong></para>' %
                      {'description': plan.description},
                      styleSheet["Bold"])
        elements.append(p)

        # Filler
        elements.append(Spacer(10 * cm, 0.5 * cm))

    # append the table to the document
    elements.append(t)
    elements.append(Paragraph('<para>&nbsp;</para>', styleSheet["Normal"]))

    # Create table with nutritional calculations
    data = []
    data.append([Paragraph(u'<para align="center">{0}</para>'.format(_('Nutritional data')),
                 styleSheet["Bold"])])
    data.append([Paragraph(_('Macronutrients'), styleSheet["Normal"]),
                 Paragraph(_('Total'), styleSheet["Normal"]),
                 Paragraph(_('Percent of energy'), styleSheet["Normal"]),
                 Paragraph(_('g per body kg'), styleSheet["Normal"])])
    data.append([Paragraph(_('Energy'), styleSheet["Normal"]),
                 Paragraph(six.text_type(plan_data['total']['energy']), styleSheet["Normal"])])
    data.append([Paragraph(_('Protein'), styleSheet["Normal"]),
                 Paragraph(six.text_type(plan_data['total']['protein']), styleSheet["Normal"]),
                 Paragraph(six.text_type(plan_data['percent']['protein']), styleSheet["Normal"]),
                 Paragraph(six.text_type(plan_data['per_kg']['protein']), styleSheet["Normal"])])
    data.append([Paragraph(_('Carbohydrates'), styleSheet["Normal"]),
                 Paragraph(six.text_type(plan_data['total']['carbohydrates']),
                           styleSheet["Normal"]),
                 Paragraph(six.text_type(plan_data['percent']['carbohydrates']),
                           styleSheet["Normal"]),
                 Paragraph(six.text_type(plan_data['per_kg']['carbohydrates']),
                           styleSheet["Normal"])])
    data.append([Paragraph(_('Sugar content in carbohydrates'), styleSheet["Normal"]),
                 Paragraph(six.text_type(plan_data['total']['carbohydrates_sugar']),
                           styleSheet["Normal"])])
    data.append([Paragraph(_('Fat'), styleSheet["Normal"]),
                 Paragraph(six.text_type(plan_data['total']['fat']), styleSheet["Normal"]),
                 Paragraph(six.text_type(plan_data['percent']['fat']), styleSheet["Normal"]),
                 Paragraph(six.text_type(plan_data['per_kg']['fat']), styleSheet["Normal"])])
    data.append([Paragraph(_('Saturated fat content in fats'), styleSheet["Normal"]),
                 Paragraph(six.text_type(plan_data['total']['fat_saturated']),
                           styleSheet["Normal"])])
    data.append([Paragraph(_('Fibres'), styleSheet["Normal"]),
                 Paragraph(six.text_type(plan_data['total']['fibres']), styleSheet["Normal"])])
    data.append([Paragraph(_('Sodium'), styleSheet["Normal"]),
                 Paragraph(six.text_type(plan_data['total']['sodium']), styleSheet["Normal"])])

    table_style = []
    table_style.append(('BOX', (0, 0), (-1, -1), 1.25, colors.black))
    table_style.append(('GRID', (0, 0), (-1, -1), 0.40, colors.black))
    table_style.append(('SPAN', (0, 0), (-1, 0)))  # Title
    table_style.append(('SPAN', (1, 2), (-1, 2)))  # Energy
    table_style.append(('SPAN', (1, 5), (-1, 5)))  # Sugar
    table_style.append(('SPAN', (1, 7), (-1, 7)))  # Saturated fats
    table_style.append(('SPAN', (1, 8), (-1, 8)))  # Fibres
    table_style.append(('SPAN', (1, 9), (-1, 9)))  # Sodium
    t = Table(data, style=table_style)
    t._argW[0] = 5 * cm
    elements.append(t)

    # Footer, date and info
    elements.append(Spacer(10 * cm, 0.5 * cm))
    created = datetime.date.today().strftime("%d.%m.%Y")
    url = reverse('nutrition:plan:view', kwargs={'id': plan.id})
    p = Paragraph('''<para align="left">
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
    elements.append(p)
    doc.build(elements)

    response['Content-Disposition'] = 'attachment; filename=nutritional-plan.pdf'
    response['Content-Length'] = len(response.content)
    return response
