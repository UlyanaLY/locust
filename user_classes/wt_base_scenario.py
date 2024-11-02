import sys, re, random
from locust import task, SequentialTaskSet, FastHttpUser, HttpUser, constant_pacing, events
from config.config import cfg, logger
from utils.assertion import check_http_response
from utils.non_test_methods import open_csv_file


class PurchaseFlightTicket(SequentialTaskSet): # класс с задачами (содержит основной сценарий)
    test_users_csv_filepath = cfg.csv_url

    def on_start(self):

        @task
        def uc_00_getHomePage(self) -> None:
            self.test_users_data = open_csv_file(self.test_users_csv_filepath)
            logger.info(f"Test data for users is: {self.test_users_data}")
            r00_0_headers = {
                'sec-fetch-mode': 'navigate'
            }
            self.client.get(
                '/WebTours/',
                name="req_00_0_getHomePage_WebTours/",
                allow_redirects=False,
                debug_stream=sys.stderr
            )
            self.client.get(
                '/WebTours/header.html',
                name="req_00_1_getHomePage_WebTours/headers.html",
                allow_redirects=False,
                debug_stream=sys.stderr
            )

            r_02_url_param_signOff = 'true'
            self.client.get(
                f'/cgi-bin/welcome.pl?signOff={r_02_url_param_signOff}',
                name="req_00_2_getHomePage_cgi-bin/welcome.pl?signOff=true",
                allow_redirects=False,
                debug_stream=sys.stderr
            )

            with self.client.get(
                '/cgi-bin/nav.pl?in=home',
                name="req_00_3_getHomePage_cgi-bin/nav.pl?in=home",
                allow_redirects=False,
                catch_response=True,
                debug_stream=sys.stderr
            ) as req00_3_response:
                check_http_response(req00_3_response, 'name="userSession"')

            self.user_session = re.search(r"name=\"userSession\" value=\"(.*)\"\/>", req00_3_response.text).group(1)  

            logger.info(f"\n__\n self.user_session: {self.user_session}\n__\n") 
            logger.info(f"\n__\n self.user_session: {req00_3_response.text}\n__\n")  
                
        @task
        def uc_01_LoginAction(self) -> None:
            r01_0_headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            self.user_data_row = random.choice(self.test_users_data)
            logger.info(self.user_data_row)

            self.username = self.user_data_row["username"]
            self.password = self.user_data_row["password"]

            logger.info(f"chosen username: { self.username} / chosen password: { self.password}")
            
            r01_01body=f"userSession={self.user_session}&username={self.username}&password={self.password}&login.x=46&login.y=2&JSFormSubmit=off"

            with self.client.post(
                '/cgi-bin/login.pl',
                name="req_01_0_LoginAction_cgi-bin/login.pl",
                headers=r01_0_headers,
                data=r01_01body,
                catch_response=True,
                allow_redirects=False,
                debug_stream=sys.stderr
            ) as r_01_00response:
                check_http_response(r_01_00response, "User password was correct")

            with self.client.get(
                f'/cgi-bin/nav.pl?page=menu&in=home',
                name="req_01_1_LoginAction_cgi-bin/nav.pl?page=menu&in=homel",
                allow_redirects=False,
                catch_response=True,
                debug_stream=sys.stderr
            ) as r_01_01response:
                check_http_response(r_01_01response, "<title>Web Tours Navigation Bar</title>")

            with self.client.get(
                f'/cgi-bin/login.pl?intro=true',
                name="req_01_2_LoginAction_cgi-bin/login.pl?intro=true",
                allow_redirects=False,
                catch_response=True,
                debug_stream=sys.stderr
            ) as r_01_02response:
                check_http_response(r_01_02response, f">Welcome, <b>{self.username}</b>, to the Web Tours reservation pages.")    

            logger.info(f"r_01_01response: {r_01_01response.body} ")  

        uc_00_getHomePage(self)  
        uc_01_LoginAction(self)      
    @task
    def check(self):
        print("The end")

class WebToursBaseUserClass(FastHttpUser): # юзер-класс, принимающий в себя основные параметры теста
    wait_time = constant_pacing(cfg.pacing)

    host = cfg.url

    logger.info(f'WebToursBaseClassUserClass started. Host: {host}')

    tasks = [PurchaseFlightTicket]