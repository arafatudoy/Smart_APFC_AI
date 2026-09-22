import streamlit as st
import requests
import pandas as pd
import time



# =====================================================
# SETTINGS
# =====================================================

SERVER_URL = "https://smart-apfc-api.onrender.com/api/data"



st.set_page_config(

    page_title="Smart APFC AI",

    layout="wide"

)



st.title(
    "⚡ Smart APFC AI Capacitor Management"
)





# =====================================================
# GET DATA
# =====================================================


def get_data():


    try:

        response=requests.get(

            SERVER_URL,

            timeout=3

        )


        return response.json()



    except:


        st.error(
            "Server not connected"
        )

        return None





data=get_data()



if data is None:

    st.stop()






# =====================================================
# ELECTRICAL PARAMETERS
# =====================================================


st.subheader(
    "Electrical Parameters"
)



c1,c2,c3,c4=st.columns(4)



c1.metric(

    "Voltage",

    f"{data['voltage']} V"

)


c2.metric(

    "Current",

    f"{data['current']} A"

)



c3.metric(

    "Real Power",

    f"{data['real_power']} W"

)



c4.metric(

    "Reactive Power",

    f"{data['reactive_power']} VAR"

)







# =====================================================
# PF CORRECTION
# =====================================================


st.subheader(
    "Power Factor Correction"
)



c1,c2,c3,c4=st.columns(4)



c1.metric(

    "Before PF",

    data["before_pf"]

)



c2.metric(

    "After PF",

    data["after_pf"]

)



c3.metric(

    "Required Compensation",

    f"{data['required_var']} VAR"

)



c4.metric(

    "Installed Compensation",

    f"{data['installed_var']} VAR"

)







# =====================================================
# BANK HEALTH
# =====================================================


st.subheader(
    "Capacitor Bank Health"
)



bank_health=data.get(

    "bank_health",

    0

)



c1,c2=st.columns(2)



c1.metric(

    "Average Bank Health",

    f"{bank_health}%"

)



failed=data.get(

    "failed_capacitors",

    []

)



if failed:


    c2.error(

        "Failed Capacitors : "

        +

        str(failed)

    )


else:


    c2.success(

        "All Capacitors Healthy"

    )








# =====================================================
# CAPACITOR TABLE
# =====================================================


st.subheader(

    "Capacitor Intelligence Table"

)



caps=data.get(

    "capacitor_status",

    {}

)



rows=[]



for name,value in caps.items():


    rows.append(

        {


        "Capacitor":
        name,


        "Health %":
        value["health"],


        "Operating Hours":
        value["operating_hours"],


        "Switch Count":
        value["switching_count"],


        "Temperature °C":
        value["temperature"],


        "Status":
        value["status"]


        }

    )



df=pd.DataFrame(rows)



st.dataframe(

    df,

    use_container_width=True

)









# =====================================================
# AI MAINTENANCE PREDICTION
# =====================================================


st.subheader(
    "🤖 AI Maintenance Prediction"
)



maintenance = data.get(
    "maintenance_prediction",
    {}
)



rows=[]


for cap,value in maintenance.items():

    rows.append({

        "Capacitor":cap,

        "RUL (Hours)":value.get(
            "RUL_hours",
            0
        ),

        "Risk Score":value.get(
            "risk_score",
            0
        ),

        "Risk Level":value.get(
            "risk_level",
            "LOW"
        )

    })


df=pd.DataFrame(rows)


st.dataframe(
    df,
    use_container_width=True
)


# =====================================================
# AI MAINTENANCE RECOMMENDATION
# =====================================================


st.subheader(
    "🤖 AI Maintenance Recommendation"
)



recommendations = data.get(

    "ai_recommendation",

    {}

)



recommendation_rows=[]



for cap,result in recommendations.items():


    recommendation_rows.append(

        {


            "Capacitor":

            cap,


            "Condition":

            result.get(

                "condition",

                "-"

            ),



            "Recommendation":

            result.get(

                "recommendation",

                "-"

            ),



            "Reason":

            result.get(

                "reason",

                "-"

            )

        }

    )



recommendation_df = pd.DataFrame(

    recommendation_rows

)



st.dataframe(

    recommendation_df,

    use_container_width=True

)



# =====================================================
# THERMAL PROTECTION STATUS
# =====================================================


st.subheader(
    "🔥 Thermal Protection Status"
)



thermal = data.get(
    "thermal_status",
    {}
)



thermal_rows=[]



for cap,status in thermal.items():


    thermal_rows.append(

        {

            "Capacitor":

            cap,


            "Temperature Status":

            status.get(
                "status",
                "NORMAL"
            ),



            "Fault":

            status.get(
                "fault",
                "-"
            ),



            "Protection":

            "TRIPPED"
            if status.get("trip")
            else "ACTIVE"

        }

    )



thermal_df = pd.DataFrame(

    thermal_rows

)



st.dataframe(

    thermal_df,

    use_container_width=True

)



# =====================================================
# CURRENT APFC SELECTION
# =====================================================


st.subheader(

    "Current APFC Selection"

)



selected=data.get(

    "selected",

    []

)



relay=data.get(

    "relay",

    {}

)



c1,c2=st.columns(2)



c1.write(

    "**Selected Capacitors:**"

)



c1.success(

    str(selected)

)





c2.write(

    "**Relay Status:**"

)



for cap,state in relay.items():


    if state=="ON":


        c2.success(

            cap+" : ON"

        )


    else:


        c2.write(

            cap+" : OFF"

        )








# =====================================================
# AUTO REFRESH
# =====================================================


time.sleep(2)


st.rerun()