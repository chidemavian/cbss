import os, sys  
sys.path.append('C:\Users\CCL\Desktop\Salvation Army/')
sys.path.append('C:\Users\CCL\Desktop\Salvation Army')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'  
import django.core.handlers.wsgi  
application = django.core.handlers.wsgi.WSGIHandler()  
