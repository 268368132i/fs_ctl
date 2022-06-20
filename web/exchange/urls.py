
from django.urls import path
from . import views
from .views import UploadAssetView

app_name='exchange'

urlpatterns = [
    path('getconf/', views.getConf,name='getConf'),
    path('confs/', views.confs, name='confs'),
    path('confs/tokenize', views.tokenize, name='tokenize'),
    path('confs/connect',views.connect, name='conf_connect'),
    path('confs/ctl?uuid=<uuid:uuid>',views.confControl, name='ctl'),
    path('confs/ctl_page?uuid=<uuid:assignment_id>',views.conf_ctl_page, name='conf_ctl_page'),
    path('confs/asset_upload',views.UploadAssetView.as_view(), name="upload_conf_asset"),
    path('confs/list_assets/<int:conf>', views.AssetsListView.as_view(), name="list_assets"),
    path('confs/delete_asset/<int:pk>', views.DeleteAssetView.as_view(), name="delete_asset"),
    path('confs/new_ctl?uuid=<uuid:uuid>',views.new_ctl, name='new_ctl'),
    path('confs/<int:conf>/recordings/', views.recordings, name='recordings'),
    path('confs/<int:conf>/recordings/<int:published>/<str:file_name>', views.get_recording, name='get_recording_file'),
    path('confs/<int:conf>/recordings/<str:file_name>/publish', views.PublishRecordingView.as_view(), name='publish_recording'),
    path('confs/recordings/<int:pk>/update', views.UpdateRecordingView.as_view(), name='update_recording'),
    path('confs/recordings/<int:pk>/delete', views.DeletePublishedRecordingView.as_view(), name='delete_recording'),
]
