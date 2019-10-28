import requests
import sys
import json
import datetime
import time



#-------------Input-----------


#Update this link with the protocol and servername:portnumber values of the ServiceDesk Plus.
apiURL = "https://yoururlhere.net"


#Replace 5CE9B1AF-D05D-4F1F-A0F1-39F407B0F72D with a Technician's API key.
TechnicianKey='5CE9B1AF-D05D-4F1F-A0F1-39F407B0F72D'

#Replace this with the  name of the additional field used for denoting the mail ids
additionalField = "INTERESTEDPARTY"

# INTERESTEDPARTY refers to the Email id(s) to notify field 

#-------------End of input -----------



#------------- Reading the Request Informations -----------


#time.sleep(60)
with requests.Session() as s:
    url = apiURL					
headers = {
    'technician_key': TechnicianKey
    }
file_Path = sys.argv[1]
with open(file_Path) as data_file:
    data = json.load(data_file)
requestObj = data['request']
workorderid = requestObj['WORKORDERID']



#------------- End of  Reading the Request Informations -----------


#------------- Reading email id to notidy field and sharing the request -----------

	
if(requestObj.get(additionalField)):


#------------- Getting technician mail ids  -----------		


	notifyField = requestObj[additionalField]
	EmailId = notifyField.strip().split(",")
	xmlData ='''
	<API version='1.0' locale='en'>
		<citype>
			<name>TECHNICIAN</name>
			<returnFields>
				<name>E-mail</name>
			</returnFields>
		</citype>
	</API>
	'''
	apprUrl = url +"/api/cmdb/ci"
	data = {'INPUT_DATA' : xmlData ,'TECHNICIAN_KEY': TechnicianKey ,'format':'json','OPERATION_NAME':'read'}
	r = s.post(apprUrl,data)
	print(r.json())
	if r.status_code == 200:
		responseobj=r.json()
		mailList=responseobj["API"]["response"]["operation"]["Details"]["field-values"]["record"]
		listArray = ""
		for mailID in mailList:
			if(listArray == ""):
				listArray = listArray + mailID["value"]
			else:
				listArray = listArray + "," + mailID["value"]


				
#------------- End of Getting technician mail ids  -----------	



		INPUT_DATA = '''
			{
				"share": {
		'''
		technicianData = '''
			"technicians": [
		'''
		requestData = '''
			"users": [
		'''
		technicianMailDatas = ""
		requesterMailDaats = ""		
		for mailId in EmailId:


		
#------------- If the email id belongs to technician, data is appended to technician details -----------


			if( listArray.find(mailId) != -1 ):				
				if(technicianMailDatas == ""):
					technicianMailDatas = technicianMailDatas + '''
					  {
						"email_id": "''' + mailId + '''"
					  }					
					'''
				else:
					technicianMailDatas = technicianMailDatas + "," + '''
					  {
						"email_id": "''' + mailId + '''"
					  }	
					'''				
				
				
#------------- End appending to technician details -----------					
				
				
				
				
#------------- If the email id belongs to requester, data is appended to technician details -----------				

				
			else:		
				if(requesterMailDaats == ""):
					requesterMailDaats = requesterMailDaats + '''
					  {
						"email_id": "''' + mailId + '''"
					  }	
					'''
				else:
					requesterMailDaats = requesterMailDaats + "," + '''
					  {
						"email_id": "''' + mailId + '''"
					  }	
					'''

					
#------------- End appending to requester details -----------



#------------- Constructing the INPUT_DATA -----------		
	
	
		if(technicianMailDatas != ""):
			INPUT_DATA = INPUT_DATA + technicianData + technicianMailDatas + "]"
		if(requesterMailDaats != ""):
			if(technicianMailDatas != ""):
				INPUT_DATA = INPUT_DATA +  ","  + requestData + requesterMailDaats + "]"
			else:
				INPUT_DATA = INPUT_DATA  + requestData + requesterMailDaats + "]"
		INPUT_DATA = INPUT_DATA + "}}"		
		
		
#------------- End of Constructing the INPUT_DATA -----------	
		

		data = {"INPUT_DATA":INPUT_DATA}
		apiurl=url+"/api/v3/requests/"+workorderid+"/share"
		r = s.put(apiurl,data,headers=headers)
		if(r.status_code == 200):
			print("Request updated successfully")					
				

#------------- End of Reading email id to notidy field and sharing the request -----------		
				
else:
	print("No emailIDs found in E-mail Id(s) To Notify")
						
