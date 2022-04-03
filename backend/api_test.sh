#!/bin/bash

rm -f token.txt
curl "http://localhost:5000/api/authenticate/?username=admin&password=ucmyPhl%m8" 2> /dev/null | grep token | awk -F":" '{print $2}' | awk -F"\"" '{print $2}' > token.txt
token_len=`cat token.txt | tr -d '\n' | wc -m | awk -F" " '{print $1}'`;
token=`cat token.txt`;
if [ $token_len != 64 ]
then
	echo "Authentication failed";
	exit;
fi;
output=`curl "http://localhost:5000/api/authenticate/?username=admin&password=" 2> /dev/null | grep status | awk -F":" '{print $2}' | awk -F"\"" '{print $2}'`;
if [ "$output" != "failure" ];
then
	echo "Authentication succeeded while it should have failed";
	exit;
fi;
curl "http://localhost:5000/api/delete_user/?token=$token&username=admin2" > /dev/null 2>&1
output=`curl "http://localhost:5000/api/stats/?token=924f3s443534fdfffffffffffff3f343242343242342342dadsadasd1231231f" 2> /dev/null | grep "Invalid\ token" | awk -F":" '{print $2}' | awk -F"\"" '{print $2}'`;
if [ "$output" != "Invalid token" ];
then
	echo "Token parsing process should have failed.";
	exit;
fi;
output=`curl "http://localhost:5000/api/stats/?token=924f3s443534fdfffffffffffff3f343242343242342342dadsadasd1231231f" 2> /dev/null | grep "Invalid\ token" | awk -F":" '{print $2}' | awk -F"\"" '{print $2}'`;
if [ "$output" != "Invalid token" ];
then
	echo "Token parsing process should have failed.";
	exit;
fi;
output=`curl "http://localhost:5000/api/add_user/?token=$token&username=admin&password=faF2%sdasvD090f0&role_id=1" 2> /dev/null | grep "Username\ already\ taken" | awk -F":" '{print $2}' | awk -F"\"" '{print $2}'`;
if [ "$output" != "Username already taken" ];
then
	echo "Username should exist";
	exit;
fi;
output=`curl "http://localhost:5000/api/add_user/?token=$token&username=admin2&password=%432ffed$&role_id=1" 2> /dev/null | grep "Password\ should\ match\ the\ pattern\ " | awk -F":" '{print $2}' | awk -F"\"" '{print $2}'`;
if [ "$output" != "Password should match the pattern ^[a-zA-Z0-9#$%&@]{10,100}$" ];
then
	echo "Password should be invalid";
	exit;
fi;
output=`curl "http://localhost:5000/api/add_user/?token=$token&username=admin2&password=432ffedffFFgFF&role_id=1" 2> /dev/null | grep "Password\ must\ contain\ at\ least\ one\ upper\ case\ letter,\ one\ number\ and\ one\ special\ character" | awk -F":" '{print $2}' | awk -F"\"" '{print $2}'`;
if [ "$output" != "Password must contain at least one upper case letter, one number and one special character" ];
then
	echo "Password should be invalid";
	exit;
fi;
output=`curl "http://localhost:5000/api/add_user/?token=$token&username=admin2&password=432ffeddFFFF%&role_id=10" 2> /dev/null | grep "Invalid\ role\ was\ given" | awk -F":" '{print $2}' | awk -F"\"" '{print $2}'`;
if [ "$output" != "Invalid role was given" ];
then
	echo "Invalid role error was expected";
	exit;
fi;
curl "http://localhost:5000/api/add_user/?token=$token&username=admin2&password=432ffeddFFFF%&first_name=Dmitriy&last_name=Kuptsov&role_id=1" 2> /dev/null > out.txt;
output=`cat out.txt | grep "success" | awk -F":" '{print $2}' | awk -F"\"" '{print $2}'`
user_id=`cat out.txt | grep "user_id" | awk -F" " '{print $2}' | sed 's/\([0-9]*\).*/\1/'`
if [ "$output" != "success" ];
then
	echo "User should have been registered in the system";
	exit;
