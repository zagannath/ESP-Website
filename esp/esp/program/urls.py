from django.conf.urls.defaults import *

urlpatterns = patterns('',
                       # manage stuff
                       (r'^manage/programs/?$', 'esp.program.views.manage_programs'),
                       (r'^manage/newprogram/?$', 'esp.program.views.newprogram'),
                       (r'^manage/submit_transaction/?$', 'esp.program.views.submit_transaction'),
                       (r'^manage/pages/?$', 'esp.program.views.manage_pages'),
                       (r'^manage/userview/?$', 'esp.program.views.userview'),
                       (r'^manage/usersearch/?$', 'esp.program.views.usersearch'),                       
                       (r'^manage/flushcache/?$', 'esp.program.views.flushcache'),
                       (r'^manage/statistics/?$', 'esp.program.views.statistics'),
                       (r'^manage/preview/?$', 'esp.program.views.template_preview'),
                       (r'^manage/mergeaccounts/?$', 'esp.users.views.merge.merge_accounts'),
                       )

# temporary redirects for Junction 2012
from django.shortcuts import redirect
urlpatterns += patterns('',
                        (r'^learn/Junction/2012/archae/?$', lambda r: redirect('/mahara/view/view.php?t=HXo8cqOKyset4ALNhGbM')),
                        (r'^learn/Junction/2012/biooc/?$', lambda r: redirect('/mahara/view/view.php?t=xfGjThwM42WAiyUqLQ5R')),
                        (r'^learn/Junction/2012/neuro/?$', lambda r: redirect('/mahara/view/view.php?t=4X7wrRPZeC8buNpGVogY')),
                        (r'^learn/Junction/2012/proteins/?$', lambda r: redirect('/mahara/view/view.php?t=QMfstlieXkJ0SjpDh9ma')),
                        (r'^learn/Junction/2012/plato/?$', lambda r: redirect('/mahara/view/view.php?t=FYXAyDd3OUmcvTwt71Eb')),
                        (r'^learn/Junction/2012/chelsea/?$', lambda r: redirect('/mahara/view/view.php?t=1ZoTfg5V2BLHnzYyhAux')),
                        )
