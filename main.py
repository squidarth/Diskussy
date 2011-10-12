from google.appengine.ext import webapp
import wsgiref.handlers
from google.appengine.ext.webapp \
	import template
from google.appengine.ext import db
import os
import sys
import re
import random
from google.appengine.ext.db import GqlQuery

#defines single model for program, a post has message, who, discussion_id, date
class Post(db.Model):
	message = db.StringProperty(required = False)
	who = db.StringProperty(required = False)
	discussion_id = db.StringProperty(required = True)
	date = db.DateTimeProperty(auto_now_add = True)
	
#handler for the main page, renders opening template and creates a post object when post is clicked
class MainPage(webapp.RequestHandler):
	def get(self):
		error_state = False
		no_errors = True
		values = {'error_state': error_state, 'no_errors': no_errors}
		self.response.out.write(template.render("main.html", values))
	
	def post(self):
		resource_name = str(random.randint(1000000000, 9999999999))
		if bool(self.request.get('message')) == False:
			error_state = True
			no_errors = False
			values = {'error_state': error_state, 'no_errors': no_errors}
			self.response.out.write(template.render("main.html", values))
			
		else:
			new_post = Post(message = self.request.get('message'), who = self.request.get('who'), discussion_id = resource_name)
			new_post.put()
			self.redirect('/' + resource_name)


#handler for discussion page--searches all posts and orders by date, then finds all the posts with the correct discussion_id	
class DiscussionPageHandler(webapp.RequestHandler):
	
	def get(self, id):
		query = GqlQuery("SELECT *FROM Post ORDER BY date ASC")
		items = query.fetch(9999)
		posts = []
		for item in items:
			if item.discussion_id == id:
				posts.append(item)
		values = {'posts' : posts}
		self.response.out.write(template.render("discussion.html", values))
		
	def post(self, id):
		if bool(self.request.get('message')) == False:
			person = self.request.get('who')
			query = GqlQuery("SELECT *FROM Post ORDER BY date ASC")
			items = query.fetch(9999)
			posts = []
			for item in items:
				if item.discussion_id == id:
					posts.append(item)
			error_state = True
			values = {'posts' : posts, 'person': person, 'error_state': error_state}
			self.response.out.write(template.render("discussion.html", values))
		else:
			new_post = Post(message = self.request.get('message'), who = self.request.get('who'), discussion_id = id)
			new_post.put()
			person = self.request.get('who')
			query = GqlQuery("SELECT *FROM Post ORDER BY date ASC")
			items = query.fetch(9999)
			posts = []
			for item in items:
				if item.discussion_id == id:
					posts.append(item)
			error_state = False
			values = {'posts' : posts, 'person': person, 'error_state': error_state}
			self.response.out.write(template.render("discussion.html", values))
		
class MessageHandler(webapp.RequestHandler):
	def get(self, id):
		query = GqlQuery("SELECT *FROM Post ORDER BY date ASC")
		items = query.fetch(9999)
		posts = []
		for item in items:
			if item.discussion_id == id:
				posts.append(item)
		self.response.out.write(template.render("chatscreen.html", {'posts':posts}))

def main():
	app = webapp.WSGIApplication([
		(r'/$', MainPage), (r'/mess/(\w*)', MessageHandler), (r'/(\d*)', DiscussionPageHandler)], debug=True)
	wsgiref.handlers.CGIHandler().run(app)

#implements program
if __name__ == "__main__":
	main()