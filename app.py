import streamlit as st
from datetime import datetime, date
import firebase_admin
from firebase_admin import credentials, firestore

fileName = str(date.today())
fileName = fileName + ".csv"

if not firebase_admin._apps:
    cred = credentials.Certificate("certificate.json")
    app = firebase_admin.initialize_app(cred)

store = firestore.client()

collection_name = fileName

doctorFileName = "DoctorList.csv"
clientFileName = "ClientList.csv"
settingFileName = "Setting.csv"

def returnData(type):
    data = []

    docs = store.collection(settingFileName).get()
    for doc in docs:
        data.append(doc.to_dict())

    if type == "Daily":
        for each in data:
            return each["DailyLimit"]
    elif type == "WalkIn":
        for each in data:
            return each["WalkInLimit"]

def uploadData(data, naming):
    store.collection(collection_name).document(naming).set(data)

def retriveData(type):
    data = []

    docs = store.collection(collection_name).get()
    for doc in docs:
        data.append(doc.to_dict())

    if type == "ID":
        IDs = []
        for each in data:
            IDs.append(each["Queue ID"])
        return IDs
    elif type == "All":
        return data
    elif type == "lenghtDaily":
        return len(data)
    elif type == "lenghtWalkIn":
        walkIn = []
        for each in data:
            if each["Doctor Name"] == "Walk in":
                walkIn.append(each)
        return len(walkIn)
    else:
        for each in data:
            if (type == each["Queue ID"]):
                return each["Status"]

def updateData(QueueID, newStatus):
    docs = store.collection(collection_name).get()
    for doc in docs:
        key = doc.id
        temp = doc.to_dict()
        if QueueID == temp["Queue ID"]:
            store.collection(collection_name).document(key).update({"Status":newStatus})
            break

def retriveDoctor(caller):
    data = []

    docs = store.collection(doctorFileName).get()
    for doc in docs:
        data.append(doc.to_dict())

    if caller == "client":
        doctorNames = []
        for each in data:
            doctorNames.append(each["Doctor Name"])
        return doctorNames
    elif caller == "doctor":
        doctorInfo = []
        for each in data:
            doctorInfo.append([each["Doctor Name"], each["Password"]])
        return doctorInfo

def uploadClient(doctor, naming):
    store.collection(clientFileName).document(naming).set(doctor)

def retriveClient():
    data = []

    docs = store.collection(clientFileName).get()
    for doc in docs:
        data.append(doc.to_dict())

    return data

# ---------------------------------------------------------------------------------

def registerClient(name, password):
    # readFile = open("DoctorList.csv", "r")
    # reader = csv.reader(readFile)
    reader = retriveClient()
    for row in reader:
        if row == name:
            return False
    # readFile.close()

    uploadClient({"Client Name": name, "Password": password}, name)
    return True

def loginClient(name, password):
    listing = retriveClient()
    for row in listing:
        if (row["Client Name"] == name) and (row["Password"] == password):
            return True
    return False

def retriveClientData(name, password):
    checker = loginClient(name, password)
    if checker:
        data = retriveData("All")
        for each in data:
            if each["Username"] == name:
                return each["Queue ID"]
        return str("False2")
    else:
        return str("False1")

# ----------------------------------------------------------------------------------------------

def addQueueV2(username, password, doctor, appointed):
    # st.warning(retriveData("lenghtWalkIn"))
    # st.warning(retriveData("lenghtDaily"))
    # st.warning(returnData("WalkIn"))
    # st.warning(returnData("Daily"))
    if appointed == False:
        if retriveData("lenghtWalkIn") >= returnData("WalkIn"):
            return "MaximumWalkIn"
    else:
        if retriveData("lenghtDaily") >= returnData("Daily"):
            return "MaximumDaily"
    retrivingUser = retriveClient()
    for each in retrivingUser:
        if (username == each["Client Name"]):
            if (password == each["Password"]):
                amount = len(retriveData("All")) + 1
                name = "Q" + str(amount)
                rightNow = datetime.now()
                if appointed == False:
                    doctor = "Walk in"
                subQueue = {"Username": username, "Password": password, "Doctor Name": doctor, "Queue ID": name, "Appointed": str(appointed), "Time": rightNow.strftime("%H:%M:%S"), "Status": "Waiting"}
                uploadData(subQueue, name)
                return name
            else:
                return "Wrong Password"
    return "No user"

# ---------------------------------------------------------------------------------------------

st.title("เข้าสู่ระบบคิวนัดพบแพทย์")

insertForm = st.empty()
form = insertForm.form(key="TestForm1", clear_on_submit=False)
username = form.text_input("ชื่อบัญชีผู้ป่วย")
password = form.text_input("รหัสผ่าน")
doctor = form.selectbox("ชื้อแพทย์ที่ท่านต้องการตรวจ", retriveDoctor("client"))
appointed = form.checkbox("นัดไว้ล่วงหน้าหรือไม่")

