from flask import Flask, jsonify, request
from flask_cors import CORS

import math

from datetime import datetime



from ML_Model.history_database import save_history

from ML_Model.predict_health import predict_health


from ML_Model.remaining_life import calculate_rul


from ML_Model.failure_prediction import (

    calculate_risk_score,

    risk_level

)


from ML_Model.maintenance_recommendation import (

    maintenance_recommendation

)



from Virtual_APFC.apfc_algorithm import smart_apfc



from Aging_Model.capacitor_database import capacitors

from Aging_Model.aging_simulator import update_aging

from Aging_Model.thermal_protection import thermal_protection





app = Flask(__name__)
CORS(app)







# =====================================================
# INITIAL DATA
# =====================================================



def all_caps_off():


    return {


        "CAP1":"OFF",

        "CAP2":"OFF",

        "CAP3":"OFF",

        "CAP4":"OFF",

        "CAP5":"OFF",

        "CAP6":"OFF"

    }






relay_status = all_caps_off()





latest_data = {


    "voltage":230,

    "current":0,


    "real_power":0,

    "reactive_power":0,

    "apparent_power":0,


    "before_pf":0,

    "after_pf":0,


    "required_var":0,

    "installed_var":0,


    "bank_health":0,


    "failed_capacitors":[],


    "health":{},


    "capacitor_status":{},


    "maintenance_prediction":{},


    "thermal_status":{},


    "ai_recommendation":{},


    "selected":[],


    "relay":relay_status

}








# =====================================================
# PF CALCULATION
# =====================================================



def calculate_pf(P,Q):


    S = math.sqrt(

        P**2 + Q**2

    )



    if S == 0:

        return 0



    return round(

        min(P/S,1),

        3

    )









# =====================================================
# CAPACITOR STATUS
# =====================================================



def get_capacitor_status():


    data={}



    for cap,info in capacitors.items():


        data[cap]={


            "health":

            round(

                info.get(

                    "health",

                    100

                ),

                2

            ),



            "operating_hours":

            round(

                info.get(

                    "operating_seconds",

                    0

                )

                /

                3600,

                2

            ),



            "switching_count":

            info.get(

                "switching_count",

                0

            ),



            "temperature":

            round(

                info.get(

                    "temperature",

                    25

                ),

                2

            ),



            "status":

            info.get(

                "status",

                "OFF"

            )

        }



    return data


# =====================================================
# STAGE 13.1
# RUL + RISK PREDICTION
# =====================================================


def get_maintenance_prediction():


    result={}



    for cap,info in capacitors.items():


        health = info.get(

            "health",

            100

        )


        temperature = info.get(

            "temperature",

            25

        )


        switching_count = info.get(

            "switching_count",

            0

        )



        operating_hours = (

            info.get(

                "operating_seconds",

                0

            )

            /

            3600

        )



        # RUL

        rul_hours = calculate_rul(

            info

        )



        # Risk

        risk = calculate_risk_score(

            health,

            temperature,

            switching_count,

            operating_hours

        )



        result[cap]={


            "RUL_hours":

            rul_hours,


            "risk_score":

            risk,


            "risk_level":

            risk_level(

                risk

            )

        }



    return result







# =====================================================
# STAGE 13.2
# THERMAL STATUS
# =====================================================


def get_thermal_status():


    thermal_status, tripped = thermal_protection(

        capacitors

    )


    return thermal_status







# =====================================================
# STAGE 13.3
# AI MAINTENANCE RECOMMENDATION
# =====================================================


def get_ai_maintenance_recommendation(

        maintenance_prediction,

        thermal_status

):


    recommendation={}



    for cap,info in capacitors.items():


        prediction = maintenance_prediction.get(

            cap,

            {}

        )


        thermal = thermal_status.get(

            cap,

            {}

        )



        health = info.get(

            "health",

            100

        )



        temperature = info.get(

            "temperature",

            25

        )



        result = maintenance_recommendation(

            
            health,


            prediction.get(

                "RUL_hours",

                0

            ),


            prediction.get(

                "risk_score",

                0

            ),


            prediction.get(

                "risk_level",

                "LOW"

            ),


            thermal.get(

                "status",

                "NORMAL"

            ),


            temperature

        )



        recommendation[cap]=result



    return recommendation







# =====================================================
# ESP32 POWER API
# =====================================================


@app.route(

    "/api/power",

    methods=["GET","POST"]

)


