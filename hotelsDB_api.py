from flask import Flask,request,jsonify
from flask_cors import CORS
import os
import mysql.connector
import datetime

app = Flask(__name__)
CORS(app)

@app.route('/')
def check() :
	return "Connected to the API server"
	
@app.route('/rooms', methods=['GET', 'POST'])
def rooms() :
	cnx = mysql.connector.connect(user = 'root', password = 'wing1226',host = 'localhost',database = 'hotelsDB')
	cursor = cnx.cursor(dictionary=True)
	
	checkin = request.args.get("checkin", default = "")
	checkout = request.args.get("checkout", default = "")
	
	query = "SELECT * from Room"
	cursor.execute(query)	
	result = cursor.fetchall()
	
	if checkin != "" and checkout != "":
		sql = ("Select Record.roomNo from Reservation Natural JOIN Record where (Reservation.checkinDate > '{0}' and Reservation.checkoutDate > '{1}') OR (Reservation.checkinDate < '{0}' and Reservation.checkoutDate > '{1}') and Reservation.status <> 'Canceling'").format(checkin, checkout)
		cursor.execute(sql)
		
		room_not_ava = cursor.fetchall()
		room_not_ava = [i['roomNo'] for i in room_not_ava]
		output = []
		
		for i in result:
			if i['roomNo'] not in room_not_ava:
				output.append(i)
		
		return jsonify(checkinDate=checkin, checkoutDate=checkout, rooms_available = output)

	#Close object
	cursor.close()
	cnx.close()
	return jsonify(results=result)
	
@app.route('/query', methods=['GET'])
def booking_query() :
	cnx = mysql.connector.connect(user = 'root', password = 'wing1226',host = 'localhost',database = 'hotelsDB')
	cursor = cnx.cursor(dictionary=True) 

	query = "Select reservationNo, email, checkinDate, checkoutDate, totalPrice, guestNum, guestFirstName, guestLastName, dateCreated, status From Reservation "
	output = []
	
	booking_no = request.args.get("booking_no", default = "")
	email = request.args.get("email", default = "")
	date_created = request.args.get("date_created", default = "")
	checkin = request.args.get("checkin", default = "")
	checkout = request.args.get("checkout", default = "")

	if booking_no == "all":
		True
	else:
		if booking_no is not "":
			query = query + "Where reservationNo = '{}' ".format(booking_no)
		elif email is not "":
			query = query + "Where email = '{}' ".format(email)
		elif checkin is not "":
			query = query + "Where checkinDate = '{}' ".format(checkin)
		elif checkout is not "":
			query = query + "Where checkoutDate = '{}' ".format(checkout)
		elif date_created is not "":
			query = query + "Where dateCreated = '{}' ".format(date_created)
		else:
			return jsonify({'error':'please check your variables'})
		
	cursor.execute(query)		
	result = cursor.fetchall()
	if result == []:
		output = {'error':'No matching result'}		
	else:
		for i in result:
			i['checkinDate'] = i['checkinDate'].strftime("%Y-%m-%d")
			i['checkoutDate'] = i['checkoutDate'].strftime("%Y-%m-%d")
			i['dateCreated'] = i['dateCreated'].strftime("%Y-%m-%d")

			query = "SELECT Room.* from Room NATURAL JOIN Record Where reservationNo = {}".format(i['reservationNo'])
			cursor.execute(query)		
			
			rooms = cursor.fetchall()
			i['room_info'] = rooms
			output.append(i)

	#Close object
	cursor.close()
	cnx.close()
	return jsonify(results=result)
	
@app.route('/booking', methods=['POST'])
def booking_build() :
	cnx = mysql.connector.connect(user = 'root', password = 'wing1226',host = 'localhost',database = 'hotelsDB')
	cursor = cnx.cursor()
	new_booking = request.get_json(force=True,silent=True)
	try:
	
		try:
			sql = ("Insert Into Contact (email) Values (%(email)s)")
			cursor.execute(sql,new_booking)
			sql = ("Insert Into Phone (email, phoneNo) Values (%(email)s, %(phone)s)")
			cursor.execute(sql,new_booking)
		except:
			True
		sql = ("Insert Into Reservation"
				"(email, checkinDate, checkoutDate, totalPrice, guestNum, guestFirstName, guestLastName, dateCreated, cardID, cardOwner, dueDate, status) "
				"Values (%(email)s, %(checkin)s, %(checkout)s, %(totalPrice)s, %(guestNum)s, %(guestFirstName)s, "
				"%(guestLastName)s, '"+ datetime.date.today().strftime("%Y-%m-%d") + "', %(card_ID)s, %(card_Owner)s, %(due_Date)s, 'Confirmed')")
				
		cursor.execute(sql,new_booking)
		cnx.commit()
		
		rooms = new_booking['roomNo'].split(",")
		booking_no = cursor.lastrowid

		sql = ("Insert Into Record (reservationNo, roomNo) Values (%(booking_no)s, %(roomNo)s)")
		for i in rooms:
			i = int(i)
			data = {'booking_no':booking_no, 'roomNo':i}
			cursor.execute(sql,data)

		cnx.commit()
		#Close object
		cursor.close()
		cnx.close()
		
		return jsonify(booking_no=booking_no, details=new_booking, status="Success") 	
	except:
		#Close object
		cursor.close()
		cnx.close()
		return jsonify(status="Failed",details=new_booking) 
		
@app.route('/cancel', methods=['POST'])
def booking_cancel() :
	cnx = mysql.connector.connect(user = 'root', password = 'wing1226',host = 'localhost',database = 'hotelsDB')
	cursor = cnx.cursor()
	cancel = request.get_json(force=True,silent=True)
	try:
		sql = ("Insert Into CancellationRequest (reservationNo, email, reason, dateCreated)  Values (%(reservationNo)s, %(email)s, %(reason)s, '")+ datetime.date.today().strftime("%Y-%m-%d") + "' )"
		cursor.execute(sql, cancel)
		sql = ("UPDATE Reservation SET status = 'Cancelled' Where reservationNo = %(reservationNo)s")
		cursor.execute(sql, cancel)
		
		cnx.commit()
		#Close object
		cursor.close()
		cnx.close()

		return jsonify(details=cancel, status="submitted")
	except:
		return jsonify(details=cancel, status="failed")
	
if __name__ == '__main__':
	app.run(host=os.getenv('IP', '0.0.0.0'),port=int(os.getenv('PORT', 8080)), threaded=True, debug=True)