register_button = form.form_submit_button("สร้างบัญชี")
submit_button = form.form_submit_button(label="เข้าคิวพบแพทย์")
check_queue = form.form_submit_button("ตรวดสอบคิว")

if register_button:
    result = registerClient(username, password)
    if result:
        st.success("สมัครเสร็จสมบูรณ์")
    else:
        st.error("มีบรรชีที่ใช้ชื่อนั้นแล้วครับ")

def longFunction(output, again):
    setTime6 = datetime.now().timestamp()
    currentTime6 = datetime.now().timestamp()
    if again:
        st.success("เลขคิวของท่านคือ {}".format(output))
    else:
        st.success("เลขคิวของท่านคือ {} โปรดรอการเรียก".format(output))
    while (currentTime6 - setTime6) < 5:
        currentTime6 = datetime.now().timestamp()
    
    initial_Pending = False
    current_Status = retriveData(output)
    previous = -1
    delay = 60
    setTime2 = datetime.now().timestamp() - delay
    while True:
        currentTime2 = datetime.now().timestamp()
        if (currentTime2 - setTime2 > delay):
            setTime2 = datetime.now().timestamp()
            status = retriveData(output)
            if current_Status != status:
                current_Status = status
                if status == "Waiting":
                    st.info("คิวของท่านยังไม่ได้ถูกเรียกหรือได้หยุกการเรีกไปแล้ว โปรดรอการเรียกครับ")
                elif status == "Pending1":
                    previous = datetime.now().timestamp()
                    initial_Pending = True
                    current_Status = status
                    updateData(output, "Pending2")
                elif status == "Pending2":
                    current = datetime.now().timestamp()
                    time_remains = (360 - (current - previous))
                    current_waiting = -1
                    setTime3 = datetime.now().timestamp() - delay
                    while (time_remains // 60) > 1 and current_Status == status:
                        currentTime3 = datetime.now().timestamp()
                        if (currentTime3 - setTime3) > delay:
                            setTime3 = datetime.now().timestamp()
                            current = datetime.now().timestamp()
                            time_remains = (360 - (current - previous))
                            if ((time_remains // 60 < 6) and (time_remains // 60 > 1)) and (time_remains // 60 != current_waiting):
                                current_waiting = (time_remains // 60)
                                st.warning("ถึงคิวของท่ามแล้ว ท่านมีเวลา {} นาทีเพื่อไปถึงห้องตรวจ".format(str(time_remains // 60)))
                            status = retriveData(output)
                    current_Status = status
                    if (retriveData(output) != "Complete") and (retriveData(output) != "Waiting"):
                        updateData(output, "Pending3")
                elif status == "Pending3":
                    current = datetime.now().timestamp()
                    time_remains = (360 - (current - previous))
                    st.warning("คิวของท่ามได้ถูกเรียกแล้ว ตอนนี้คุณเหลือเวลา 1.0 นาทีเพื่อไปถึงห้องตรวจ")
                    setTime4 = datetime.now().timestamp() - delay
                    while time_remains > 0 and current_Status == status:
                        currentTime4 = datetime.now().timestamp()
                        if (currentTime4 - setTime4) > delay:
                            setTime4 = datetime.now().timestamp()
                            current = datetime.now().timestamp()
                            time_remains = (360 - (current - previous))
                            status = retriveData(output)
                    current_Status = status
                    if (retriveData(output) != "Complete") and (retriveData(output) != "Waiting"):
                        updateData(output, "Pending4")
                elif status == "Pending4":
                    st.warning("โปรดเข้าพบแพทย์ทันที")
                    current_Status = status
                    setTime5 = datetime.now().timestamp() - delay
                    while current_Status == status:
                        currentTime5 = datetime.now().timestamp()
                        if (currentTime5 - setTime5) > delay:
                            setTime5 = datetime.now().timestamp()
                            status = retriveData(output)
                elif status == "Complete":
                    st.success("ขอบคุณที่ใช้บริการเข้าคิวพบแพทย์")
                    break                
                else:
                    st.error("มีข้อผิดพลาดทางระบบ โปรดติดต่อเจ้าหน้าที่")
                    break

if check_queue:
    output = retriveClientData(username, password)
    if output == "False1":
        st.error("ไม่มีบัญชีชื่อนี้หร์อรหัสผ่านผิด")
    elif output == "False2":
        st.warning("คุณยังไม่ได้เข้าระบบคิว")
    else:
        longFunction(output, True)

if submit_button:
    output = addQueueV2(username, password, doctor, appointed)
    if output == "No user":
        st.error("ไม่เจอบัญชี")
    elif output == "Wrong Password":
        st.error("ไม่มีบัญชีชื่อนี้หร์อรหัสผ่านผิด")
    elif output == "MaximumDaily":
        st.error("วันนี้จำนวนรับตรวจผู้ป่วยเต็มแล้ว")
    elif output == "MaximumWalkIn":
        st.error("วันนี้จำนวนรับตรวจผู้ป่วยที่ไม่ได้นัดไว้เต็มแล้ว")
    else:
        longFunction(output, False)
