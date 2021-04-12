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

# Standard Library
import logging

# Django
from django.contrib.auth.decorators import login_required
from django.http import (
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseRedirect
)
from django.shortcuts import (
    get_object_or_404,
    render
)
from django.template.context_processors import csrf
from django.urls import (
    reverse,
    reverse_lazy
)
from django.utils.translation import (
    gettext as _,
    gettext_lazy
)
from django.views.generic import (
    DeleteView,
    UpdateView
)

# Third Party
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table
)

# wger
from wger.nutrition.models import (
    MEALITEM_WEIGHT_GRAM,
    MEALITEM_WEIGHT_UNIT,
    NutritionPlan
)
from wger.utils.generic_views import (
    WgerDeleteMixin,
    WgerFormMixin
)
from wger.utils.helpers import (
    check_token,
    make_token
)
from wger.utils.language import load_language
from wger.utils.pdf import (
    get_logo,
    header_colour,
    render_footer,
    row_color,
    styleSheet
)


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
    """
    Add a new nutrition plan and redirect to its page
    """

    plan = NutritionPlan()
    plan.user = request.user
    plan.language = load_language()
    plan.save()

    return HttpResponseRedirect(reverse('nutrition:plan:view', kwargs={'id': plan.id}))


class PlanDeleteView(WgerDeleteMixin, DeleteView):
    """
    Generic view to delete a nutritional plan
    """

    model = NutritionPlan
    fields = ('description', 'has_goal_calories')
    success_url = reverse_lazy('nutrition:plan:overview')
    messages = gettext_lazy('Successfully deleted')

    def get_context_data(self, **kwargs):
        """
        Send some additional data to the template
        """
        context = super(PlanDeleteView, self).get_context_data(**kwargs)
        context['title'] = _('Delete {0}?').format(self.object)
        return context


class PlanEditView(WgerFormMixin, UpdateView):
    """
    Generic view to update an existing nutritional plan
    """

    model = NutritionPlan
    fields = ('description', 'has_goal_calories')

    def get_context_data(self, **kwargs):
        """
        Send some additional data to the template
        """
        context = super(PlanEditView, self).get_context_data(**kwargs)
        context['title'] = _('Edit {0}').format(self.object)
        return context


def view(request, id):
    """
    Show the nutrition plan with the given ID
    """
    template_data = {}

    plan = get_object_or_404(NutritionPlan, pk=id)
    user = plan.user
    is_owner = request.user == user

    if not is_owner and not user.userprofile.ro_access:
        return HttpResponseForbidden()

    uid, token = make_token(user)

    # Process and show the last 5 diary entries
    log_data = []
    planned_calories = plan.get_nutritional_values()['total']['energy']
    for item in plan.get_log_overview()[:5]:
        log_data.append({'date': item['date'],
                         'planned_calories': planned_calories,
                         'logged_calories': item['energy'],
                         'difference': item['energy'] - planned_calories})

    # Load the language and pass it to the template
    language = load_language()
    template_data['language'] = language
    template_data['MEALITEM_WEIGHT_GRAM'] = MEALITEM_WEIGHT_GRAM
    template_data['MEALITEM_WEIGHT_UNIT'] = MEALITEM_WEIGHT_UNIT

    # Get the nutritional info
    template_data['plan'] = plan
    template_data['nutritional_data'] = \
        plan.get_nutritional_values()

    # Get the weight entry used
    template_data['weight_entry'] = plan.get_closest_weight_entry()

    # Tokens for the links
    template_data['uid'] = uid
    template_data['log_data'] = log_data
    template_data['token'] = token
    template_data['owner_user'] = user
    template_data['is_owner'] = is_owner
    template_data['show_shariff'] = is_owner

    return render(request, 'plan/view.html', template_data)


