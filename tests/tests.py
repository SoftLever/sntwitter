import requests

update_case = requests.put(
	# "https://dev123554.service-now.com/api/now/table/sn_customerservice_case/8212fdc897721110c6f7322e6253af91",
	"https://dev123554.service-now.com/api/sn_customerservice/case/8212fdc897721110c6f7322e6253af91",
	auth=("TechniCollins", "Test_pwd_2022"),
	data='{"comments":"More comments by admin"}'.encode('utf-8'),
	headers={"Accept":"application/json", "Content-type":"application/json"}
)

print(update_case.status_code)
print(update_case.__dict__)
