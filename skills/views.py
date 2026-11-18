from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST, require_http_methods
from .forms import LoginForm, RegisterForm, ReviewForm, SkillForm
from .models import Review, Skill


@require_http_methods(['GET'])
def skill_list(request):
    # GET keeps searches bookmarkable. Q combines the two matches with OR.
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    skills = Skill.objects.select_related('owner').annotate(average_rating=Avg('reviews__rating'), review_count=Count('reviews')).order_by('-created_at', '-pk')
    if query:
        skills = skills.filter(Q(title__icontains=query) | Q(category__icontains=query))
    if category:
        skills = skills.filter(category=category)
    page = Paginator(skills, 9).get_page(request.GET.get('page'))
    return render(request, 'skills/skill_list.html', {'page_obj': page, 'query': query, 'category': category, 'categories': Skill.Category.choices})


@require_http_methods(['GET', 'POST'])
def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = RegisterForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Welcome to Campus SkillSwap! Share your first skill.')
        return redirect('dashboard')
    return render(request, 'registration/register.html', {'form': form})


@require_http_methods(['GET', 'POST'])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request, data=request.POST if request.method == 'POST' else None)
    next_url = request.POST.get('next', request.GET.get('next', ''))
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
            return redirect(next_url)
        return redirect('dashboard')
    return render(request, 'registration/login.html', {'form': form, 'next': next_url})


@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, 'You have signed out.')
    return redirect('skill_list')


@login_required
@require_http_methods(['GET'])
def dashboard(request):
    skills = request.user.skills.annotate(average_rating=Avg('reviews__rating'), review_count=Count('reviews'))
    return render(request, 'skills/dashboard.html', {'skills': skills})


@require_http_methods(['GET', 'POST'])
def skill_detail(request, pk):
    skill = get_object_or_404(Skill.objects.select_related('owner'), pk=pk)
    own_review = skill.reviews.filter(author=request.user).first() if request.user.is_authenticated else None
    form = ReviewForm(instance=own_review)
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect(f"/accounts/login/?next={skill.get_absolute_url()}")
        if request.user == skill.owner:
            messages.error(request, 'You cannot review your own skill.')
            return redirect(skill)
        # Fix skill and author before validation; never accept these from the browser.
        review = own_review or Review(skill=skill, author=request.user)
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your review has been saved.')
            return redirect(skill)
    reviews = skill.reviews.select_related('author')
    return render(request, 'skills/skill_detail.html', {'skill': skill, 'reviews': reviews, 'average_rating': reviews.aggregate(value=Avg('rating'))['value'], 'form': form, 'own_review': own_review})


@login_required
@require_http_methods(['GET', 'POST'])
def skill_create(request):
    form = SkillForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        skill = form.save(commit=False)
        skill.owner = request.user
        skill.save()
        messages.success(request, 'Your skill is now live!')
        return redirect(skill)
    return render(request, 'skills/skill_form.html', {'form': form, 'heading': 'Share your skill'})


@login_required
@require_http_methods(['GET', 'POST'])
def skill_edit(request, pk):
    skill = get_object_or_404(Skill, pk=pk, owner=request.user)
    form = SkillForm(request.POST if request.method == 'POST' else None, instance=skill)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Your skill has been updated.')
        return redirect(skill)
    return render(request, 'skills/skill_form.html', {'form': form, 'heading': 'Edit your skill', 'skill': skill})


@login_required
@require_http_methods(['GET', 'POST'])
def skill_delete(request, pk):
    skill = get_object_or_404(Skill, pk=pk, owner=request.user)
    if request.method == 'POST':
        skill.delete()
        messages.success(request, 'Your skill and its reviews have been deleted.')
        return redirect('dashboard')
    return render(request, 'skills/skill_confirm_delete.html', {'skill': skill})


@login_required
@require_POST
def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk, author=request.user)
    skill = review.skill
    review.delete()
    messages.success(request, 'Your review has been deleted.')
    return redirect(skill)
