import os
import json
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group

from cms.models import PageContent, Placeholder 
from cms.api import create_page, add_plugin, publish_page
from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from djangocms_versioning.models import Version
from djangocms_moderation.models import Workflow, Role, ModerationCollection, ModerationRequest
from djangocms_moderation import constants
from djangocms_versioning.constants import DRAFT, PUBLISHED
from djangocms_versioning.test_utils import factories


def create_page_version(pg, user, status=DRAFT):
    pg.set_translations_cache()
    content_obj = pg.get_title_obj('en')

    return Version.objects.create(
        content_type=ContentType.objects.get_for_model(PageContent),
        object_id=content_obj.pk,
        created_by_id=user.pk,
        state=status
    )


class Command(BaseCommand):
    help = 'Bootstrap Test project with sample user, rules, and content'

    def handle(self, *args, **options):
        self.stdout.write("Creating users, roles, and workflow")
        self.bootstrap()

    def bootstrap(self):
        """ Setup initial workflow, pages, users and roles for moderation

            From: https://github.com/divio/djangocms-moderation/blob/master/tests/utils.py 
        """

        # create admin user
        admin = factories.UserFactory(is_staff=True, is_superuser=True, username="admin", email="admin@admin.com", password="admin")

        # create users, groups and roles
        user = factories.UserFactory(username='test', email='test@test.com', password='test')
        user2 = factories.UserFactory(username='test2', email='test2@test.com', password='test2')
        user3 = factories.UserFactory(username='test3', email='test3@test.com', password='test3')

        group = Group.objects.create(name='Group 1',)
        user2.groups.add(group)
        user3.groups.add(group)

        role1 = Role.objects.create(name='Role 1', user=user,)
        role2 = Role.objects.create(name='Role 2', user=user2,)
        role3 = Role.objects.create(name='Role 3', group=group,)

        # create workflows
        wf1 = Workflow.objects.create(pk=1, name='Workflow 1', is_default=True,)
        wf2 = Workflow.objects.create(pk=2, name='Workflow 2',)
        wf3 = Workflow.objects.create(pk=3, name='Workflow 3',)

        # create pages
        self.create_homepage(user)
        pg1 = create_page(title='Page 1', template='INHERIT', language='en',)
        pg2 = create_page(title='Page 2', template='INHERIT', language='en',)
        pg3 = create_page(title='Page 3', template='INHERIT', language='en',)
        pg4 = create_page(title='Page 4', template='INHERIT', language='en',)

        # create versions
        v1 = create_page_version(pg1, user, DRAFT)
        v2 = create_page_version(pg2, user2, DRAFT)
        v3 = create_page_version(pg3, user3, DRAFT)
        v4 = create_page_version(pg4, user, DRAFT)

        # create workflow steps for workflow
        wf1st1 = wf1.steps.create(role=role1, is_required=True, order=1,)
        wf1st2 = wf1.steps.create(role=role2, is_required=False, order=2,)
        wf1st3 = wf1.steps.create(role=role3, is_required=True, order=3,)

        wf2st1 = wf2.steps.create(role=role1, is_required=True, order=1,)
        wf2st2 = wf2.steps.create(role=role3, is_required=True, order=2,)

        wf3st1 = wf3.steps.create(role=role1, is_required=True, order=1,)
        wf3st2 = wf3.steps.create(role=role3, is_required=False, order=2,)

        # create collections
        collection1 = ModerationCollection.objects.create(
            author=user, name='Collection 1', workflow=wf1
        )
        collection2 = ModerationCollection.objects.create(
            author=user2, name='Collection 2', workflow=wf2
        )

        # add each version to the collection
        collection1.add_version(v1)
        collection1.add_version(v2)
        collection2.add_version(v3)
        collection2.add_version(v4)

    def create_homepage(self, user):
        """
            Create the home page for a blank django cms install
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
        page = create_page(_('Home'), template, lang)
        page.set_as_homepage()

        # create version
        create_page_version(page, user, PUBLISHED)

        placeholder['main'] = page.get_placeholders('en').get(slot='content')

        try:
            # try to get a feature placeholder
            placeholder_feature = page.get_placeholders('en').get(slot='feature')
            add_plugin(
                placeholder_feature,
                'TextPlugin', lang,
                body=content['feature']
            )
        except Placeholder.DoesNotExist:
            # fallback, add it to the
            add_plugin(placeholder['main'], 'TextPlugin', lang, body=content['feature'])

        # Add main content to a MultiColumnPlugin
        multi_columns_plugin = add_plugin(placeholder['main'], 'MultiColumnPlugin', lang)
        for column_content in content['main']:
            col = add_plugin(
                placeholder['main'],
                'ColumnPlugin',
                lang,
                target=multi_columns_plugin, **{'width': '33%'}
            )
            add_plugin(
                placeholder['main'],
                'TextPlugin',
                lang,
                body=column_content,
                target=col
            )
