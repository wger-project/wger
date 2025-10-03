# Django
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

# Local
from ..forms import CustomExerciseForm
from ..models import CustomExercise


@login_required
def custom_exercise_list(request):
    items = CustomExercise.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'exercises/custom_list.html', {'exercises': items})


@login_required
def custom_exercise_create(request):
    if request.method == 'POST':
        form = CustomExerciseForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            form.save_m2m()
            return redirect('exercise:custom_exercise_list')
    else:
        form = CustomExerciseForm()
    return render(request, 'exercises/custom_form.html', {'form': form})


@login_required
def custom_exercise_edit(request, pk):
    obj = get_object_or_404(CustomExercise, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CustomExerciseForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('exercise:custom_exercise_list')
    else:
        form = CustomExerciseForm(instance=obj)
    return render(request, 'exercises/custom_form.html', {'form': form, 'obj': obj})


@login_required
def custom_exercise_delete(request, pk):
    obj = get_object_or_404(CustomExercise, pk=pk, user=request.user)
    if request.method == 'POST':
        obj.delete()
        return redirect('exercise:custom_exercise_list')
    return render(request, 'exercises/custom_confirm_delete.html', {'obj': obj})
