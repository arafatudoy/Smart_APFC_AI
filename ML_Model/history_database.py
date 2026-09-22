import pandas as pd
import os


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


history_file = os.path.join(
    BASE_DIR,
    "ML_Model",
    "history.csv"
)



def save_history(data):

    df = pd.DataFrame(
        [data]
    )


    if os.path.exists(history_file):

        old = pd.read_csv(
            history_file
        )

        df = pd.concat(
            [
                old,
                df
            ],
            ignore_index=True
        )


    df.to_csv(
        history_file,
        index=False
    )