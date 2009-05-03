#!/usr/bin/env python

import wsgiref.handlers

import base64
import os
import re
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template


class Post(db.Expando):
  created_at = db.DateTimeProperty(auto_now_add=True)
  file = db.TextProperty()
  mimetype = db.StringProperty()
  data = db.TextProperty()

class MainHandler(webapp.RequestHandler):
  def get(self):
    query = Post.all()
    query.order("-created_at")
    x = query.fetch(20);
    template_values = {
      'posts': x
    }
    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, template_values))

  def post(self):
    DATA_STREAM_EXTRA = 'org.linkdroid.intent.extra.stream'
    MIMETYPE_STREAM_EXTRA = 'org.linkdroid.intent.extra.stream_mime_type'
    mimetype = str(self.request.get(MIMETYPE_STREAM_EXTRA))
    obj = Post()
    if mimetype is not None and re.match("^(audio|image|video)/.+$", mimetype):
      obj.file = str(self.request.get(DATA_STREAM_EXTRA))
      obj.mimetype = mimetype

    vars = []
    for arg in self.request.arguments():
      if not arg == DATA_STREAM_EXTRA:
        vars.append("%s: %s" % (arg, self.request.get(arg)))
    obj.data = "\n".join(vars)
    obj.put()

class FileHandler(webapp.RequestHandler):
  def get(self):
    key = self.request.get('key')
    p = Post.get_by_id(int(key))
    if p is not None and re.match("^(audio|image|video)/.+$", p.mimetype):
      self.response.headers["Content-Type"] = str(p.mimetype)
      self.response.out.write(base64.decodestring(p.file))

def main():
  application = webapp.WSGIApplication(
      [('/', MainHandler),
       ('/file', FileHandler)],
      debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()
