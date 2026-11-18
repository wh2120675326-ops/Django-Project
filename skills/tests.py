from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import Client, TestCase
from django.urls import reverse
from .models import Review, Skill


class MarketplaceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user('alex', password='CampusStrong!982')
        cls.student = User.objects.create_user('sam', password='CampusStrong!982')
        cls.skill = Skill.objects.create(owner=cls.owner, title='Python study buddy', category='Technology', description='Learn Python together.', exchange='Trade for music lessons', location='Library')

    def sign_in(self, owner=False):
        self.client.force_login(self.owner if owner else self.student)

    def test_public_list_detail_and_search(self):
        for query in ['', '?q=PYTHON', '?q=technology', '?q=%20Python%20', '?category=Technology']:
            response = self.client.get('/' + query)
            self.assertContains(response, self.skill.title)
        for query in ['?q=notfound', '?category=Music', '?q=Python&category=Music']:
            self.assertNotContains(self.client.get('/' + query), self.skill.title)
        self.assertContains(self.client.get(self.skill.get_absolute_url()), 'Learn Python together.')
        self.assertEqual(self.client.get('/skills/999/').status_code, 404)

    def test_register_login_logout(self):
        response = self.client.post(reverse('register'), {'username': 'newstudent', 'password1': 'UniqueCampus!934', 'password2': 'UniqueCampus!934'})
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(User.objects.get(username='newstudent').check_password('UniqueCampus!934'))
        self.assertEqual(self.client.get(reverse('logout')).status_code, 405)
        self.client.post(reverse('logout'))
        self.assertNotIn('_auth_user_id', self.client.session)
        response = self.client.post(reverse('login'), {'username': 'newstudent', 'password': 'UniqueCampus!934', 'next': 'https://evil.example/'})
        self.assertRedirects(response, reverse('dashboard'))

    def test_login_next_and_invalid_credentials(self):
        self.assertContains(self.client.post(reverse('login'), {'username': 'alex', 'password': 'wrong'}), 'Please enter a correct')
        response = self.client.post(reverse('login'), {'username': 'alex', 'password': 'CampusStrong!982', 'next': '/skills/new/'})
        self.assertRedirects(response, '/skills/new/')

    def test_private_routes_require_login(self):
        for url in ['/dashboard/', '/skills/new/', f'/skills/{self.skill.pk}/edit/', f'/skills/{self.skill.pk}/delete/']:
            self.assertEqual(self.client.get(url).status_code, 302)

    def test_skill_crud_and_dashboard(self):
        self.sign_in()
        data = {'title': 'Guitar basics', 'category': 'Music', 'description': 'Beginner lessons', 'exchange': 'Free', 'location': 'Online', 'owner': self.owner.pk}
        response = self.client.post(reverse('skill_create'), data)
        skill = Skill.objects.get(title='Guitar basics')
        self.assertEqual(skill.owner, self.student)
        self.assertRedirects(response, skill.get_absolute_url())
        dashboard = self.client.get(reverse('dashboard'))
        self.assertContains(dashboard, skill.title)
        self.assertNotContains(dashboard, self.skill.title)
        data['title'] = 'Guitar practice'
        self.client.post(reverse('skill_edit', args=[skill.pk]), data)
        skill.refresh_from_db()
        self.assertEqual(skill.title, 'Guitar practice')
        self.assertEqual(self.client.get(reverse('skill_delete', args=[skill.pk])).status_code, 200)
        self.assertTrue(Skill.objects.filter(pk=skill.pk).exists())
        self.client.post(reverse('skill_delete', args=[skill.pk]))
        self.assertFalse(Skill.objects.filter(pk=skill.pk).exists())

    def test_cannot_modify_other_students_post(self):
        self.sign_in()
        for name in ['skill_edit', 'skill_delete']:
            for method in [self.client.get, self.client.post]:
                self.assertEqual(method(reverse(name, args=[self.skill.pk])).status_code, 404)
        self.assertTrue(Skill.objects.filter(pk=self.skill.pk).exists())

    def test_skill_validation_and_form_pages(self):
        self.sign_in(owner=True)
        for url in ['/skills/new/', f'/skills/{self.skill.pk}/edit/', '/dashboard/']:
            self.assertEqual(self.client.get(url).status_code, 200)
        self.assertContains(self.client.post('/skills/new/', {}), 'This field is required.')
        self.assertEqual(Skill.objects.count(), 1)

    def test_review_create_update_average_delete(self):
        self.sign_in()
        url = self.skill.get_absolute_url()
        self.assertRedirects(self.client.post(url, {'rating': 5, 'comment': 'Helpful!'}), url)
        self.assertContains(self.client.get(url), '5.0 / 5')
        self.client.post(url, {'rating': 3, 'comment': 'Updated feedback'})
        self.assertEqual(Review.objects.count(), 1)
        review = Review.objects.get()
        self.assertEqual(review.rating, 3)
        self.assertContains(self.client.get(url), '3.0 / 5')
        delete_url = reverse('review_delete', args=[review.pk])
        self.assertEqual(self.client.get(delete_url).status_code, 405)
        self.client.post(delete_url)
        self.assertFalse(Review.objects.exists())

    def test_review_restrictions(self):
        self.client.post(self.skill.get_absolute_url(), {'rating': 5, 'comment': 'Guest'})
        self.assertFalse(Review.objects.exists())
        self.sign_in(owner=True)
        self.client.post(self.skill.get_absolute_url(), {'rating': 5, 'comment': 'Self'})
        self.assertFalse(Review.objects.exists())
        self.sign_in()
        for rating in [0, 6, 'abc', '']:
            self.assertEqual(self.client.post(self.skill.get_absolute_url(), {'rating': rating, 'comment': 'Bad rating'}).status_code, 200)
        self.client.post(self.skill.get_absolute_url(), {'rating': 5, 'comment': '   '})
        self.assertFalse(Review.objects.exists())

    def test_review_ownership_and_constraints(self):
        review = Review.objects.create(skill=self.skill, author=self.student, rating=4, comment='Good')
        self.sign_in(owner=True)
        self.assertEqual(self.client.post(reverse('review_delete', args=[review.pk])).status_code, 404)
        with self.assertRaises(ValidationError):
            Review(skill=self.skill, author=self.owner, rating=3, comment='Self').full_clean()
        for data in [{'author': self.student, 'rating': 5}, {'author': self.owner, 'rating': 6}]:
            with self.assertRaises(IntegrityError), transaction.atomic():
                Review.objects.create(skill=self.skill, comment='Invalid', **data)
        self.skill.delete()
        self.assertFalse(Review.objects.exists())

    def test_csrf_and_escaped_content(self):
        strict = Client(enforce_csrf_checks=True)
        strict.force_login(self.owner)
        self.assertEqual(strict.post(reverse('skill_create'), {}).status_code, 403)
        self.skill.description = '<script>alert(1)</script>'
        self.skill.save()
        response = self.client.get(self.skill.get_absolute_url())
        self.assertContains(response, '&lt;script&gt;')
        self.assertNotContains(response, '<script>alert(1)</script>')

    def test_pagination_keeps_query(self):
        for n in range(10):
            Skill.objects.create(owner=self.owner, title=f'Python {n}', category='Technology', description='Study', exchange='Free', location='Online')
        response = self.client.get('/?q=Python&category=Technology')
        self.assertEqual(len(response.context['page_obj']), 9)
        self.assertContains(response, 'q=Python&amp;category=Technology&amp;page=2')
        self.assertEqual(self.client.get('/?page=bad').status_code, 200)

    def test_admin_access(self):
        admin = User.objects.create_superuser('admin', password='AdminStrong!982')
        self.client.force_login(admin)
        for url in ['/admin/', '/admin/skills/skill/', '/admin/skills/review/']:
            self.assertEqual(self.client.get(url).status_code, 200)