fi;
curl "http://localhost:5000/api/change_password/?token=$token&user_id=$user_id&new_password=432ffeddFFFF%2554" 2> /dev/null > out.txt
output=`cat out.txt | grep "success" | awk -F":" '{print $2}' | awk -F"\"" '{print $2}'`;
if [ "$output" != "success" ];
then
	echo "Password should have been changed";
	exit;
fi;
curl "http://localhost:5000/api/add_user/?token=$token&username=guest&password=432ffeddFFFF%&first_name=Dmitriy&last_name=Kuptsov&role_id=3" > /dev/null 2>&1
curl "http://localhost:5000/api/authenticate/?username=guest&password=432ffeddFFFF%" 2> /dev/null | grep token | awk -F":" '{print $2}' | awk -F"\"" '{print $2}' > token2.txt
guest_token=`cat token2.txt`
output=`curl "http://localhost:5000/api/stats/?token=$guest_token" 2> /dev/null | grep "forbidden" | awk -F":" '{print $2}' | awk -F"\"" '{print $2}'`
if [ "$output" != "forbidden" ];
then
	echo "Insufficient access rights";
	exit;
fi;

output=`curl "http://localhost:5000/api/update_user/?token=$token&user_id=$user_id&first_name=Dmitry&last_name=Kuptsov&role_id=1&email_address=dmitriy.kuptsov@gmail.com" 2> /dev/null | grep "success" | awk -F":" '{print $2}' | awk -F"\"" '{print $2}'`;
if [ "$output" != "success" ];
then
	echo "User info should have been updated in the database";
	exit;
fi;
#curl "http://localhost:5000/api/delete_user/?token=$token&username=guest" > /dev/null 2>&1
#output=`curl curl "http://localhost:5000/api/add_permission/?token=$token&access_role_id=10&access_right_id=32&resource=/api/histogram/" 2> /dev/null | grep "Invalid\ role\ was\ given" | awk -F":" '{print $2}' | awk -F"\"" '{print $2}'`;
#if [ "$output" != "Invalid role was given" ];
#then
#	echo "Invalid role error should have been returned";
#	exit;
#fi;
#output=`curl "http://localhost:5000/api/add_permission/?token=$token&access_role_id=1&access_right_id=32&resource=/api/histogram/" 2> /dev/null | grep "Invalid\ access\ right\ was\ given" | awk -F":" '{print $2}' | awk -F"\"" '{print $2}'`;
#if [ "$output" != "Invalid access right was given" ];
#then
#	echo "Invalid access right error should have been returned";
#	exit;
#fi;
#output=`curl "http://localhost:5000/api/add_permission/?token=$token&access_role_id=1&access_right_id=1&resource=/api/histogram" 2> /dev/null | grep "Resource\ name\ does\ not\ look\ like\ a\ valid\ resource\ string\ nor\ like\ a\ valid\ UUID" | awk -F":" '{print $2}' | awk -F"\"" '{print $2}'`;
#if [ "$output" != "Resource name does not look like a valid resource string nor like a valid UUID" ];
#then
#	echo "Invalid resource name error should have been returned";
#	exit;
#fi;
curl "http://localhost:5000/api/delete_image/?name=test&token=$token" > /dev/null 2>&1
#curl -d @test_material/image.dat "http://localhost:5000/api/add_image/?token=$token"
output=`curl -d @test_material/image.dat "http://localhost:5000/api/add_image/?token=$token" 2> /dev/null | grep "success" | awk -F":" '{print $2}' | awk -F"\"" '{print $2}'`;
if [ "$output" != "success" ];
then
	echo "TEST 1: Image should have been added to the database";
	exit;
