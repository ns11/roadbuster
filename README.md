*********************
Roadbuster
*********************

Overview
============
A lightweight django project with helper management commands to speed up djangocms development/test workflow (especially django_moderation).


Extras
---------
1) settings.py has all the necessary setups in INSTALLED_APP
2) django-su is installed, allowing us to switch easily between admin users


Prerequisites
============
Elastic search needs to be installed. Visit http://127.0.0.1:9200/ to confirm it is installed and configured correctly.


Installation & Setup
============

This assumes you have a python virtual environment setup with djangocms installed. If not run:

```
    mkvirtualenv roadbuster
    pip install -r dev_requirements.txt
```

Then, pip install the plugin/application under test/development (e.g django_moderation) using ```pip -e <path_to_plugin>```


Usage
==========

1) To reset you database and re-populate it with CMS Pages and Moderation Workflows run the management command:

``` 
    python manage.py reload_db
```

2) To drop the DB and refresh it to a brand new blank database. The reload_db command will also need to be ran manually.
``` 
    python manage.py drop_db
```

3) One way to use roadbuster with a package you're currently working on is:
   ```
       pip uninstall <package_name>
       python path/to/package/setup.py develop
   ```
   And then when you're done:
   ```
      python path/to/package/setup.py develop --uninstall
      pip install -r dev_requirements.txt
   ```

Contribution
=============

Please add more management commands as you see fit.
