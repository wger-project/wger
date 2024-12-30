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
from django.forms import model_to_dict
from django.http import (
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext as _

# Third Party
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
)

# wger
from wger.nutrition.consts import MEALITEM_WEIGHT_GRAM
from wger.nutrition.models import (
    Meal,
    MealItem,
    NutritionPlan,
)
from wger.utils.pdf import (
    get_logo,
    header_colour,
    render_footer,
    row_color,
    styleSheet,
)


logger = logging.getLogger(__name__)


# ************************
# Plan functions
# ************************


@login_required
def copy(request, pk):
    """
    Copy the nutrition plan
    """
    orig_plan = get_object_or_404(NutritionPlan, pk=pk, user=request.user)

    # Convert the original plan to a dictionary and remove the primary key
    plan_data = model_to_dict(orig_plan)
    plan_data.pop('id')

    plan_copy = NutritionPlan.objects.create(user=request.user, **plan_data)

    # Copy meals and meal items
    orig_meals = orig_plan.meal_set.all()
    for orig_meal in orig_meals:
        meal_data = model_to_dict(orig_meal)
        meal_data.pop('id')
        meal_data['plan'] = plan_copy
        # setting manually due to "editable" False
        meal_data['order'] = orig_meal.order

        meal_copy = Meal.objects.create(**meal_data)

        orig_meal_items = orig_meal.mealitem_set.all()
        for orig_meal_item in orig_meal_items:
            meal_item_data = model_to_dict(orig_meal_item)
            meal_item_data.pop('id')
            meal_item_data.pop('ingredient')
            meal_item_data['meal'] = meal_copy
            meal_item_data['ingredient_id'] = orig_meal_item.ingredient_id
            # setting manually due to "editable" False
            meal_item_data['order'] = orig_meal_item.order
            MealItem.objects.create(**meal_item_data)

    # Redirect
    return HttpResponseRedirect(reverse('nutrition:plan:view', kwargs={'id': plan_copy.id}))


def export_pdf(request, id: int):
    """
    Generates a PDF with the contents of a nutrition plan

    See also
    * http://www.blog.pythonlibrary.org/2010/09/21/reportlab
    * http://www.reportlab.com/apis/reportlab/dev/platypus.html
    """
    # Load the plan
    if request.user.is_anonymous:
        return HttpResponseForbidden()
    plan = get_object_or_404(NutritionPlan, pk=id, user=request.user)

    plan_data = plan.get_nutritional_values()

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')

    # Create the PDF object, using the response object as its "file."
    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        title=_('Nutritional plan'),
        author='wger Workout Manager',
        subject=_('Nutritional plan for %s') % request.user.username,
        topMargin=1 * cm,
    )

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
            p = Paragraph(
                f'<para align="center"><strong>{_("Nr.")} {i}</strong></para>',
                styleSheet['SubHeader'],
            )
        else:
            p = Paragraph(
                f'<para align="center"><strong>'
                f'{_("Nr.")} {i} - {meal.time.strftime("%H:%M")}'
                f'</strong></para>',
                styleSheet['SubHeader'],
            )
        data.append([p])

        # Ingredients
        for item in meal.mealitem_set.select_related():
            ingredient_markers.append(len(data))

            p = Paragraph(f'<para>{item.ingredient.name}</para>', styleSheet['Normal'])
            if item.get_unit_type() == MEALITEM_WEIGHT_GRAM:
                unit_name = 'g'
            else:
                unit_name = ' × ' + item.weight_unit.unit.name

            data.append(
                [Paragraph('{0:.0f}{1}'.format(item.amount, unit_name), styleSheet['Normal']), p]
            )

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
        t = Paragraph(
            _('<i>This is an empty plan, what did you expect on the PDF?</i>'), styleSheet['Normal']
        )

    # Add site logo
    elements.append(get_logo())
    elements.append(Spacer(10 * cm, 0.5 * cm))

    # Set the title (if available)
    if plan.description:
        p = Paragraph(
            '<para align="center"><strong>%(description)s</strong></para>'
            % {'description': plan.description},
            styleSheet['HeaderBold'],
        )
        elements.append(p)

        # Filler
        elements.append(Spacer(10 * cm, 1.5 * cm))

    # append the table to the document
    elements.append(t)
    elements.append(Paragraph('<para>&nbsp;</para>', styleSheet['Normal']))

    # Create table with nutritional calculations
    data = []
    data.append(
        [
            Paragraph(
                f'<para align="center">{_("Nutritional data")}</para>',
                styleSheet['SubHeaderBlack'],
            )
        ]
    )
    data.append(
        [
            Paragraph(_('Macronutrients'), styleSheet['Normal']),
            Paragraph(_('Total'), styleSheet['Normal']),
            Paragraph(_('Percent of energy'), styleSheet['Normal']),
            Paragraph(_('g per body kg'), styleSheet['Normal']),
        ]
    )
    data.append(
        [
            Paragraph(_('Energy'), styleSheet['Normal']),
            Paragraph(str(plan_data['total'].energy), styleSheet['Normal']),
        ]
    )
    data.append(
        [
            Paragraph(_('Protein'), styleSheet['Normal']),
            Paragraph(str(plan_data['total'].protein), styleSheet['Normal']),
            Paragraph(str(plan_data['percent']['protein']), styleSheet['Normal']),
            Paragraph(str(plan_data['per_kg']['protein']), styleSheet['Normal']),
        ]
    )
    data.append(
        [
            Paragraph(_('Carbohydrates'), styleSheet['Normal']),
            Paragraph(str(plan_data['total'].carbohydrates), styleSheet['Normal']),
            Paragraph(str(plan_data['percent']['carbohydrates']), styleSheet['Normal']),
            Paragraph(str(plan_data['per_kg']['carbohydrates']), styleSheet['Normal']),
        ]
    )
    data.append(
        [
            Paragraph('    ' + _('Sugar content in carbohydrates'), styleSheet['Normal']),
            Paragraph(str(plan_data['total'].carbohydrates_sugar), styleSheet['Normal']),
        ]
    )
    data.append(
        [
            Paragraph(_('Fat'), styleSheet['Normal']),
            Paragraph(str(plan_data['total'].fat), styleSheet['Normal']),
            Paragraph(str(plan_data['percent']['fat']), styleSheet['Normal']),
            Paragraph(str(plan_data['per_kg']['fat']), styleSheet['Normal']),
        ]
    )
    data.append(
        [
            Paragraph(_('Saturated fat content in fats'), styleSheet['Normal']),
            Paragraph(str(plan_data['total'].fat_saturated), styleSheet['Normal']),
        ]
    )
    data.append(
        [
            Paragraph(_('Fiber'), styleSheet['Normal']),
            Paragraph(str(plan_data['total'].fiber), styleSheet['Normal']),
        ]
    )
    data.append(
        [
            Paragraph(_('Sodium'), styleSheet['Normal']),
            Paragraph(str(plan_data['total'].sodium), styleSheet['Normal']),
        ]
    )

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
    table_style.append(('SPAN', (1, 8), (-1, 8)))  # Fiber
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