fi;
curl "http://localhost:5000/api/delete_image/?name=test2&token=$token" > /dev/null 2>&1
output=`curl -d @test_material/image2.dat "http://localhost:5000/api/add_image/?token=$token" 2> /dev/null | grep "Image\ name\ cannot\ be\ empty,\ should\ contain\ letters\ and\ numbers\ and\ its\ length\ should\ not\ exceed\ 100\ characters" | awk -F":" '{print $2}' | awk -F"\"" '{print $2}'`;
if [ "$output" != "Image name cannot be empty, should contain letters and numbers and its length should not exceed 100 characters" ];
then
	echo "TEST 2: Invalid image name error should have been returned";
	exit;
fi;
curl "http://localhost:5000/api/delete_deposit/?token=$token&deposit_name_ru=новый(тест)&deposit_name_en=test&deposit_name_uz=test" > /dev/null 2>&1
#curl "http://localhost:5000/api/add_deposit/?token=$token&region_area_id=1&type_group_id=2&deposit_name_ru=новый(тест)&deposit_name_en=test&deposit_name_uz=test&amount_unit_id=7"
output=`curl "http://localhost:5000/api/add_deposit/?token=$token&region_area_id=1&type_group_id=2&deposit_name_ru=новый(тест)&deposit_name_en=test&deposit_name_uz=test&amount_unit_id=7" 2> /dev/null | grep "success" | awk -F":" '{print $2}' | awk -F"\"" '{print $2}'`;
if [ "$output" != "success" ];
then
	echo "Deposit should have been added into the database";
	exit;
fi;
curl "http://localhost:5000/api/delete_deposit/?token=$token&deposit_name_ru=новый(тест)&deposit_name_en=test&deposit_name_uz=test" > /dev/null 2>&1
curl "http://localhost:5000/api/delete_mineral/?token=$token&mineral_name_ru=test&mineral_name_en=test&mineral_name_uz=test" > /dev/null 2>&1
output=`curl "http://localhost:5000/api/add_mineral/?token=$token&mineral_name_ru=тест&mineral_name_en=test&mineral_name_uz=test" 2> /dev/null | grep "success" | awk -F":" '{print $2}' | awk -F"\"" '{print $2}'`;
if [ "$output" != "success" ];
then
	echo "Mineral should have been added into the database";
	exit;
fi;
#curl "http://localhost:5000/api/add_site/?token=$token&site_name_ru=новый&site_name_uz=newsite&site_name_en=newsite"
curl "http://localhost:5000/api/delete_mineral/?token=$token&mineral_name_ru=тест&mineral_name_en=test&mineral_name_uz=test" > /dev/null 2>&1
site_id=`curl "http://localhost:5000/api/add_site/?token=$token&site_name_ru=новый&site_name_uz=newsite&site_name_en=newsite" 2> /dev/null | grep site_id | awk -F" " '{print $2}' | sed 's/\([0-9]*\).*/\1/'`
#cat site.txt | grep site_id | awk -F" " '{print $2}' | sed 's/\([0-9]*\).*/\1/' 
#echo $site_id
#site_id=`curl "http://localhost:5000/api/add_site/?token=$token&site_name_ru=новый&site_name_uz=newsite&site_name_en=newsite" 2> /dev/null | grep site_id | awk -F" " '{print $2}' | sed 's/\([0-9]*\).*/\1/'`
#curl "http://localhost:5000/api/add_deposit/?token=$token&region_area_id=1&type_group_id=2&deposit_name_ru=newdeposit&deposit_name_en=newdeposit&deposit_name_uz=newdeposit&amount_unit_id=7" > deposit.txt
#cat deposit.txt 
#deposit_id=`curl "http://localhost:5000/api/add_deposit/?token=$token&region_area_id=1&type_group_id=2&deposit_name_ru=newdeposit&deposit_name_en=newdeposit&deposit_name_uz=newdeposit&amount_unit_id=7" 2> /dev/null | grep deposit_id | awk -F" " '{print $2}' | sed 's/\([0-9]*\).*/\1/'`
deposit_id=`curl "http://localhost:5000/api/add_deposit/?token=$token&region_area_id=1&type_group_id=2&deposit_name_ru=новый(тест)&deposit_name_en=newdeposit(test)&deposit_name_uz=newdeposit(test)&amount_unit_id=7" 2> /dev/null | grep deposit_id | awk -F" " '{print $2}' | sed 's/\([0-9]*\).*/\1/'`
#echo $deposit_id
output=`curl "http://localhost:5000/api/add_deposit_site/?token=$token&deposit_id=$deposit_id&site_id=$site_id&minerals_id=125&latitude=0&longitude=0&status_id=2" 2> /dev/null | grep "success" | awk -F":" '{print $2}' | awk -F"\"" '{print $2}'`
if [ "$output" != "success" ];
then
	echo "Deposit/site should have been added into the database";
	exit;