@login_required
def copy(request, pk):
    """
    Copy the nutrition plan
    """

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
    """
    Generates a PDF with the contents of a nutrition plan

    See also
    * http://www.blog.pythonlibrary.org/2010/09/21/reportlab
    * http://www.reportlab.com/apis/reportlab/dev/platypus.html
    """

    # Load the plan
    if uidb64 is not None and token is not None:
        if check_token(uidb64, token):
            plan = get_object_or_404(NutritionPlan, pk=id)
        else:
            return HttpResponseForbidden()
    else:
        if request.user.is_anonymous:
            return HttpResponseForbidden()
        plan = get_object_or_404(NutritionPlan, pk=id, user=request.user)

    plan_data = plan.get_nutritional_values()

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')

    # Create the PDF object, using the response object as its "file."
    doc = SimpleDocTemplate(response,
                            pagesize=A4,
                            title=_('Nutritional plan'),
                            author='wger Workout Manager',
                            subject=_('Nutritional plan for %s') % request.user.username,
                            topMargin=1 * cm,)

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
            p = Paragraph('<para align="center"><strong>{nr} {meal_nr}</strong></para>'
                          .format(nr=_('Nr.'), meal_nr=i),
                          styleSheet["SubHeader"])
        else:
            p = Paragraph('<para align="center"><strong>'
                          '{nr} {meal_nr} - {meal_time}'
                          '</strong></para>'
                          .format(nr=_('Nr.'), meal_nr=i, meal_time=meal.time.strftime("%H:%M")),
                          styleSheet["SubHeader"])
        data.append([p])

        # Ingredients
        for item in meal.mealitem_set.select_related():
            ingredient_markers.append(len(data))

            p = Paragraph('<para>{0}</para>'.format(item.ingredient.name), styleSheet["Normal"])
            if item.get_unit_type() == MEALITEM_WEIGHT_GRAM:
                unit_name = 'g'
            else:
                unit_name = ' × ' + item.weight_unit.unit.name

            data.append([Paragraph("{0:.0f}{1}".format(item.amount, unit_name),
                                   styleSheet["Normal"]), p])

        # Add filler
        data.append([Spacer(1 * cm, 0.6 * cm)])

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
        t._argW[0] = 3.5 * cm

    # There is nothing to output
    else:
        t = Paragraph(_('<i>This is an empty plan, what did you expect on the PDF?</i>'),
                      styleSheet["Normal"])

    # Add site logo
    elements.append(get_logo())
    elements.append(Spacer(10 * cm, 0.5 * cm))

    # Set the title (if available)
    if plan.description:

        p = Paragraph('<para align="center"><strong>%(description)s</strong></para>' %
                      {'description': plan.description},
                      styleSheet["HeaderBold"])
        elements.append(p)

        # Filler
        elements.append(Spacer(10 * cm, 1.5 * cm))

    # append the table to the document
    elements.append(t)
    elements.append(Paragraph('<para>&nbsp;</para>', styleSheet["Normal"]))

    # Create table with nutritional calculations
    data = []
    data.append([Paragraph('<para align="center">{0}</para>'.format(_('Nutritional data')),
                           styleSheet["SubHeaderBlack"])])
    data.append([Paragraph(_('Macronutrients'), styleSheet["Normal"]),
                 Paragraph(_('Total'), styleSheet["Normal"]),
                 Paragraph(_('Percent of energy'), styleSheet["Normal"]),
                 Paragraph(_('g per body kg'), styleSheet["Normal"])])
    data.append([Paragraph(_('Energy'), styleSheet["Normal"]),
                 Paragraph(str(plan_data['total']['energy']), styleSheet["Normal"])])
    data.append([Paragraph(_('Protein'), styleSheet["Normal"]),
                 Paragraph(str(plan_data['total']['protein']), styleSheet["Normal"]),
                 Paragraph(str(plan_data['percent']['protein']), styleSheet["Normal"]),
                 Paragraph(str(plan_data['per_kg']['protein']), styleSheet["Normal"])])
    data.append([Paragraph(_('Carbohydrates'), styleSheet["Normal"]),
                 Paragraph(str(plan_data['total']['carbohydrates']),
                           styleSheet["Normal"]),
                 Paragraph(str(plan_data['percent']['carbohydrates']),
                           styleSheet["Normal"]),
                 Paragraph(str(plan_data['per_kg']['carbohydrates']),
                           styleSheet["Normal"])])
    data.append([Paragraph("    " + _('Sugar content in carbohydrates'), styleSheet["Normal"]),
                 Paragraph(str(plan_data['total']['carbohydrates_sugar']),
                           styleSheet["Normal"])])
    data.append([Paragraph(_('Fat'), styleSheet["Normal"]),
                 Paragraph(str(plan_data['total']['fat']), styleSheet["Normal"]),
                 Paragraph(str(plan_data['percent']['fat']), styleSheet["Normal"]),
                 Paragraph(str(plan_data['per_kg']['fat']), styleSheet["Normal"])])
    data.append([Paragraph(_('Saturated fat content in fats'), styleSheet["Normal"]),
                 Paragraph(str(plan_data['total']['fat_saturated']),
                           styleSheet["Normal"])])
    data.append([Paragraph(_('Fibres'), styleSheet["Normal"]),
                 Paragraph(str(plan_data['total']['fibres']), styleSheet["Normal"])])
    data.append([Paragraph(_('Sodium'), styleSheet["Normal"]),
                 Paragraph(str(plan_data['total']['sodium']), styleSheet["Normal"])])

    table_style = []
    table_style.append(('BOX', (0, 0), (-1, -1), 1.25, colors.black))
    table_style.append(('GRID', (0, 0), (-1, -1), 0.40, colors.black))
    table_style.append(('SPAN', (0, 0), (-1, 0)))  # Title
    table_style.append(('SPAN', (1, 2), (-1, 2)))  # Energy
    table_style.append(('BACKGROUND', (0, 3), (-1, 3), row_color))  # Protein
    table_style.append(('BACKGROUND', (0, 4), (-1, 4), row_color))  # Carbohydrates
    table_style.append(('SPAN', (1, 5), (-1, 5)))  # Sugar
    table_style.append(('LEFTPADDING', (0, 5), (0, 5), 15))
    table_style.append(('BACKGROUND', (0, 6), (-1, 6), row_color))  # Fats
    table_style.append(('SPAN', (1, 7), (-1, 7)))  # Saturated fats
    table_style.append(('LEFTPADDING', (0, 7), (0, 7), 15))
    table_style.append(('SPAN', (1, 8), (-1, 8)))  # Fibres
    table_style.append(('SPAN', (1, 9), (-1, 9)))  # Sodium
    t = Table(data, style=table_style)
    t._argW[0] = 6 * cm
    elements.append(t)

    # Footer, date and info
    elements.append(Spacer(10 * cm, 0.5 * cm))
    elements.append(render_footer(request.build_absolute_uri(plan.get_absolute_url())))
    doc.build(elements)

    response['Content-Disposition'] = 'attachment; filename=nutritional-plan.pdf'
    response['Content-Length'] = len(response.content)
    return response
