import json
import requests

from problem.models import Problem 

from django.core.mail import send_mail	
from codedigger.settings import EMAIL_HOST_USER

from django.core.exceptions import ObjectDoesNotExist
from .models import organization , country , user , contest , user_contest_rank 
from user.models import Profile


def sendMailToUsers(rating_changes):
	users=Profile.objects.all()			
	for rating_change in rating_changes:
		user = users.filter(codeforces=rating_change['handle'])
		if user.exists():
			subject = 'Codeforces Rating Updated'
			message = 'Your rating is updated to ' + str(rating_change['newRating']) + ' from '+ str(rating_change['oldRating'])
			recepient = [user[0].owner.email]   
			
			send_mail(subject, message, EMAIL_HOST_USER, recepient, fail_silently = False)
			


def ratingChangeReminder():

	res=requests.get('https://codeforces.com/api/contest.list')

	if res.status_code != 200 :
		return 
	contests=res.json()
	if contests['status']!='OK':
		return

	subject = 'Codeforces Rating Reminder Started (Status OK)'
	message = 'This is automated message from Codedigger which tells that your codeforces rating reminder has started'
	recepient = 'shivamsinghal1012@gmail.com'
	send_mail(subject, message, EMAIL_HOST_USER, [recepient], fail_silently = False)

	contests = contests['result']

	for codeforces_contest in contests:
		id = str(codeforces_contest['id'])
		
		res = requests.get("https://codeforces.com/api/contest.ratingChanges?contestId="+id)
		
		if res.status_code == 200 :
			
			rating_changes = res.json()
			
			if rating_changes['status']=='OK':

				new_contest,created = contest.objects.get_or_create(
					contestId = str(codeforces_contest['id']) , 
					defaults = {
						'Type' : 'R',
						'name' : codeforces_contest['name'],
						'duration' : codeforces_contest['durationSeconds'],
					}
				)
				if 'startTimeSeconds' in codeforces_contest:
					new_contest.startTime = codeforces_contest['startTimeSeconds']

				new_contest.save()
					
				if not new_contest.isUpdated:
					new_contest.isUpdated = True
					new_contest.save()
					sendMailToUsers(rating_changes['result'])
				else:
					break
			
			else:
				check_contest = contest.objects.filter(contestId = id)

				if not check_contest.exists() : 
					continue
				elif check_contest[0].isUpdated :
					break
				else :
					continue

	
		else:
			check_contest = contest.objects.filter(contestId = id)

			if not check_contest.exists() : 
				continue
			elif check_contest[0].isUpdated :
				break
			else :
				continue
			 

def rating_to_difficulty(rating):
	if rating <= 1100 : 
		return 'B'
	elif rating <= 1500:
		return 'E'
	elif rating <= 1800:
		return 'M'
	elif rating <= 2100:
		return 'H'
	elif rating <= 2600:
		return 'S'
	else :
		return 'C'

def codeforces_update_users():
	
	url = "https://codeforces.com/api/user.ratedList"
	
	res  = requests.get(url)
	cnt = 0

	while res.status_code != 200 and cnt < 3:
		res  = requests.get(url)
		cnt+=1
	
	data= res.json()
	del res

	if(data["status"] != 'OK') :
		return 

	subject = 'Codeforces update Users Started (Status OK)'
	message = 'This is automated message from Codedigger which tells that your codeforces updation has started'
	recepient = 'shivamsinghal1012@gmail.com'
	send_mail(subject, message, EMAIL_HOST_USER, [recepient], fail_silently = False)

	for codeforces_user in data["result"]:

		newUser,created = user.objects.get_or_create(handle = codeforces_user['handle'])
		name = ""
		if 'firstName' in codeforces_user:
			name += codeforces_user['firstName']
			name += " "
		if 'lastName' in codeforces_user:
			name += codeforces_user['lastName']

		if len(name) > 100 : 
			name = name[:100]

		newUser.name = name		
		newUser.rating = codeforces_user['rating']
		newUser.maxRating = codeforces_user['maxRating']
		newUser.rank = codeforces_user['rank']
		newUser.maxRank  = codeforces_user['maxRank']
		newUser.photoUrl = codeforces_user['titlePhoto'][2:]

		if 'country' in codeforces_user :

			obj, created = country.objects.get_or_create(name=  codeforces_user['country'] )
			newUser.country = obj

		if 'organization' in codeforces_user :

			obj, created = organization.objects.get_or_create(name=  codeforces_user['organization'] )
			newUser.organization = obj

		newUser.save()

	subject = 'Codeforces update Users Finished (All users are updated)'
	message = 'This is automated message from Codedigger which tells that your codeforces updation has finished'
	recepient = 'shivamsinghal1012@gmail.com'
	send_mail(subject, message, EMAIL_HOST_USER, [recepient], fail_silently = False)

	del data
	return 

