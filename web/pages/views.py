from django.shortcuts import render

from manuscripts.models import Manuscript, Transcription


def home(request):
    context = {
        "manuscript_count": Manuscript.objects.count(),
        "approved_count": Transcription.objects.filter(
            status=Transcription.Status.APPROVED
        ).count(),
    }
    return render(request, "pages/home.html", context)
