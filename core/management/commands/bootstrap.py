import os
import json
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group

from cms.models import PageContent, Placeholder 
from cms.api import add_plugin, assign_user_to_page, create_page, publish_page
from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
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
        admin = factories.UserFactory(is_staff=True, is_superuser=True, 
            username="admin", email="admin@admin.com", password="admin")

        # create users, groups and roles
        user = factories.UserFactory(username='test', email='test@test.com', password='test', is_staff=True,)
        user2 = factories.UserFactory(username='test2', email='test2@test.com', password='test2', is_staff=True, is_superuser=True,)
        user3 = factories.UserFactory(username='test3', email='test3@test.com', password='test3', is_staff=True, is_superuser=True,)
        moderator = factories.UserFactory(username='moderator', email='moderator@test.com', password='moderator', is_staff=True, )
        reviewer = factories.UserFactory(username='reviewer', email='reviewer@test.com', password='reviewer', is_staff=True, )
        artworker = factories.UserFactory(username='artworker', email='artworker@test.com', password='artworker', is_staff=True, )

        # add permissions
        content_type = ContentType.objects.get_for_model(ModerationCollection)
        permission = Permission.objects.get(content_type=content_type, codename='can_change_author')
        user.user_permissions.add(permission)
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(content_type=content_type, codename='change_moderationcollection')
        user.user_permissions.add(permission)
        moderator.user_permissions.add(permission)
        reviewer.user_permissions.add(permission)
        permission = Permission.objects.get(content_type=content_type, codename='add_moderationcollection')
        user.user_permissions.add(permission)
        moderator.user_permissions.add(permission)
        content_type = ContentType.objects.get_for_model(ModerationRequest)
        permission = Permission.objects.get(content_type=content_type, codename='change_moderationrequest')
        user.user_permissions.add(permission)
        moderator.user_permissions.add(permission)
        reviewer.user_permissions.add(permission)
        permission = Permission.objects.get(content_type=content_type, codename='add_moderationrequest')
        user.user_permissions.add(permission)
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='use_structure')
        moderator.user_permissions.add(permission)
        reviewer.user_permissions.add(permission)
        permission = Permission.objects.get(codename='add_staticplaceholder')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='change_staticplaceholder')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='delete_staticplaceholder')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='add_cmsplugin')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='change_cmsplugin')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='delete_cmsplugin')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='add_page')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='delete_page')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='view_page')
        moderator.user_permissions.add(permission)
        reviewer.user_permissions.add(permission)
        permission = Permission.objects.get(codename='change_page')
        moderator.user_permissions.add(permission)
        reviewer.user_permissions.add(permission)
        permission = Permission.objects.get(codename='publish_page')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='edit_static_placeholder')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='add_aliaspluginmodel')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='change_aliaspluginmodel')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='delete_aliaspluginmodel')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='add_text')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='change_text')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='delete_text')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='add_textareafieldplugin')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='change_textareafieldplugin')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='delete_textareafieldplugin')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='add_image')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='change_image')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='delete_image')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='add_link')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='change_link')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='delete_link')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='add_style')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='change_style')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='delete_style')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='add_snippet')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='change_snippet')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='delete_snippet')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='add_version')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='change_version')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='delete_version')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='add_pagecontentversion')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='change_pagecontentversion')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='delete_pagecontentversion')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='add_versionlock')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='change_versionlock')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='delete_versionlock')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='add_moderationrequest')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='change_moderationrequest')
        moderator.user_permissions.add(permission)
        reviewer.user_permissions.add(permission)
        permission = Permission.objects.get(codename='delete_moderationrequest')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='add_moderationrequestaction')
        moderator.user_permissions.add(permission)
        reviewer.user_permissions.add(permission)
        permission = Permission.objects.get(codename='change_moderationrequestaction')
        moderator.user_permissions.add(permission)
        reviewer.user_permissions.add(permission)
        permission = Permission.objects.get(codename='delete_moderationrequestaction')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='add_workflow')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='change_workflow')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='delete_workflow')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='add_collectioncomment')
        moderator.user_permissions.add(permission)
        reviewer.user_permissions.add(permission)
        permission = Permission.objects.get(codename='change_collectioncomment')
        moderator.user_permissions.add(permission)
        reviewer.user_permissions.add(permission)
        permission = Permission.objects.get(codename='delete_collectioncomment')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='add_confirmationformsubmission')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='change_confirmationformsubmission')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='delete_confirmationformsubmission')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='add_moderationform')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='change_moderationform')
        moderator.user_permissions.add(permission)
        permission = Permission.objects.get(codename='delete_moderationform')
        moderator.user_permissions.add(permission)

        # create pages
        self.create_homepage(admin)
        pg1 = create_page(title='Page 1', template='INHERIT', language='en', created_by=user, )
        pg2 = create_page(title='Page 2', template='INHERIT', language='en', created_by=user2, )
        pg3 = create_page(title='Page 3', template='INHERIT', language='en', created_by=user3, )
        pg4 = create_page(title='Page 4', template='INHERIT', language='en', created_by=user,)
        pg5 = create_page(title='Page 5', template='INHERIT', language='en', created_by=moderator,)
        assign_user_to_page(pg5, moderator, can_view=True,
                            can_change=True)
        assign_user_to_page(pg5, reviewer, can_view=True,
                            can_change=False)
        assign_user_to_page(pg5, artworker, can_view=True,
                            can_change=True)

        group = Group.objects.create(name='Group 1',)
        group2 = Group.objects.create(name='Moderator',)
        group3 = Group.objects.create(name='Reviewer',)
        group4 = Group.objects.create(name='Artworker',)
        user2.groups.add(group)
        user3.groups.add(group)
        moderator.groups.add(group2)
        reviewer.groups.add(group3)
        artworker.groups.add(group4)

        role1 = Role.objects.create(name='Role 1', user=user,)
        role2 = Role.objects.create(name='Role 2', user=user2,)
        role3 = Role.objects.create(name='Role 3', group=group,)
        role4 = Role.objects.create(name='Moderator', group=group2,)
        role5 = Role.objects.create(name='Reviewer', group=group3,)
        role6 = Role.objects.create(name='Artworker', group=group4,)

        # create workflows
        wf1 = Workflow.objects.create(pk=1, name='Workflow 1', is_default=True,)
        wf2 = Workflow.objects.create(pk=2, name='Workflow 2',)
        wf3 = Workflow.objects.create(pk=3, name='Workflow 3',)
        wf4 = Workflow.objects.create(pk=4, name='NCO',)

        # create versions
        v1 = Version.objects.filter_by_grouper(pg1).filter(state=DRAFT).first()
        v2 = Version.objects.filter_by_grouper(pg2).filter(state=DRAFT).first()
        v3 = Version.objects.filter_by_grouper(pg3).filter(state=DRAFT).first()
        v4 = Version.objects.filter_by_grouper(pg4).filter(state=DRAFT).first()
        v5 = Version.objects.filter_by_grouper(pg5).filter(state=DRAFT).first()

        # create workflow steps for workflow
        wf1st1 = wf1.steps.create(role=role1, is_required=True, order=1,)
        wf1st2 = wf1.steps.create(role=role2, is_required=False, order=2,)
        wf1st3 = wf1.steps.create(role=role3, is_required=True, order=3,)

        wf2st1 = wf2.steps.create(role=role1, is_required=True, order=1,)
        wf2st2 = wf2.steps.create(role=role3, is_required=True, order=2,)

        wf3st1 = wf3.steps.create(role=role1, is_required=True, order=1,)
        wf3st2 = wf3.steps.create(role=role3, is_required=False, order=2,)

        wf4st1 = wf4.steps.create(role=role5, is_required=True, order=1,)

        # create collections
        # collection 1  (v1 by user, v2 by user2)->
        #   workflow 1 ->
        #       step_role_1 (user) >>
        #       step_role_2 (user2) >>
        #       step_role_3 (user2 and user3) >>
        #

        collection1 = ModerationCollection.objects.create(
            author=user, name='Collection 1', workflow=wf1
        )
        collection2 = ModerationCollection.objects.create(
            author=user2, name='Collection 2', workflow=wf2
        )
        collection3 = ModerationCollection.objects.create(
            author=moderator, name='Collection for review', workflow=wf4
        )

        # add each version to the collection
        collection1.add_version(v1)
        collection1.add_version(v2)
        collection2.add_version(v3)
        collection2.add_version(v4)
        collection3.add_version(v5)

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
        page = create_page(title=_('Home'), template=template, language=lang, created_by=user,)

        # page = create_page(_('Home'), template, lang, user)
        page.set_as_homepage()

        # create version
        v5 = Version.objects.filter_by_grouper(page).filter(state=DRAFT).first()
        v5.publish(user)
        placeholder['main'] = v5.content.get_placeholders().get(slot='content')

        try:
            # try to get a feature placeholder
            placeholder_feature = v5.content.get_placeholders().get(slot='feature')
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
