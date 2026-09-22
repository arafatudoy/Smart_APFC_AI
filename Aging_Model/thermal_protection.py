# =====================================================
# SMART APFC AI
# Stage 13.2
# Thermal Fault Protection
# =====================================================


WARNING_TEMP = 50

TRIP_TEMP = 70

RECOVERY_TEMP = 45



thermal_fault_memory = {}





# =====================================================
# CHECK SINGLE CAPACITOR
# =====================================================


def check_temperature(cap, info):


    temperature = info.get(
        "temperature",
        25
    )


    # create memory

    if cap not in thermal_fault_memory:

        thermal_fault_memory[cap] = False





    # Already tripped

    if thermal_fault_memory[cap]:


        if temperature <= RECOVERY_TEMP:


            thermal_fault_memory[cap] = False


            return {


                "status":"RECOVERED",

                "fault":None,

                "trip":False

            }


        else:


            return {


                "status":"TRIPPED",

                "fault":"OVER TEMPERATURE",

                "trip":True

            }





    # New trip

    if temperature >= TRIP_TEMP:


        thermal_fault_memory[cap] = True


        return {


            "status":"TRIPPED",

            "fault":"OVER TEMPERATURE",

            "trip":True

        }





    elif temperature >= WARNING_TEMP:


        return {


            "status":"WARNING",

            "fault":"HIGH TEMPERATURE",

            "trip":False

        }





    else:


        return {


            "status":"NORMAL",

            "fault":None,

            "trip":False

        }





# =====================================================
# SCAN ALL CAPS
# =====================================================


def thermal_protection(capacitors):


    thermal_status={}

    tripped=[]



    for cap,info in capacitors.items():


        result = check_temperature(

            cap,

            info

        )


        thermal_status[cap]=result



        if result["trip"]:


            tripped.append(cap)



    return thermal_status,tripped