#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import re
from django.db import models
from apps.reporters.models import PersistantConnection, Reporter


class Section(models.Model):
    title   = models.CharField(max_length=100)
    code    = models.CharField(max_length=30)
    pattern = models.CharField(max_length=100, blank=True,
        help_text="Any incoming message prefixed by a string matching this regexp " +
                  "is assumed to be reporting on this section. The CODE field is " +
                  "automatically prepended to this pattern.")
    
    def __unicode__(self):
        return self.title
    
    @property
    def prefix(self):
        if self.pattern:
            return("%s|(?:%s)" %
                (self.code, self.pattern))
        
        # no pattern was specified, so all
        # we need to look for is the code
        return self.code


class Question(models.Model):
    section = models.ForeignKey(Section, related_name="questions")
    number  = models.IntegerField()
    text    = models.TextField()
    
    class Meta:
        ordering = ["section", "number"]
    
    def __unicode__(self):
        return "%s Q%d" % (
            self.section,
            self.number)
    
    @property
    def num_answers(self):
        return self.answers.count()
    
    @property
    def answer_percentage(self):
        sect_sub = self.section.submissions.count()
        if not sect_sub:
            return "0"
        
        return "%2d" % ((float(self.num_answers) / sect_sub) * 100)
    
    @property
    def last_answer(self):
        ans_objs = self.answers.all().order_by("-submission__submitted")
        return ans_objs[0] if ans_objs.count() else None


class Submission(models.Model):
    reporter   = models.ForeignKey(Reporter, null=True, related_name="submissions")
    connection = models.ForeignKey(PersistantConnection, null=True, related_name="submissions")
    section    = models.ForeignKey(Section, related_name="submissions")
    submitted  = models.DateTimeField(auto_now_add=True)
    raw_text   = models.TextField()
    
    class Meta:
        ordering = ["-submitted"]
    
    def __unicode__(self):
        return "Submission by %s on %s" % (
            (self.reporter or self.connection),
            self.section)
    
    @property
    def num_answers(self):
        return self.answers.count()


class Answer(models.Model):
    submission = models.ForeignKey(Submission, related_name="answers")
    question   = models.ForeignKey(Question, related_name="answers")
    raw_text   = models.TextField()
    
    def __unicode__(self):
        return "Answer to %s: %s" % (
            self.question,
            self.raw_text)
