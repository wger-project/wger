# -*- coding: utf-8 -*-

# This file is part of Workout Manager.
# 
# Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
import logging
import json

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.forms import ModelForm
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy


from django.views.generic import DeleteView
from django.views.generic import CreateView
from django.views.generic import UpdateView


from nutrition.models import NutritionPlan
from nutrition.models import Meal
from nutrition.models import MealItem
from nutrition.models import Ingredient

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4, cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table
from reportlab.lib import colors

from manager.utils import load_language
from manager.utils import load_ingredient_languages

from workout_manager import get_version
from workout_manager.constants import NUTRITION_TAB
from workout_manager.generic_views import YamlFormMixin
from workout_manager.generic_views import YamlDeleteMixin


logger = logging.getLogger('workout_manager.custom')


# ************************
# Plan functions
# ************************

class PlanForm(ModelForm):
    class Meta:
        model = NutritionPlan
        exclude=('user', 'language', )

@login_required
def overview(request):
    template_data = {}
    template_data.update(csrf(request))
    template_data['active_tab'] = NUTRITION_TAB
    
    plans  = NutritionPlan.objects.filter(user = request.user)
    template_data['plans'] = plans
    
    return render_to_response('nutrition_overview.html',
                              template_data,
                              context_instance=RequestContext(request))

@login_required
def add(request):
    """Add a new nutrition plan and redirect to its page
    """
    
    plan = NutritionPlan()
    plan.user = request.user
    plan.language = load_language()
    plan.save()
    
    return HttpResponseRedirect(reverse('nutrition.views.view', kwargs= {'id': plan.id}))

class PlanDeleteView(YamlDeleteMixin, DeleteView):
    """
    Generic view to delete a nutritional plan
    """
    
    active_tab = NUTRITION_TAB
    model = NutritionPlan
    success_url = reverse_lazy('nutrition.views.overview')
    title = ugettext_lazy('Delete nutritional plan?')
    form_action_urlname = 'nutrition-delete'

class PlanEditView(YamlFormMixin, UpdateView):
    """
    Generic view to update an existing nutritional plan
    """
    
    active_tab = NUTRITION_TAB
    model = NutritionPlan
    form_class = PlanForm
    title = ugettext_lazy('Add a new nutritional plan')
    form_action_urlname = 'nutrition-edit'


@login_required
def view(request, id):
    """Show the nutrition plan with the given ID
    """
    template_data = {}
    template_data['active_tab'] = NUTRITION_TAB
    
    plan = get_object_or_404(NutritionPlan, pk=id, user=request.user)
    template_data['plan'] = plan
    
    # Load the language and pass it to the template
    language = load_language()
    template_data['language'] = language
    
    # Get the nutrional info
    
    template_data['nutritional_data'] = plan.get_nutritional_values()
    
    return render_to_response('view_nutrition_plan.html', 
                              template_data,
                              context_instance=RequestContext(request))

