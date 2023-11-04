from django.urls import path ,include
from rest_framework_simplejwt import views as jwt_views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, re_path, include
from .views import sendDungleData, CustomTokenObtainPairView, CustomUserCreate, LogoutAPIView, MqttRunCommand, sendLastData, SetConfigNode, graphNodes,weather,Floor,controlPanel,ReportNodeStation,ReportSecurityStation,MatFiled,ReportRoomTem

urlpatterns = [
    path('create/', CustomUserCreate.as_view(), name="create_user"),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('mqttrun/',MqttRunCommand.as_view()),
    path('sendlastdata/',sendLastData.as_view()),
    path('setnodeconfig/',SetConfigNode.as_view()),
    path('graph/',graphNodes.as_view()),
    path('weather/',weather.as_view()),
    path('Floor/',Floor.as_view()),
    path('controlPanel/',controlPanel.as_view()),
    path('ReportNodeStation/',ReportNodeStation.as_view()),
    path('ReportSecurityStation/',ReportSecurityStation.as_view()),
    path('MatFile/',MatFiled.as_view()),
    path('ReportRoomTem/',ReportRoomTem.as_view()),
    path('DungleUpdate/', sendDungleData.as_view()),
]
