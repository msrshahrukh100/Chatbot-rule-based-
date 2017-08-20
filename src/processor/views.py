# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.http import Http404, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

import json
# Create your views here.

def homepage(request) :
	if request.method == "POST" :
		if request.FILES.get("jsonfile") :
			data = json.loads(request.FILES.get("jsonfile").read())
			print type(data)
			request.session["chatbotdata"] = data
			return redirect('processor:chatbot')

		
		elif request.POST.get('jsondata') :
			data = json.loads(request.POST.get('jsondata'))
			print type(data)
			request.session["chatbotdata"] = data
			return redirect('processor:chatbot')
		else :
			messages.error(request, 'No input provided !')



	return render(request, "index.html", {})

def response(request) :
	return HttpResponse(str(request.session['main_response']))


@csrf_exempt
def chatbot(request) :
	

	if request.is_ajax() :

		step = request.session.get('step', 0)
		stage = request.session.get('stage', 1)
		data = request.session.get('chatbotdata', None)
		# print "The stage is " + str(stage)
		if not data :
			raise Http404("Chatbot data no more available !")
		
		
		textresponse = None
		optionresponse = None

		if request.method == 'POST' :
			textresponse = request.POST.get('textresponse')
			optionresponse = request.POST.get('options')
			# print textresponse
			# print optionresponse
			if textresponse or optionresponse :
				stage = stage + 1
				request.session['stage'] = stage
 
		questions = data["questions"]


		if "conditions" in questions[step].keys() :
			conditions = questions[step]["conditions"]
			# print (questions[step]["var"], str(textresponse))
			if textresponse : 
	 			exec("%s = '%s'" % (questions[step]["var"], textresponse))
	 		else :
	 			exec("%s = '%s'" % (questions[step]["var"], optionresponse))

			truth_values = []
			for c in conditions :
				values = []
				for i in c :
					print eval(i)
					values.append(eval(i))
				truth_values.append(all(values))

			final = any(truth_values)
			# print "final value is " + str(final)
			if not final :
				step = step + 1
				request.session['step'] = step

			
		if "instruction" in questions[step].keys() : 
			text = questions[step]['instruction']
		else :
			text = questions[step]['text']

		html = ""
		quick_replies = []

		if "var" in questions[step].keys() :
			if "options" in questions[step].keys() :
				# do something
				for o in questions[step]["options"] :
					html += "<p><input name='options' value='"+o+"' type='radio' id='"+o+"' /><label for='"+o+"'>"+o+"</label></p>"
					quick_replies.append({"content_type":"text", "title":o, "payload": o.lower()})
			else :
				html = "<div class='input-field col s12'><input id='textresponse' name='textresponse' type='text' class='validate'><label for='textresponse'>Your response</label></div>"

		response = {"text" : text, "html":html, "main_response":""}
		if not "conditions" in questions[step].keys() :
			request.session['step'] = step + 1


		# this is for the main response
		main_response = request.session.get('main_response')
		t = main_response.get("stage"+str(stage))
		if not t :
			main_response["stage"+str(stage)] = {}
		bot_says_list = main_response["stage"+str(stage)].get('Bot Says', [])
		if len(quick_replies) != 0 :
			bot_says_list.append({"message":{"text":text, "quick_replies":quick_replies}})
		else :
			bot_says_list.append({"message":{"text":text}})
		main_response["stage"+str(stage)]['Bot Says'] = bot_says_list
		if textresponse : 
			main_response["stage"+str(stage-1)]['User Says'] = textresponse
		elif optionresponse :
			main_response["stage"+str(stage-1)]['User Says'] = optionresponse

		request.session['main_response'] = main_response
		# print request.session['main_response']
		# this is for the main response
		if request.session['step'] == len(questions) :
			response['main_response'] = request.session['main_response']

		return JsonResponse(response)

	request.session['main_response'] = {}
	request.session['step'] = 0
	request.session['stage'] = 1
	return render(request, "chatbot.html", {})
