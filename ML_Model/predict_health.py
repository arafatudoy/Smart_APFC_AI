import tensorflow as tf
import joblib
import numpy as np
import os



# =====================================================
# PATHS
# =====================================================


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


MODEL_PATH = os.path.join(
    BASE_DIR,
    "capacitor_health_model.keras"
)


SCALER_PATH = os.path.join(
    BASE_DIR,
    "health_scaler.pkl"
)





# =====================================================
# LOAD MODEL
# =====================================================


print("Loading AI capacitor health model...")


model = tf.keras.models.load_model(
    MODEL_PATH
)


print("Loading scaler...")


scaler = joblib.load(
    SCALER_PATH
)


print("AI Model Ready")






# =====================================================
# PREDICT FUNCTION
# =====================================================


def predict_health(features):


    """

    Input:

    [
    voltage,
    current,
    reactive_power,
    pf,
    temperature,
    age,
    switch
    ]

    Output:

    Health %

    """



    input_data = np.array(

        [features],

        dtype=float

    )



    # scale input

    scaled = scaler.transform(

        input_data

    )



    # prediction

    prediction = model.predict(

        scaled,

        verbose=0

    )



    health = float(

        prediction[0][0]

    )



    # limit

    health = max(

        0,

        min(

            100,

            health

        )

    )


    return round(

        health,

        2

    )