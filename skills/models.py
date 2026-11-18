from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse


class Skill(models.Model):
    class Category(models.TextChoices):
        TUTORING = 'Tutoring', 'Tutoring'
        TECH = 'Technology', 'Technology'
        DESIGN = 'Design', 'Design & Creative'
        LANGUAGES = 'Languages', 'Languages'
        MUSIC = 'Music', 'Music'
        FITNESS = 'Fitness', 'Fitness & Wellness'
        OTHER = 'Other', 'Other'

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='skills')
    title = models.CharField(max_length=120)
    category = models.CharField(max_length=20, choices=Category.choices)
    description = models.TextField(max_length=5000)
    exchange = models.CharField(max_length=150, help_text='Example: $15/hour, free, or trade for guitar lessons.')
    location = models.CharField(max_length=120, help_text='Example: Library, campus cafe, or online.')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at', '-pk']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('skill_detail', args=[self.pk])


class Review(models.Model):
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at', '-pk']
        constraints = [
            models.UniqueConstraint(fields=['skill', 'author'], name='one_review_per_student'),
            models.CheckConstraint(condition=models.Q(rating__gte=1, rating__lte=5), name='rating_between_1_and_5'),
        ]

    def clean(self):
        super().clean()
        if self.skill_id and self.author_id and self.skill.owner_id == self.author_id:
            raise ValidationError('You cannot review your own skill.')

    def __str__(self):
        return f'{self.author} — {self.skill} ({self.rating}/5)'
