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
        ordering = ["number"]
    
    def __unicode__(self):
        return "%s Q%d" % (
            self.section,
            self.number)


class Submission(models.Model):
    reporter   = models.ForeignKey(Reporter, null=True, related_name="submissions")
    connection = models.ForeignKey(PersistantConnection, null=True, related_name="submissions")
    submitted  = models.DateTimeField(auto_now_add=True)
    section    = models.ForeignKey(Section)
    raw_text   = models.TextField()
    
    def __unicode__(self):
        return "Submission by %s on %s" % (
            (self.reporter or self.connection),
            self.section)


class Answer(models.Model):
    submission = models.ForeignKey(Submission)
    question   = models.ForeignKey(Question)
    raw_text   = models.TextField()
    
    def __unicode__(self):
        return "Answer to %s: %s" % (
            self.question,
            self.raw_text)
