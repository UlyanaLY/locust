import sys, re, random
from locust import task, SequentialTaskSet, FastHttpUser, HttpUser, constant_pacing, events
from config.config import cfg, logger
from utils.assertion import check_http_response
from utils.non_test_methods import open_csv_file, generateFlightsDates, generateCardNumber
from urllib.parse import quote_plus, quote


class PurchaseFlightTicket(SequentialTaskSet): # класс с задачами (содержит основной сценарий)
    test_users_csv_filepath = cfg.csv_url
    test_flights_csv_filepath = cfg.csv_fl_url

    test_flights_data = open_csv_file(test_flights_csv_filepath)
    test_users_data = open_csv_file(test_users_csv_filepath)
    postHeaders = { 'Content-Type': 'application/x-www-form-urlencoded'}

    def on_start(self):
        @task
        def uc_00_getHomePage(self) -> None:
            logger.info(f"Test data for users is: {self.test_users_data}")
            self.client.get(
                '/WebTours/',
                name="req_00_0_getHomePage_WebTours/",
                allow_redirects=False,
                #debug_stream=sys.stderr
            )
            self.client.get(
                '/WebTours/header.html',
                name="req_00_1_getHomePage_WebTours/headers.html",
                allow_redirects=False,
                #debug_stream=sys.stderr
            )

            r_02_url_param_signOff = 'true'
            self.client.get(
                f'/cgi-bin/welcome.pl?signOff={r_02_url_param_signOff}',
                name="req_00_2_getHomePage_cgi-bin/welcome.pl?signOff=true",
                allow_redirects=False,
                #debug_stream=sys.stderr
            )

            with self.client.get(
                '/cgi-bin/nav.pl?in=home',
                name="req_00_3_getHomePage_cgi-bin/nav.pl?in=home",
                allow_redirects=False,
                catch_response=True,
                #debug_stream=sys.stderr
            ) as req00_3_response:
                check_http_response(req00_3_response, 'name="userSession"')

            self.user_session = re.search(r"name=\"userSession\" value=\"(.*)\"\/>", req00_3_response.text).group(1)  

            logger.info(f"\n__\n self.user_session: {self.user_session}\n__\n") 
            logger.info(f"\n__\n self.user_session: {req00_3_response.text}\n__\n")  
                
        @task
        def uc_01_LoginAction(self) -> None:
            self.user_data_row = random.choice(self.test_users_data)
            logger.info(self.user_data_row)

            self.username = self.user_data_row["username"]
            self.password = self.user_data_row["password"]

            logger.info(f"chosen username: { self.username} / chosen password: { self.password}")
            
            r01_01body=f"userSession={self.user_session}&username={self.username}&password={self.password}&login.x=46&login.y=2&JSFormSubmit=off"

            with self.client.post(
                '/cgi-bin/login.pl',
                name="req_01_0_LoginAction_cgi-bin/login.pl",
                headers=self.postHeaders,
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
                #debug_stream=sys.stderr
            ) as r_01_01response:
                check_http_response(r_01_01response, "<title>Web Tours Navigation Bar</title>")
            #logger.info(f"r_01_01response: {r_01_01response} ")     

            with self.client.get(
                f'/cgi-bin/login.pl?intro=true',
                name="req_01_2_LoginAction_cgi-bin/login.pl?intro=true",
                allow_redirects=False,
                catch_response=True,
                #debug_stream=sys.stderr
            ) as r_01_02response:
                check_http_response(r_01_02response, f">Welcome, <b>{self.username}</b>, to the Web Tours reservation pages.")     
        uc_00_getHomePage(self)  
        uc_01_LoginAction(self)

    @task
    def uc02_OpenFlightsTab(self):
        self.client.get(
            f'/cgi-bin/welcome.pl?page=search',
            name="req_02_0_OpenFlightsTab_cgi-bin/welcome.pl?page=search",
            allow_redirects=False,
            catch_response=True,
            # debug_stream=sys.stderr
        )

        self.client.get(
            f'/cgi-bin/nav.pl?page=menu&in=flights',
            name="req_02_1_OpenFlightsTab_cgi-bin/nav.pl?page=menu&in=flights",
            allow_redirects=False,
            # debug_stream=sys.stderr
        ) 

        self.client.get(
            f'/cgi-bin/reservations.pl?page=welcome',
            name="req_02_2_OpenFlightsTab_cgi-bin/reservations.pl?page=welcome",
            allow_redirects=False,
            catch_response=True,
            # debug_stream=sys.stderr
        )

    @task
    def uc03_FindFlight_InputParams(self):
        self.flights_data_row = random.choice(self.test_flights_data)
        depart = self.user_data_row["depart"]
        arrive = self.user_data_row["arrive"]
        self.seat_pref = self.flights_data_row["seatPref"]
        self.seat_type = self.flights_data_row["seatType"]

        dates_dict = generateFlightsDates()

        print("hi i am here")

        r03_0_body = f"advanceDiscount=0&depart={depart}&departDate={dates_dict["depart_date"]}&arrive={arrive}&returnDate={dates_dict["return_date"]}&numPassengers=1&seatPref={self.seat_pref}&seatType={self.seat_type}&findFlights.x=26&findFlights.y=1&.cgifields=roundtrip&.cgifields=seatType&.cgifields=seatPref"
        logger.info(f"r03_0_body: {r03_0_body}")
        with self.client.post(
            f'/cgi-bin/reservations.pl',
            name="req_03_0_FindFlight_InputParams_cgi-bin/welcome.pl?page=search",
            headers=self.postHeaders,
            data=r03_0_body,
            allow_redirects=False,
            catch_response=True,
           #debug_stream=sys.stderr
        ) as r_03_0response:
            check_http_response(r_03_0response, "Flight departing from")
            self.outboundFlight = re.search(r"<input type=\"radio\" name=\"outboundFlight\" value=\"(.*)\">", r_03_0response.text).group(1)

    @task
    def uc04_ChooseFlightOption(self):

        r04_0_body = f"outboundFlight={quote_plus(self.outboundFlight)}&numPassengers=1&advanceDiscount=0&seatType={self.seat_type}&seatPref={self.seat_pref}&reserveFlights.x=75&reserveFlights.y=8"
        logger.info(f"r03_0_body: {r04_0_body}")
        with self.client.post(
            f'/cgi-bin/reservations.pl',
            name="req_04_0_ChooseFlightOption_cgi-bin/reservations.pl",
            headers=self.postHeaders,
            data=r04_0_body,
            allow_redirects=False,
            catch_response=True,
        #    debug_stream=sys.stderr
        ) as r_04_0response:
            check_http_response(r_04_0response, "Total for 1 ticket(s) is =")      
        logger.info(f"r04!_0_responsebody: {r_04_0response}")      

    @task
    def uc05_ConfirmFlightBooking(self):
        self.firstname = self.user_data_row["firstname"]
        self.lastname = self.user_data_row["lastname"]
        self.street = self.user_data_row["street"]
        self.cityProvince = self.user_data_row["cityProvince"]
        self.exp_date = self.flights_data_row["expData"]

        r05_00_body = f"firstName={self.firstname}&lastName={self.lastname}&address1={quote(self.street)}&address2={quote(self.cityProvince)}&pass1={quote(self.firstname + ' ' + self.lastname)}&creditCard={generateCardNumber()}&expDate={quote_plus(self.exp_date)}&oldCCOption=&numPassengers=1&seatType={self.seat_type}&seatPref={self.seat_pref}&outboundFlight={quote_plus(self.outboundFlight)}&advanceDiscount=0&returnFlight=&JSFormSubmit=off&buyFlights.x=40&buyFlights.y=17&.cgifields=saveCC"
        logger.info(f"uc05 request body: {r05_00_body}")
        
        with self.client.post(
            '/cgi-bin/reservations.pl',
            name='req_05_0_ConfirmFlightBooking_cgi-bin/reservations.pl',
            headers=self.postHeaders,
            data=r05_00_body,
            debug_stream=sys.stderr,
            catch_response=True
        ) as r_05_0response:
            check_http_response(r_05_0response, "Thank you for booking through Web Tours.")
            logger.info("WebToursBaseUserClass: uc05_ConfirmFlightBooking done!")    



class WebToursBaseUserClass(FastHttpUser): # юзер-класс, принимающий в себя основные параметры теста
    wait_time = constant_pacing(cfg.pacing)

    host = cfg.url

    logger.info(f'WebToursBaseClassUserClass started. Host: {host}')

    tasks = [PurchaseFlightTicket]