import os
import json
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group

from cms.models import Placeholder
from cms.api import create_page, add_plugin, publish_page
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from djangocms_moderation.models import Workflow, Role, ModerationCollection
from djangocms_moderation import constants


class Command(BaseCommand):
    help = 'Bootstrap Test project with sample user, rules, and content'

    def handle(self, *args, **options):
        self.stdout.write("Creating users, roles, and workflow")
        self.bootstrap()
        self.create_pages()
        

    def bootstrap(self):
        """ Setup initial workflow, pages, users and roles for moderation

            From: https://github.com/divio/djangocms-moderation/blob/master/tests/utils.py 
        """
        wf1 = Workflow.objects.create(pk=1, name='Workflow 1', is_default=True,)
        wf2 = Workflow.objects.create(pk=2, name='Workflow 2',)
        wf3 = Workflow.objects.create(pk=3, name='Workflow 3',)

        # create pages
        pg1 = create_page(title='Page 1', template='INHERIT', language='en',)
        pg2 = create_page(title='Page 2', template='INHERIT', language='en',)
        pg3 = create_page(title='Page 3', template='INHERIT', language='en', published=True)
        pg4 = create_page(title='Page 4', template='INHERIT', language='en',)

        # create users, groups and roles
        # create admin user
        User.objects.create_superuser('admin', 'admin@admin.com', 'admin', 
        is_staff=True, is_superuser=True)

        user = User.objects.create_superuser(
            username='test', email='test@test.com', password='test',)
        user2 = User.objects.create_superuser(
            username='test2', email='test2@test.com', password='test2',)
        user3 = User.objects.create_superuser(
            username='test3', email='test3@test.com', password='test3',)

        group = Group.objects.create(name='Group 1',)
        user2.groups.add(group)
        user3.groups.add(group)

        role1 = Role.objects.create(name='Role 1', user=user,)
        role2 = Role.objects.create(name='Role 2', user=user2,)
        role3 = Role.objects.create(name='Role 3', group=group,)

        # create workflow steps for workflow
        wf1st1 = wf1.steps.create(role=role1, is_required=True, order=1,)
        wf1st2 = wf1.steps.create(role=role2, is_required=False, order=2,)
        wf1st3 = wf1.steps.create(role=role3, is_required=True, order=3,)

        wf2st1 = wf2.steps.create(role=role1, is_required=True, order=1,)
        wf2st2 = wf2.steps.create(role=role3, is_required=True, order=2,)

        wf3st1 = wf3.steps.create(role=role1, is_required=True, order=1,)
        wf3st2 = wf3.steps.create(role=role3, is_required=False, order=2,)

        collection1 = ModerationCollection.objects.create(
            author=user, name='Collection 1', workflow=wf1
        )
        collection2 = ModerationCollection.objects.create(
            author=user2, name='Collection 2', workflow=wf2
        )

        collection1.add_object(pg1)
        collection1.add_object(pg2)

        collection2.add_object(pg3)
        collection2.add_object(pg4)




    def create_pages(self):
        """Create the home page for a blank django cms install
        
           From: https://github.com/nephila/djangocms-installer/blob/develop/djangocms_installer/share/starting_page.py#L8
        """


        placeholder = {}

        with open(os.path.join(os.path.dirname(__file__), 'starting_page.json')) as data_file:
            content = json.load(data_file)

        try:
            # try to get a feature template with fallback
            template = settings.CMS_TEMPLATES[1][0]
            if template != 'feature.html':
                template = settings.CMS_TEMPLATES[0][0]
        except IndexError:
            template = settings.CMS_TEMPLATES[0][0]

        lang = settings.LANGUAGES[0][0]
        page = create_page(_('Home'), template, lang, published=True)
        page.set_as_homepage()
        placeholder['main'] = page.placeholders.get(slot='content')

        try:
            # try to get a feature placeholder
            placeholder_feature = page.placeholders.get(slot='feature')
            add_plugin(placeholder_feature, 'TextPlugin', lang,
                    body=content['feature'])
        except Placeholder.DoesNotExist:
            # fallback, add it to the
            add_plugin(placeholder['main'], 'TextPlugin', lang, body=content['feature'])

        # Add main content to a MultiColumnPlugin
        multi_columns_plugin = add_plugin(placeholder['main'], 'MultiColumnPlugin', lang)
        for column_content in content['main']:
            col = add_plugin(placeholder['main'], 'ColumnPlugin', lang,
                            target=multi_columns_plugin, **{'width': '33%'})
            add_plugin(placeholder['main'], 'TextPlugin', lang, body=column_content,
                    target=col)

        # In order to publish the page there needs to be at least one user
        if User.objects.count() > 0:
            try:
                publish_page(page, User.objects.all()[0], lang)
            except TypeError:
                # supporting old cms versions
                publish_page(page, User.objects.all()[0])
