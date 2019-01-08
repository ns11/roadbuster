from cms.exceptions import SubClassNeededError

from .models import PageExtension, TitleExtension


class ExtensionPool(object):
    def __init__(self):
        self.page_extensions = set()
        self.title_extensions = set()

    def register(self, extension):
        """
        Registers the given extension.

        Example::

            class MyExtension(PageExtension):
                pass

            extension_pool.register(MyExtension)

        or as decorator::

            @extension_pool.register
            class MyExtension(PageExtension):
                pass

        """

        if issubclass(extension, PageExtension):
            self.page_extensions.add(extension)
        elif issubclass(extension, TitleExtension):
            self.title_extensions.add(extension)
        else:
            raise SubClassNeededError(
                'Extension has to subclass either %r or %r. %r does not!' % (PageExtension, TitleExtension, extension)
            )
        return extension

    def unregister(self, extension):
        """
        Unregisters the given extension. No error is thrown if given extension isn't an extension or wasn't
        registered yet.
        """

        try:
            if issubclass(extension, PageExtension):
                self.page_extensions.remove(extension)
            elif issubclass(extension, TitleExtension):
                self.title_extensions.remove(extension)
        except KeyError:
            pass

    def _copy_page_extensions(self, source_page, target_page, language, clone=False):
        for extension in self.page_extensions:
            for instance in extension.objects.filter(extended_object=source_page):
                if clone:
                    instance.copy(target_page, language)
                else:
                    instance.copy_to_public(target_page, language)

    def _copy_title_extensions(self, source_page, target_page, language, clone=False):
        source_title = source_page.pagecontent_set.get(language=language)
        if target_page:
            target_title = target_page.pagecontent_set.get(language=language)
        else:
            target_title = source_title.publisher_public
        for extension in self.title_extensions:
            for instance in extension.objects.filter(extended_object=source_title):
                if clone:
                    instance.copy(target_title, language)
                else:
                    instance.copy_to_public(target_title, language)

    def copy_extensions(self, source_page, target_page, languages=None):
        if not languages:
            languages = target_page.get_languages()
        if self.page_extensions:
            self._copy_page_extensions(source_page, target_page, None, clone=True)
        for language in languages:
            if self.title_extensions:
                self._copy_title_extensions(source_page, target_page, language, clone=True)

    def get_page_extensions(self, page=None):
        extensions = []
        for extension in self.page_extensions:
            if page:
                extensions.extend(list(extension.objects.filter(extended_object=page)))
            else:
                extensions.extend(list(extension.objects.all()))
        return extensions

    def get_title_extensions(self, title=None):
        extensions = []
        for extension in self.title_extensions:
            if title:
                extensions.extend(list(extension.objects.filter(extended_object=title)))
            else:
                extensions.extend(list(extension.objects.all()))
        return extensions

extension_pool = ExtensionPool()
