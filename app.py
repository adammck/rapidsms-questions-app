#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import re
import rapidsms
from models import *


class App(rapidsms.app.App):
    def start(self):
        pass
    
    def handle(self, msg):
        for sect_obj in Section.objects.all():
            
            # attempt to match the incoming text against
            # this section's pattern. at this point, any
            # msg prefixed with a section pattern will do
            s_pat = r"^\s*(?:%s)\b(.*)$" % (sect_obj.prefix)
            sm = re.match(s_pat, msg.text, re.IGNORECASE)
            if sm is not None:
                
                text = str(sm.groups()[-1]).strip()
                self.info("Grabbed message: Section=%s, Text=%r" %
                    (sect_obj, text))
                
                sub_obj = Submission.objects.create(
                    section=sect_obj,
                    raw_text=text,
                    **msg.persistance_dict)
                
                # build an array of answers, by extracing
                # a single "Qn. Whatever" token from the
                # end of the text, until none are left
                answers = []
                while True:
                    q_pat = r"(.*)Q(\d+)\.?(.+?)$"
                    qm = re.match(q_pat, text, re.IGNORECASE)
                    if qm is None: break
                    
                    # we found an answer! store it, modify the
                    # text (replace it with the remainder)
                    text, number, answer = qm.groups()
                    answers.append((int(number), answer.strip()))
                
                self.info("Answers: %r" % (answers))
                
                # if no answers were found, the caller probably
                # formatted the message wrong, so return an error
                # TODO: try to deduce their error heuristically
                if not answers:
                    return msg.respond(
                        ("Sorry, I couldn't understand your answers.\n" +
                        "It should look like: %s Q1 answer Q2 answer") %
                            (sect_obj.code))
                
                answer_objects = []
                invalid_nums = []
                
                # iterate the answers that we just extracted,
                # which are still just chunks of text
                for num, text in answers:
                    try:
                    
                        # (attempt to) fetch the question object via
                        # its number. TODO: sub-questions? (1a, 1b, etc)
                        que_obj = Question.objects.get(
                            section=sect_obj,
                            number=num)
                    
                    # the question number was invalid!
                    except Question.DoesNotExist:
                        invalid_nums.append(num)
                    
                    # store the answer itself as raw text,
                    # since questions are untyped. casting
                    # happens when we want to VIEW the data
                    answer_objects.append(
                        Answer.objects.create(
                            submission=sub_obj,
                            question=que_obj,
                            raw_text=text))
                
                # send confirmation back to the reporter
                msg.respond("Thanks you for answering %d questions in the %s section." %
                    (len(answer_objects), sect_obj.title))
                
                return True
        
        # no section was matched, so
        # assume this message was not
        # for us...
        return False