fi;
curl "http://localhost:5000/api/delete_deposit_site/?token=$token&deposit_id=$deposit_id&site_id=$site_id" > /dev/null 2>&1
curl "http://localhost:5000/api/delete_deposit/?token=$token&deposit_id=$deposit_id" > /dev/null 2>&1
curl "http://localhost:5000/api/delete_site/?token=$token&site_id=$site_id" > /dev/null 2>&1
output=`curl "http://localhost:5000/api/add_license/?token=$token&license=FN%20N%202002%20F3&company_id=2&date_of_issue=2012-01-01" 2> /dev/null | grep "success" | awk -F":" '{print $2}' | awk -F"\"" '{print $2}'`
if [ "$output" != "success" ];
then
	echo "License should have been added into the database";
	exit;
fi;
curl "http://localhost:5000/api/delete_license/?token=$token&license=FN%20N%202002%20F3" > /dev/null 2>&1
license_id=`curl "http://localhost:5000/api/add_license/?token=$token&license=FN%20N%202002%20F3&company_id=2&date_of_issue=2012-01-01" 2> /dev/null | grep license_id | awk -F" " '{print $2}' | sed 's/\([0-9]*\).*/\1/'`
output=`curl "http://localhost:5000/api/delete_license/?token=$token&license_id=$license_id" 2> /dev/null | grep "success" | awk -F":" '{print $2}' | awk -F"\"" '{print $2}'`
if [ "$output" != "success" ];
then
	echo "License should have been deleted from the database";
	exit;
fi;
curl "http://localhost:5000/api/add_deposit_site_license/?token=$token&deposit_site_id=984&license_id=682&amount_units_a_b_c1=1&amount_units_c2=2" 2>/dev/null > out.txt
output=`cat out.txt | grep "success" | awk -F":" '{print $2}' | awk -F"\"" '{print $2}'`
deposit_site_license_id=`cat out.txt | grep deposit_site_license_id | awk -F" " '{print $2}' | sed 's/\([0-9]*\).*/\1/'`
if [ "$output" != "success" ];
then
	echo "Deposit/site/license should have been added into the database";
	exit;
fi;
curl "http://localhost:5000/api/delete_deposit_site_license/?token=$token&deposit_site_license_id=$deposit_site_license_id" > /dev/null 2>&1
curl "http://localhost:5000/api/add_region/?token=$token&region_name_ru=тест%20тест&region_name_uz=test%20test&region_name_en=test%20test" > out.txt 2>/dev/null
#cat out.txt
region_id=`cat out.txt | grep region_id | awk -F" " '{print $2}' | sed 's/\([0-9]*\).*/\1/'`
if [ "$region_id" == "" ];
then
	echo "New region should have been added into the database. Instead we have got an error."
fi;
curl "http://localhost:5000/api/delete_region/?token=$token&region_id=$region_id" > /dev/null 2>&1
rm out.txt
#rm token*