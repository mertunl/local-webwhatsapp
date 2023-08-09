from flask import Flask, render_template
import requests
import psycopg2
import json

#postgresql database'le bağlantı kuruyoruz
try:
    connection = psycopg2.connect(
        dbname="stajwp",
        user="postgres",
        password="1234",
        host="localhost",
        port="5432"
    )
    print("Bağlantı başarılı!")
except psycopg2.Error as e:
    print("Bağlantı hatası:", e)

cur= connection.cursor()

print( connection.get_dsn_parameters() )



app = Flask(__name__)

interval_seconds = 2
# Anasayfa
@app.route('/')

def home():
    while True:
        
        
        
        urlmsg="https://api.ultramsg.com/ornek/chats/messages"
        urlname="https://api.ultramsg.com/ornek/chats"
   
        
        querystring2 = {
        "token": "ornek"
        }
        headers = {'content-type': 'application/x-www-form-urlencoded'}

        #id ve name verileri için API' gönderilen istek
        responseName=requests.request("GET", urlname, headers=headers, params=querystring2)
        
        #Json formatıyla gelen verilerin içinden id ve name verilerini alıyoruz
        parsed_data5=json.loads(responseName.text)
        first_item3 = parsed_data5[0]
        print(first_item3["id"])
        idText=  first_item3["id"]

        parsed_data6=json.loads(responseName.text)
        first_item4 = parsed_data6[0]
        print(first_item4["name"])
        nameText=  first_item4["name"]
        
        # id verisini kullanarak son gelen-giden mesaj içeriğine istek yolluyoruz
        msg={
        "token": "ornek",
        "chatId": idText,
        "limit": 1
        }
        response2 = requests.request("GET", urlmsg, headers=headers, params=msg)

        #Json formatıyla gelen-giden mesaj içeriği verilerin içinden body ve fromMe(mesajı kendimiz mi karşının mı gönderdiği) verilerini alıyoruz
        parsed_data1=json.loads(response2.text)
        first_item1 = parsed_data1[0]
        print(first_item1["body"])
        bodyText=  first_item1["body"]

        parsed_data2=json.loads(response2.text)
        first_item2 = parsed_data2[0]
        print(first_item2["fromMe"])
        frommeText=  first_item2["fromMe"]

        #fromme table'ındaki veri sayısı 5'i geçtiğinde database'i siliyoruz
        def check_and_delete_rows():
            table_name = "fromme"
            row_limit = 5

            cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cur.fetchone()[0]
            if row_count >= row_limit:
                cur.execute(f"DELETE FROM {table_name}")
                connection.commit()
                print("Veriler silindi.")

        check_and_delete_rows()

        #api'lara istek yolladığımızda son gelen mesajın name,body,fromme verilerini database'e kaydediyoruz
        try:
            komut_INSERT = "INSERT INTO fromme(isim,body,fromme) VALUES('{}','{}','{}');".format(nameText,bodyText,frommeText)
            cur.execute(komut_INSERT)
            connection.commit()

            
        except Exception as e:
            connection.rollback()
            print("Hata:", e)

        #fromme table'ındaki fromme=False olan verinin son body verisini döndürüyoruz
        fromme_value3="False"
        query_body2= " SELECT body FROM fromme WHERE fromme = %s ORDER BY id DESC LIMIT 1;"
        cur.execute(query_body2,(fromme_value3,))
        rows_body2= cur.fetchone()
        print(rows_body2)
        #veriler table'ındaki fromme=False olan verinin son body verisini döndürüyoruz
        fromme_value4="False"
        query_body_last="SELECT body FROM veriler WHERE fromme = %s ORDER BY id DESC LIMIT 1;"
        cur.execute(query_body_last,(fromme_value4,))
        son_veri=cur.fetchone()
           
        #kullandığımız iki table'daki son verilerin body verisi farklı ise veriler table'ına verileri yolluyoruz
        if rows_body2!=son_veri:
            try:
                komut_INSERT = "INSERT INTO veriler(isim,body,fromme) VALUES('{}','{}','{}');".format(nameText,bodyText,frommeText)
                cur.execute(komut_INSERT)
                connection.commit()
                
            
            except Exception as e:
        # Hata durumunda işlemi geri almak için ROLLBACK yapmak
                connection.rollback()
                print("Hata:", e)

        

        #veriler table'ındaki isimler verisini bir diziye aktarıp dizinin son 5 indexindeki elemanları döndürüyoruz
        query_isim= " SELECT isim FROM veriler WHERE fromme = %s ORDER BY id LIMIT 50;"
        fromme_value="False"
        cur.execute(query_isim,(fromme_value,))
        rows_isim= cur.fetchall()
        isimdizi=[]
        for row_isim in rows_isim:
            
                isimdizi.append(row_isim)
        last_isimdizi= isimdizi[-5:]
        print(last_isimdizi)


        #veriler table'ındaki mesajlar verisini bir diziye aktarıp dizinin son 5 indexindeki elemanları döndürüyoruz
        query_body= " SELECT body FROM veriler WHERE fromme = %s ORDER BY id LIMIT 50;"
        cur.execute(query_body,(fromme_value,))
        rows_body= cur.fetchall()
        isimdizi=[]
        
        for row_body in rows_body:
            
                isimdizi.append(row_body)
       
        last_bodydizi=[]
        last_bodydizi= isimdizi[-5:]
        
        
        
        



        return render_template('index.html', 
                               body=last_bodydizi, isimler=last_isimdizi
                               
                               )

        



if __name__ == '__main__':
    app.run(debug=True)