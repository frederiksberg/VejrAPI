from configparser import ConfigParser
import psycopg2

def config(filename="psql.ini", section="postgresql"):
    parser = ConfigParser()
    parser.read(filename)

    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
        return db

def connect(user, pwd):
    conn = None

    try:
        params = config()
        if params is None:
            return None
        conn = psycopg2.connect(
            user=user,
            password=pwd,
            **params
        )
        cur = conn.cursor()

        cur.execute("SELECT version()")
        
        # print("Established connection to", cur.fetchone())
        cur.close()

    except:
        return None
    
    return conn

def check_connection(user, pwd):
    conn = connect(user, pwd)
    if conn is not None:
        conn.close()
        return True
    return False


def add_hourly(user, pwd, D):
    SQL = "INSERT INTO vejr.hourly (from_date, temperature, pressure, windspd, humidity, precipitation) VALUES(%s, %s, %s, %s, %s, %s);"

    try:
        conn = connect(user, pwd)

        cur = conn.cursor()

        cur.execute(SQL, vars=[
            D["from_date"],
            D["temperature"],
            D["pressure"],
            D["windspd"],
            D["humidity"],
            D["precipitation"]
        ])
        conn.commit()

        cur.close()
        conn.close()
        return True
    except Exception as e:
        print("I failed")
        print(e)
        return None

def add_daily(user, pwd, D):
    SQL = "INSERT INTO vejr.daily (from_date, temperature_mean, temperature_min, temperature_max, pressure_mean, pressure_min, pressure_max, windspd_mean, windspd_min, windspd_max, humidity_mean, humidity_min, humidity_max, precipitation) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"

    try:
        conn = connect(user, pwd)

        cur = conn.cursor()

        cur.execute(SQL, vars=[
            D["from_date"],
            D["temperature_mean"],
            D["temperature_min"],
            D["temperature_max"],
            D["pressure_mean"],
            D["pressure_min"],
            D["pressure_max"],
            D["windspd_mean"],
            D["windspd_min"],
            D["windspd_max"],
            D["humidity_mean"],
            D["humidity_min"],
            D["humidity_max"],
            D["precipitation"]
        ])
        conn.commit()

        cur.close()
        conn.close()
        return True
    except Exception as e:
        print("I failed")
        print(e)
        return None