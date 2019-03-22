from channels.routing import ProtocolTypeRouter
from django.conf.urls import url
from . import consumers

application = ProtocolTypeRouter({
    # Empty for now (http->django views is added by default)
    url(r'^ws/instructor-input$', consumers.AudioConsumer),
})