def export_pdf(request, id):
    """Generates a PDF with the contents of a nutrition plan
    
    See also
    * http://www.blog.pythonlibrary.org/2010/09/21/reportlab-tables-creating-tables-in-pdfs-with-python/
    * http://www.reportlab.com/apis/reportlab/dev/platypus.html
    """
    
    #Load the workout
    plan = get_object_or_404(NutritionPlan, pk=id, user=request.user)
    
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(mimetype='application/pdf')
    
    # Translators: translation can only have ASCII characters
    response['Content-Disposition'] = 'attachment; filename=%s.pdf' % _('nutritional-plan') 
    
    # Create the PDF object, using the response object as its "file."
    doc = SimpleDocTemplate(response,
                            pagesize = A4,
                            title = _('Workout'),
                            author = _('Workout Manager'),
                            subject = _('Nutritional plan %s') % request.user.username)

    # Background colour for header
    # Reportlab doesn't use the HTML hexadecimal format, but has a range of
    # 0 till 1, so we have to convert here.
    header_colour = colors.Color(int('73', 16) / 255.0,
                                 int('8a', 16) / 255.0,
                                 int('5f', 16) / 255.0)
    
    
    # container for the 'Flowable' objects
    elements = []
    
    styleSheet = getSampleStyleSheet()
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
            P = Paragraph('<para align="center"><strong>%(meal_nr)s - %(meal_time)s</strong></para>' %
                        {'meal_nr': i,
                         'meal_time': meal.time.strftime("%H:%M")},
                      styleSheet["Normal"])
        data.append([P])
        
        # Ingredients
        for item in meal.mealitem_set.select_related():
            ingredient_markers.append(len(data))
            
            P = Paragraph('<para>%s</para>' % item.ingredient.name,
                          styleSheet["Normal"])
            data.append(["%sg" % item.amount_gramm, P])
    
    # Set general table styles
    table_style = [
                    #('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                    #('BOX', (0,0), (-1,-1), 0.25, colors.black)
                    ]
    
    # Set specific styles, e.g. background for title cells
    previous_marker = 0
    for marker in meal_markers:
        # Set background colour for headings
        table_style.append(('BACKGROUND', (0, marker), (-1, marker), header_colour))
        table_style.append(('BOX', (0, marker), (-1, marker), 1.25, colors.black))
        
        # Make the headings span the whole width
        table_style.append(('SPAN', (0, marker), (-1, marker)))

    
    t = Table(data, style = table_style)
    
    # Manually set the width of the columns
    t._argW[0] = 2 * cm


    # Set the title (if available)
    if plan.description:
        P = Paragraph('<para align="center"><strong>%(description)s</strong></para>' %
                                            {'description' : plan.description},
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
    P = Paragraph('<para align="left">%(date)s - %(created)s v%(version)s</para>' %
                    {'date' : _("Created on the <b>%s</b>") % plan.creation_date.strftime("%d.%m.%Y"),
                     'created' : "Workout Manager",
                     'version': get_version()},
                  styleSheet["Normal"])
    elements.append(P)
    
    doc.build(elements)

    return response


# ************************
# Meal functions
# ************************

class MealForm(ModelForm):
    class Meta:
        model = Meal
        exclude=('plan', 'order')

class MealItemForm(ModelForm):
    class Meta:
        model = MealItem
        exclude=('meal', 'order')


class MealCreateView(YamlFormMixin, CreateView):
    """
    Generic view to add a new meal to a nutrition plan
    """
    
    active_tab = NUTRITION_TAB
    model = Meal
    form_class = MealForm
    title = ugettext_lazy('Add new meal')
    owner_object = {'pk': 'plan_pk', 'class': NutritionPlan}
    
    def form_valid(self, form):
        plan = get_object_or_404(NutritionPlan, pk = self.kwargs['plan_pk'], user=self.request.user)
        form.instance.plan = plan
        form.instance.order = 1
        return super(MealCreateView, self).form_valid(form)
    
    def get_success_url(self):
        return reverse('nutrition.views.view', kwargs ={'id': self.object.plan.id})

    # Send some additional data to the template
    def get_context_data(self, **kwargs):
        context = super(MealCreateView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('meal-add',
                                         kwargs={'plan_pk': self.kwargs['plan_pk']})
         
        return context


class MealEditView(YamlFormMixin, UpdateView):
    """
    Generic view to update an existing meal
    """
    
    active_tab = NUTRITION_TAB
    model = Meal
    form_class = MealForm
    title = ugettext_lazy('Edit meal')
    form_action_urlname = 'meal-edit'
 
    def get_success_url(self):
        return reverse('nutrition.views.view', kwargs ={'id': self.object.plan.id})

   
@login_required
def delete_meal(request, id):
    """Deletes the meal with the given ID
    """
    
    # Load the meal
    meal = get_object_or_404(Meal, pk=id)
    plan = meal.plan
    
    # Only delete if the user is the owner
    if plan.user == request.user:
        meal.delete()
        return HttpResponseRedirect(reverse('nutrition.views.view', kwargs= {'id': plan.id}))
    else:
        return HttpResponseForbidden()



# ************************
# Meal ingredient functions
# ************************

@login_required
def delete_meal_item(request, item_id):
    """Deletes the meal ingredient with the given ID
    """
    
    # Load the item
    item = get_object_or_404(MealItem, pk=item_id)
    plan = item.meal.plan
    
    # Only delete if the user is the owner
    if plan.user == request.user:
        item.delete()
        return HttpResponseRedirect(reverse('nutrition.views.view', kwargs= {'id': plan.id}))
    else:
        return HttpResponseForbidden()

@login_required
def edit_meal_item(request, id, meal_id, item_id=None):
    """Form to add a meal to a plan
    """
    template_data = {}
    template_data['active_tab'] = NUTRITION_TAB
    
    # Load the plan
    plan = get_object_or_404(NutritionPlan, pk=id, user=request.user)
    template_data['plan'] = plan
    
    # Load the meal
    meal = get_object_or_404(Meal, pk=meal_id)
    template_data['meal'] = meal
    
    if meal.plan != plan:
        return HttpResponseForbidden()
    
    
    # Load the meal item
    # If the object is new, we will receice a 'None' (string) as the ID
    # from the template, so we check for it (ValueError) and for an actual
    # None (TypeError)
    try:
        int(item_id)
        meal_item = get_object_or_404(MealItem, pk=item_id)
        template_data['ingredient'] = meal_item.ingredient.id
        template_data['ingredient_searchfield'] = meal_item.ingredient.name
        
    except ValueError, TypeError:
        meal_item = MealItem()

    template_data['meal_item'] = meal_item
    
    # Check that javascript is activated This is used to hide the drop down list with the
    # ingredients and use the autocompleter version instead. This is not only nicer but also much
    # faster as the ingredient list from USDA is many thosand entries long.
    js_active = request.GET.get('js', False)
    template_data['js_active'] = js_active
    
    
    # Process request
    if request.method == 'POST':
        meal_form = MealItemForm(request.POST, instance=meal_item)
        
        # Pass the ingredient ID back to the template, this is originally set by the JQuery
        # autocompleter, in case of errors (max. gramms reached), we need to set the ID manually
        # so the user can simply submit again.
        template_data['ingredient'] = request.POST.get('ingredient', '')
        
        template_data['ingredient_searchfield'] = request.POST.get('ingredient_searchfield', '')
        
        
        # If the data is valid, save and redirect
        if meal_form.is_valid():
            meal_item = meal_form.save(commit=False)
            meal_item.meal = meal
            meal_item.order = 1
            meal_item.save()
            
            return HttpResponseRedirect(reverse('nutrition.views.view', kwargs= {'id': id}))
        
    else:
        meal_form = MealItemForm(instance=meal_item)
    template_data['form'] = meal_form
    
    return render_to_response('edit_meal_item.html', 
                              template_data,
                              context_instance=RequestContext(request))

# ************************
# Ingredient functions
# ************************
def ingredient_overview(request):
    """Show an overview of all ingredients
    """
    
    template_data = {}
    template_data['active_tab'] = NUTRITION_TAB
    
    # Filter the ingredients the user will see by its language
    # (the user can also want to see ingredients in English, see load_ingredient_languages)
    languages = load_ingredient_languages(request)
            
    # Load the ingredients
    ingredients_list  = Ingredient.objects.filter(language__in = languages)
    
    # Show 25 ingredients per page
    paginator = Paginator(ingredients_list, 25)
    page = request.GET.get('page')
    try:
        ingredients = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        ingredients = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        ingredients = paginator.page(paginator.num_pages)
    
    template_data['ingredients'] = ingredients
    
    return render_to_response('ingredient_overview.html',
                              template_data,
                              context_instance=RequestContext(request))
    
def ingredient_view(request, id):
    template_data = {}
    template_data['active_tab'] = NUTRITION_TAB
    
    ingredient = get_object_or_404(Ingredient, pk=id)
    template_data['ingredient'] = ingredient
    
    return render_to_response('view_ingredient.html', 
                              template_data,
                              context_instance=RequestContext(request))


class IngredientForm(ModelForm):
    class Meta:
        model = Ingredient
        exclude=('language',)


class IngredientDeleteView(YamlDeleteMixin, DeleteView):
    """
    Generic view to delete an existing ingredient
    """
    
    model = Ingredient
    template_name = 'delete.html'
    success_url = reverse_lazy('nutrition.views.ingredient_overview')
    
    
    # Send some additional data to the template
    def get_context_data(self, **kwargs):
        context = super(IngredientDeleteView, self).get_context_data(**kwargs)
        
        context['title'] = _('Delete %s?') % self.object.name
        context['form_action'] = reverse('ingredient-delete', kwargs={'pk': self.kwargs['pk']})
    
        return context


class IngredientEditView(YamlFormMixin, UpdateView):
    """
    Generic view to update an existing ingredient
    """
    
    active_tab = NUTRITION_TAB
    model = Ingredient
    form_class = IngredientForm
    title = ugettext_lazy('Add a new ingredient')
    form_action_urlname = 'ingredient-edit'


class IngredientCreateView(YamlFormMixin, CreateView):    
    """
    Generic view to add a new ingredient
    """
    
    active_tab = NUTRITION_TAB
    model = Ingredient
    form_class = IngredientForm
    title = ugettext_lazy('Add a new ingredient')
    form_action = reverse_lazy('ingredient-add')
    
    def form_valid(self, form):
        form.instance.language = load_language()
        return super(IngredientCreateView, self).form_valid(form)



def ingredient_search(request):
    """Search for an exercise, return the result as a JSON list or as HTML page, depending on how
    the function was invoked
    """
    # Filter the ingredients the user will see by its language
    # (the user can also want to see ingredients in English, see load_ingredient_languages)
    languages = load_ingredient_languages(request)
    
    # Perform the search
    q = request.GET.get('term', '')
    ingredients = Ingredient.objects.filter(name__icontains = q, language__in = languages)
    
    # AJAX-request, this comes from the autocompleter. Create a list and send it back as JSON
    if request.is_ajax():
        
        results = []
        for ingredient in ingredients:
            ingredient_json = {}
            ingredient_json['id'] = ingredient.id
            ingredient_json['name'] = ingredient.name
            ingredient_json['value'] = ingredient.name
            results.append(ingredient_json)
        data = json.dumps(results)
        
        # Return the results to the server
        mimetype = 'application/json'
        return HttpResponse(data, mimetype)
    
    # Usual search (perhaps JS disabled), present the results as normal HTML page
    else:
        template_data = {}
        template_data.update(csrf(request))
        template_data['ingredients'] = ingredients
        template_data['search_term'] = q
        return render_to_response('ingredient_search.html',
                                  template_data,
                                  context_instance=RequestContext(request))