def codeforces_update_problems():

	subject = 'Codeforces update Problems Started'
	message = 'This is automated message from Codedigger which tells that your codeforces updation has started'
	recepient = 'shivamsinghal1012@gmail.com'
	send_mail(subject, message, EMAIL_HOST_USER, [recepient], fail_silently = False)


	url = "https://codeforces.com/api/contest.list"
	res = requests.get(url)

	if res.status_code != 200 :
		return

	data = res.json()
	del res

	if(data["status"] != 'OK') :
		return 

	for codeforces_contest in data['result'] : 

		url = "https://codeforces.com/api/contest.standings?contestId=" + str(codeforces_contest['id']) + "&from=1&count=1"
		res = requests.get(url)
		data= res.json()

		if(data["status"] != 'OK') :
			continue 

		new_contest = contest()
		if 'startTimeSeconds' in codeforces_contest:
			new_contest.startTime = codeforces_contest['startTimeSeconds']

		new_contest.Type = 'R'
		new_contest.contestId = codeforces_contest['id']
		new_contest.name = codeforces_contest['name']
		new_contest.duration = codeforces_contest['durationSeconds']

		if len(contest.objects.filter(contestId=codeforces_contest['id'])) == 0: 
			new_contest.save()

		for contest_problem in data['result']['problems']:
			new_problem = Problem()
			new_problem.name = contest_problem['name']
			new_problem.contest_id = contest_problem['contestId']
			new_problem.prob_id = str(contest_problem['contestId']) + contest_problem['index']
			new_problem.url = "https://codeforces.com/contest/"+ str(contest_problem['contestId'])+"/problem/"+contest_problem['index']
			new_problem.platform = 'F'  
			new_problem.index = contest_problem['index']
			new_problem.tags = contest_problem['tags']
			if 'rating' in contest_problem : 
				new_problem.rating = contest_problem['rating']
				new_problem.difficulty = rating_to_difficulty(int(contest_problem['rating']))

			if len(Problem.objects.filter(prob_id = str(contest_problem['contestId']) + contest_problem['index'])) == 0: 
				new_problem.save()
	
	url = "https://codeforces.com/api/contest.list?gym=true"
	res = requests.get(url)

	if res.status_code != 200 :
		return

	data = res.json()

	if(data["status"] != 'OK') :
		return 

	for codeforces_contest in data['result'] : 

		url = "https://codeforces.com/api/contest.standings?contestId=" + str(codeforces_contest['id']) + "&from=1&count=1"
		res = requests.get(url)
		if res.status_code != 200 :
			continue
		data= res.json()

		if(data["status"] != 'OK') :
			continue 

		new_contest = contest()
		if 'startTimeSeconds' in codeforces_contest:
			new_contest.startTime = codeforces_contest['startTimeSeconds']

		new_contest.Type = 'R'
		new_contest.contestId = codeforces_contest['id']
		new_contest.name = codeforces_contest['name']
		new_contest.duration = codeforces_contest['durationSeconds']

		if len(contest.objects.filter(contestId=codeforces_contest['id'])) == 0: 
			new_contest.save()

		for contest_problem in data['result']['problems']:
			new_problem = Problem()
			new_problem.name = contest_problem['name']
			new_problem.contest_id = contest_problem['contestId']
			new_problem.prob_id = str(contest_problem['contestId']) + contest_problem['index']
			new_problem.url = "https://codeforces.com/gym/"+ str(contest_problem['contestId'])+"/problem/"+contest_problem['index']
			new_problem.platform = 'F'  
			new_problem.index = contest_problem['index']
			new_problem.tags = contest_problem['tags']
			if 'rating' in contest_problem : 
				new_problem.rating = contest_problem['rating']
				new_problem.difficulty = rating_to_difficulty(int(contest_problem['rating']))

			if len(Problem.objects.filter(prob_id = str(contest_problem['contestId']) + contest_problem['index'])) == 0: 
				new_problem.save()

	subject = 'Codeforces update Problem Finished'
	message = 'This is automated message from Codedigger which tells that your codeforces updation has finished'
	recepient = 'shivamsinghal1012@gmail.com'
	send_mail(subject, message, EMAIL_HOST_USER, [recepient], fail_silently = False)

	del data
	return

def codeforces_update_contest():

	subject = 'Codeforces update Contest Started'
	message = 'This is automated message from Codedigger which tells that your codeforces updation has started'
	recepient = 'shivamsinghal1012@gmail.com'
	send_mail(subject, message, EMAIL_HOST_USER, [recepient], fail_silently = False)

	url = "https://codeforces.com/api/contest.list"
	res = requests.get(url)
	if res.status_code != 200 :
		return
	data = res.json()
	del res

	if(data["status"] != 'OK') :
		return 

	for codeforces_contest in data["result"]:

		url = "https://codeforces.com/api/contest.ratingChanges?contestId=" + str(codeforces_contest['id'])
		res = requests.get(url)

		if res.status_code != 200 :
			continue

		data = res.json()

		if(data["status"] != 'OK') :
			continue

		new_contest,created = contest.objects.get_or_create(
			contestId = str(codeforces_contest['id']) , 
			defaults = {
				'Type' : 'R',
				'name' : codeforces_contest['name'],
				'duration' : codeforces_contest['durationSeconds'],
			}
		)
		if 'startTimeSeconds' in codeforces_contest:
			new_contest.startTime = codeforces_contest['startTimeSeconds']

		new_contest.save()

		if len(user_contest_rank.objects.filter(contest = new_contest)) == len(data['result']) :
			continue

		for participant in data['result']:
			user_handle = participant['handle']
			rank = participant['rank']

			try:
				contest_user = user.objects.get(handle = user_handle)
			except ObjectDoesNotExist:
				continue

			ucr,created = user_contest_rank.objects.get_or_create(user = contest_user , 
															contest = new_contest)

			ucr.worldRank = rank

			ucr.save()

	subject = 'Codeforces update Contest Finished'
	message = 'This is automated message from Codedigger which tells that your codeforces updation has finished'
	recepient = 'shivamsinghal1012@gmail.com'
	send_mail(subject, message, EMAIL_HOST_USER, [recepient], fail_silently = False)

	del data
	return