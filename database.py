from sqlalchemy import create_engine, text
import pandas as pd


class OptionDatabase:

    def __init__(
        self,
        db_name="option_chain.db"
    ):

        self.engine = create_engine(
            f"sqlite:///{db_name}",
            echo=False
        )

        self.create_tables()

    # --------------------------------------------------
    # CREATE TABLES
    # --------------------------------------------------

    def create_tables(self):

        query = """
        CREATE TABLE IF NOT EXISTS option_history (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            timestamp TEXT,

            symbol TEXT,

            spot REAL,

            strike REAL,

            call_oi INTEGER,
            put_oi INTEGER,

            call_change_oi INTEGER,
            put_change_oi INTEGER,

            call_volume INTEGER,
            put_volume INTEGER,

            call_iv REAL,
            put_iv REAL,

            call_ltp REAL,
            put_ltp REAL

        );
        """

        with self.engine.begin() as conn:

            conn.execute(
                text(query)
            )

    # --------------------------------------------------
    # SAVE SNAPSHOT
    # --------------------------------------------------

    def save_snapshot(
        self,
        symbol,
        spot,
        df,
        timestamp
    ):

        temp = df.copy()

        temp["timestamp"] = timestamp
        temp["symbol"] = symbol
        temp["spot"] = spot

        temp.rename(
            columns={

                "Strike":
                    "strike",

                "Call_OI":
                    "call_oi",

                "Put_OI":
                    "put_oi",

                "Call_Chg_OI":
                    "call_change_oi",

                "Put_Chg_OI":
                    "put_change_oi",

                "Call_Volume":
                    "call_volume",

                "Put_Volume":
                    "put_volume",

                "Call_IV":
                    "call_iv",

                "Put_IV":
                    "put_iv",

                "Call_LTP":
                    "call_ltp",

                "Put_LTP":
                    "put_ltp"

            },
            inplace=True
        )

        temp.to_sql(
            "option_history",
            self.engine,
            if_exists="append",
            index=False
        )

    # --------------------------------------------------
    # LAST SNAPSHOT
    # --------------------------------------------------

    def get_previous_snapshot(
        self,
        symbol,
        limit=500
    ):

        query = f"""
        SELECT *
        FROM option_history
        WHERE symbol='{symbol}'
        ORDER BY id DESC
        LIMIT {limit}
        """

        try:

            return pd.read_sql(
                query,
                self.engine
            )

        except Exception:

            return pd.DataFrame()

    # --------------------------------------------------
    # SPOT HISTORY
    # --------------------------------------------------

    def get_spot_history(
        self,
        symbol,
        limit=1000
    ):

        query = f"""
        SELECT
            timestamp,
            spot
        FROM option_history
        WHERE symbol='{symbol}'
        ORDER BY id DESC
        LIMIT {limit}
        """

        try:

            df = pd.read_sql(
                query,
                self.engine
            )

            if not df.empty:

                df["timestamp"] = (
                    pd.to_datetime(
                        df["timestamp"]
                    )
                )

            return df

        except Exception:

            return pd.DataFrame()

    # --------------------------------------------------
    # STRIKE HISTORY
    # --------------------------------------------------

    def get_strike_history(
        self,
        symbol,
        strike,
        limit=500
    ):

        query = f"""
        SELECT *
        FROM option_history
        WHERE symbol='{symbol}'
        AND strike={strike}
        ORDER BY id DESC
        LIMIT {limit}
        """

        try:

            df = pd.read_sql(
                query,
                self.engine
            )

            if not df.empty:

                df["timestamp"] = (
                    pd.to_datetime(
                        df["timestamp"]
                    )
                )

            return df

        except Exception:

            return pd.DataFrame()

    # --------------------------------------------------
    # OI SHIFT
    # --------------------------------------------------

    def get_latest_vs_previous(
        self,
        symbol
    ):

        query = f"""
        SELECT *
        FROM option_history
        WHERE symbol='{symbol}'
        ORDER BY id DESC
        """

        try:

            df = pd.read_sql(
                query,
                self.engine
            )

            if len(df) < 2:

                return (
                    pd.DataFrame(),
                    pd.DataFrame()
                )

            timestamps = (
                df["timestamp"]
                .drop_duplicates()
                .tolist()
            )

            if len(timestamps) < 2:

                return (
                    pd.DataFrame(),
                    pd.DataFrame()
                )

            latest_ts = timestamps[0]
            previous_ts = timestamps[1]

            latest = (
                df[
                    df["timestamp"]
                    ==
                    latest_ts
                ]
            )

            previous = (
                df[
                    df["timestamp"]
                    ==
                    previous_ts
                ]
            )

            return (
                latest,
                previous
            )

        except Exception:

            return (
                pd.DataFrame(),
                pd.DataFrame()
            )

    # --------------------------------------------------
    # CLEANUP OLD DATA
    # --------------------------------------------------

    def cleanup_old_data(
        self,
        keep_rows=100000
    ):

        query = f"""
        DELETE FROM option_history
        WHERE id NOT IN
        (
            SELECT id
            FROM option_history
            ORDER BY id DESC
            LIMIT {keep_rows}
        )
        """

        try:

            with self.engine.begin() as conn:

                conn.execute(
                    text(query)
                )

        except Exception:

            pass

    # --------------------------------------------------
    # DATABASE STATS
    # --------------------------------------------------

    def get_stats(self):

        try:

            query = """
            SELECT
                COUNT(*) as total_rows
            FROM option_history
            """

            df = pd.read_sql(
                query,
                self.engine
            )

            return {

                "rows":
                    int(
                        df.iloc[0][
                            "total_rows"
                        ]
                    )

            }

        except Exception:

            return {

                "rows": 0

            }
        
def get_last_spot(
    self,
    symbol
):

    query = f"""
    SELECT spot
    FROM option_history
    WHERE symbol='{symbol}'
    ORDER BY id DESC
    LIMIT 1
    """

    try:

        df = pd.read_sql(
            query,
            self.engine
        )

        if len(df):

            return (
                float(
                    df.iloc[0]["spot"]
                )
            )

    except:
        pass

    return None