def power():


    global latest_data

    global relay_status



    if request.method=="GET":


        return jsonify(

            latest_data

        )



    data=request.json or {}



    print("\nESP32 DATA")

    print(data)




    voltage=float(

        data.get(

            "voltage",

            230

        )

    )



    current=float(

        data.get(

            "current",

            0

        )

    )



    real_power=float(

        data.get(

            "real_power",

            0

        )

    )



    reactive_power=float(

        data.get(

            "reactive_power",

            0

        )

    )



    before_pf = calculate_pf(

        real_power,

        reactive_power

    )



    # =================================================
    # AI HEALTH
    # =================================================


    health_data={}



    for cap,info in capacitors.items():


        features=[


            voltage,


            current,


            reactive_power,


            before_pf,


            info.get(

                "temperature",

                25

            ),


            info.get(

                "age",

                0

            ),


            info.get(

                "switching_count",

                0

            )

        ]



        ai_health = predict_health(

            features

        )



        physical_health = info.get(

            "health",

            100

        )



        final_health=(

            ai_health*0.7

            +

            physical_health*0.3

        )



        final_health=max(

            0,

            min(

                100,

                final_health

            )

        )



        health_data[cap]=round(

            final_health,

            2

        )
        
            # =================================================
    # APFC DECISION
    # =================================================


    apfc_result = smart_apfc(

        real_power,

        reactive_power,

        before_pf,

        health_data

    )



    if apfc_result is None:


        apfc_result={}



    relay_status = apfc_result.get(

        "relay",

        all_caps_off()

    )





    # =================================================
    # UPDATE CAPACITOR STATUS
    # =================================================


    for cap in capacitors:


        capacitors[cap]["status"] = relay_status.get(

            cap,

            "OFF"

        )





    # =================================================
    # AGING UPDATE
    # =================================================


    update_aging(

        relay_status,

        reactive_power

    )







    # =================================================
    # HISTORY SAVE
    # =================================================


    history={


        "time":

        datetime.now().strftime(

            "%Y-%m-%d %H:%M:%S"

        ),


        "voltage":

        voltage,


        "current":

        current,


        "real_power":

        real_power,


        "reactive_power":

        reactive_power,


        "pf":

        before_pf

    }




    for cap in capacitors:


        history[cap+"_health"] = capacitors[cap].get(

            "health",

            100

        )



    save_history(history)






    # =================================================
    # FINAL DATA
    # =================================================


    apparent_power = math.sqrt(

        real_power**2

        +

        reactive_power**2

    )



    capacitor_status = get_capacitor_status()



    # Stage 13.1

    maintenance_prediction = get_maintenance_prediction()



    # Stage 13.2

    thermal_status = get_thermal_status()



    # Stage 13.3

    ai_recommendation = get_ai_maintenance_recommendation(

        maintenance_prediction,

        thermal_status

    )






    latest_data={



        "voltage":

        round(

            voltage,

            2

        ),



        "current":

        round(

            current,

            3

        ),



        "real_power":

        round(

            real_power,

            2

        ),



        "reactive_power":

        round(

            reactive_power,

            2

        ),



        "apparent_power":

        round(

            apparent_power,

            2

        ),



        "before_pf":

        before_pf,



        "after_pf":

        apfc_result.get(

            "after_pf",

            before_pf

        ),



        "required_var":

        apfc_result.get(

            "required_var",

            0

        ),



        "installed_var":

        apfc_result.get(

            "reactive_reduction",

            0

        ),



        "bank_health":

        round(

            sum(

                health_data.values()

            )

            /

            len(

                health_data

            ),

            2

        ),



        "failed_capacitors":[


            cap

            for cap,h in health_data.items()

            if h < 40

        ],



        "health":

        health_data,



        "capacitor_status":

        capacitor_status,



        "maintenance_prediction":

        maintenance_prediction,



        "thermal_status":

        thermal_status,



        "ai_recommendation":

        ai_recommendation,



        "selected":

        apfc_result.get(

            "selected_capacitors",

            []

        ),



        "relay":

        relay_status

    }



    return jsonify(

        latest_data

    )








# =====================================================
# DASHBOARD API
# =====================================================


@app.route("/api/data")

def dashboard_data():


    return jsonify(

        latest_data

    )






@app.route("/api/status")

def status():


    return jsonify(

        latest_data

    )







@app.route("/")

def home():


    return "Smart APFC AI Stage 13.3 Server Running"







# =====================================================
# RUN SERVER
# =====================================================


if __name__=="__main__":


    app.run(

        host="0.0.0.0",

        port=5000,

        debug=False

    )
        
        
        