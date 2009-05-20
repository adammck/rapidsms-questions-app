#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.views.decorators.http import *
from rapidsms.webui.utils import *
from apps.questions.models import *


@require_GET
def submissions(req):
    return render_to_response(req,
        "questions/submissions.html", {
        "submissions": paginated(req, Submission.objects.all())
    })


@require_GET
def questions(req, pk=None):
    return render_to_response(req,
        "questions/questions.html", {
        "sections": Section.objects.all()
    })


@require_GET
def add_question(req):
    pass


@require_GET
def edit_question(req):
    pass
