import marimo

__generated_with = "0.13.8"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # Exploratory flight data analysis

    **By**: Gustavo Alvarado

    **Drone**: RB-01

    **Flight log**: 19-07-2023

    ## 1. Scouting data
    """
    )
    return


@app.cell
def _():
    import marimo as mo
    import polars as pl
    return mo, pl


@app.cell
def _(pl):
    df = pl.read_csv("crash.csv")
    df.glimpse()
    return (df,)


@app.cell
def _(df):
    print(f"Este dataset tiene {len(df)} filas.")
    df_1 = df.fill_nan(None)
    df_1.null_count()
    return (df_1,)


@app.cell
def _(df_1):
    df_2 = df_1.fill_null(strategy="zero")
    new_names = ["time", "voltage", "current", "speed", "altitude"]
    df_2.columns = new_names
    return (df_2,)


@app.cell
def _(df_2, pl):
    df_3 = df_2.with_columns(
        pl.col("time").cast(pl.Int64).cast(pl.Duration(time_unit="ms"))
    )
    df_3 = df_3.with_columns(
        (pl.datetime(1970, 1, 1) + pl.col("time")).alias("visual_time")
    )
    df_3.glimpse()
    return (df_3,)


@app.cell
def _(df_3, pl):
    df_4 = df_3.with_columns(
        (pl.col("voltage") * pl.col("current") / 1000.0).alias("power")
    )
    df_4.describe()
    return (df_4,)


@app.cell
def _():
    import plotly.express as px
    return (px,)


@app.cell
def _():
    from collections import namedtuple
    Labels = namedtuple('Labels', ['time', 'power', 'aspd', 'alt'])
    lbl = Labels(time="Tiempo transcurrido (HH:MM:SS)", power="Power [kW]", aspd="Airspeed [m/s]", alt="Altitude [m.s.n.m.]")
    print(lbl.time)
    return (lbl,)


@app.cell
def _(df_4, px):
    _fig = px.line(df_4, x="visual_time", y="altitude", title="Altitude Timeline")
    _fig.update_xaxes(tickformat="%H:%M:%S", type="date")
    _fig.show()
    return


@app.cell
def _(df_4, lbl, px):
    _fig = px.line(
        df_4,
        x="visual_time",
        y="power",
        title="Power over Flight",
        labels={"Power": lbl.power},
    )
    _fig.update_xaxes(tickformat="%H:%M:%S", type="date")
    _fig.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## 2. Climb stage""")
    return


@app.cell
def _(df_4, pl):
    df_5 = df_4.with_columns(
        (
            (pl.col("altitude") - pl.col("altitude").mean()) / pl.col("altitude").std()
        ).alias("z_altitude")
    )
    return (df_5,)


@app.cell
def _(df_5, pl):
    reach_altitude = df_5.filter(
        pl.col("z_altitude") >= df_5.max()["z_altitude"][0] - 0.2
    ).head(1)
    reach_altitude["time"][0]
    return (reach_altitude,)


@app.cell
def _(df_5, pl):
    change_altitude = df_5.filter(
        pl.col("z_altitude") >= df_5.min()["z_altitude"][0] + 0.35
    ).head(1)
    change_altitude["time"][0]
    return


@app.cell
def _(df_5, pl, reach_altitude):
    reach_altitude_time = reach_altitude["time"][0]
    _q = df_5.lazy().filter(
        pl.col("time") < reach_altitude_time, pl.col("current") >= 8
    )
    df_takeoff = _q.collect()
    df_takeoff.glimpse()
    return df_takeoff, reach_altitude_time


@app.cell
def _(df_takeoff, pl):
    _df_write = df_takeoff.with_columns(pl.col("time").dt.total_milliseconds())
    _df_write = _df_write.select(
        pl.col(["time", "voltage", "current", "speed", "altitude"])
    )
    _df_write.write_csv("19-07-2023 - VTOL Takeoff and Climb.csv")
    return


@app.cell
def _():
    import plotly.graph_objects as go
    return (go,)


@app.cell
def _(df_takeoff):
    plot_x = df_takeoff["visual_time"]
    plot_y1 = df_takeoff["altitude"]
    plot_y2 = df_takeoff["speed"]
    plot_y3 = df_takeoff["power"]
    plot_title = "Full Climb Visualization"
    return plot_title, plot_x, plot_y1, plot_y2, plot_y3


@app.cell
def _(go, lbl, plot_title, plot_x, plot_y1, plot_y2, plot_y3):
    _fig = go.Figure()
    _fig.add_trace(
        go.Scatter(
            x=plot_x, y=plot_y1, mode="lines", line=dict(color="red"), name="Altitude"
        )
    )
    _fig.add_trace(
        go.Scatter(
            x=plot_x,
            y=plot_y2,
            yaxis="y2",
            mode="lines",
            line=dict(color="orange"),
            name="Airspeed",
        )
    )
    _fig.add_trace(
        go.Scatter(
            x=plot_x,
            y=plot_y3,
            yaxis="y3",
            mode="lines",
            line=dict(color="purple"),
            name="Power",
        )
    )
    _fig.update_layout(
        title=plot_title,
        xaxis_title=lbl.time,
        yaxis=dict(title=lbl.alt, color="red"),
        yaxis2=dict(
            title=lbl.aspd, overlaying="y", side="right", color="orange"
        ),
        yaxis3=dict(
            title=lbl.power,
            overlaying="y",
            anchor="free",
            autoshift=True,
            color="purple",
        ),
    )
    _fig.update_xaxes(tickformat="%H:%M:%S", type="date")
    _fig.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### 2.1. Filtering VTOL Takeoff""")
    return


@app.cell
def _(df_5, pl, reach_altitude_time):
    _q = df_5.lazy().filter(
        pl.col("time") < reach_altitude_time,
        pl.col("altitude") < 59,
        pl.col("current") >= 8,
    )
    df_takeoff_1 = _q.collect()
    plot_x_1 = df_takeoff_1["visual_time"]
    plot_y1_1 = df_takeoff_1["altitude"]
    plot_y2_1 = df_takeoff_1["speed"]
    plot_y3_1 = df_takeoff_1["power"]
    plot_title_1 = "VTOL Takeoff"
    return (
        df_takeoff_1,
        plot_title_1,
        plot_x_1,
        plot_y1_1,
        plot_y2_1,
        plot_y3_1,
    )


@app.cell
def _(go, lbl, plot_title_1, plot_x_1, plot_y1_1, plot_y2_1, plot_y3_1):
    _fig = go.Figure()
    _fig.add_trace(
        go.Scatter(
            x=plot_x_1,
            y=plot_y1_1,
            mode="lines",
            line=dict(color="red"),
            name="Altitude",
        )
    )
    _fig.add_trace(
        go.Scatter(
            x=plot_x_1,
            y=plot_y2_1,
            yaxis="y2",
            mode="lines",
            line=dict(color="orange"),
            name="Airspeed",
        )
    )
    _fig.add_trace(
        go.Scatter(
            x=plot_x_1,
            y=plot_y3_1,
            yaxis="y3",
            mode="lines",
            line=dict(color="purple"),
            name="Power",
        )
    )
    _fig.update_layout(
        title=plot_title_1,
        xaxis_title=lbl.time,
        yaxis=dict(title=lbl.alt, color="red"),
        yaxis2=dict(
            title=lbl.aspd, overlaying="y", side="right", color="orange"
        ),
        yaxis3=dict(
            title=lbl.power,
            overlaying="y",
            anchor="free",
            autoshift=True,
            color="purple",
        ),
    )
    _fig.update_xaxes(tickformat="%H:%M:%S", type="date")
    _fig.show()
    return


@app.cell
def _(df_takeoff_1):
    df_takeoff_1["voltage", "current", "power", "speed", "altitude"].describe()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### 2.2. Filtering Climb in Cruise""")
    return


@app.cell
def _(df_5, pl, reach_altitude_time):
    _q = df_5.lazy().filter(
        pl.col("time") < reach_altitude_time, pl.col("altitude") >= 59
    )
    df_climb = _q.collect()
    plot_x_2 = df_climb["visual_time"]
    plot_y1_2 = df_climb["altitude"]
    plot_y2_2 = df_climb["speed"]
    plot_y3_2 = df_climb["power"]
    plot_title_2 = "Climb"
    return df_climb, plot_title_2, plot_x_2, plot_y1_2, plot_y2_2, plot_y3_2


@app.cell
def _(go, lbl, plot_title_2, plot_x_2, plot_y1_2, plot_y2_2, plot_y3_2):
    _fig = go.Figure()
    _fig.add_trace(
        go.Scatter(
            x=plot_x_2,
            y=plot_y1_2,
            mode="lines",
            line=dict(color="red"),
            name="Altitude",
        )
    )
    _fig.add_trace(
        go.Scatter(
            x=plot_x_2,
            y=plot_y2_2,
            yaxis="y2",
            mode="lines",
            line=dict(color="orange"),
            name="Airspeed",
        )
    )
    _fig.add_trace(
        go.Scatter(
            x=plot_x_2,
            y=plot_y3_2,
            yaxis="y3",
            mode="lines",
            line=dict(color="purple"),
            name="Power",
        )
    )
    _fig.update_layout(
        title=plot_title_2,
        xaxis_title=lbl.time,
        yaxis=dict(title=lbl.alt, color="red"),
        yaxis2=dict(
            title=lbl.aspd, overlaying="y", side="right", color="orange"
        ),
        yaxis3=dict(
            title=lbl.power,
            overlaying="y",
            anchor="free",
            autoshift=True,
            color="purple",
        ),
    )
    _fig.update_xaxes(tickformat="%H:%M:%S", type="date")
    _fig.show()
    return


@app.cell
def _(df_climb):
    df_climb["voltage", "current", "power", "speed", "altitude"].describe()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## 3. Cruise stable sample""")
    return


@app.cell
def _(df_5, pl):
    mid_current = df_5.filter(
        pl.col("z_altitude") >= df_5.max()["z_altitude"][0] - 0.2
    ).median()["current"][0]
    df_cummulates = df_5.filter(
        pl.col("z_altitude") > df_5.max()["z_altitude"][0] - 0.25
    ).with_columns(
        pl.col("current")
        .is_between(0.8 * mid_current, 1.2 * mid_current)
        .rle_id()
        .alias("cummulates")
    )
    stable_cummulates = (
        df_cummulates.group_by("cummulates")
        .agg(pl.len().alias("count"))
        .filter(pl.col("cummulates") != 0)
        .top_k(1, by="count")["cummulates"][0]
    )
    df_stable = df_cummulates.filter(pl.col("cummulates") == stable_cummulates).drop(
        "cummulates"
    )
    df_stable.glimpse()
    return (df_stable,)


@app.cell
def _(df_stable, pl):
    _df_write = df_stable.with_columns(pl.col("time").dt.total_milliseconds())
    _df_write = _df_write.select(
        pl.col(["time", "voltage", "current", "speed", "altitude"])
    )
    _df_write.write_csv("19-07-2023 - Cruise flight sample.csv")
    return


@app.cell
def _(df_stable):
    plot_x_3 = df_stable["visual_time"]
    plot_y1_3 = df_stable["altitude"]
    plot_y2_3 = df_stable["speed"]
    plot_y3_3 = df_stable["power"]
    plot_title_3 = "Cruise flight sample"
    return plot_title_3, plot_x_3, plot_y1_3, plot_y2_3, plot_y3_3


@app.cell
def _(go, lbl, plot_title_3, plot_x_3, plot_y1_3, plot_y2_3, plot_y3_3):
    _fig = go.Figure()
    _fig.add_trace(
        go.Scatter(
            x=plot_x_3,
            y=plot_y1_3,
            mode="lines",
            line=dict(color="red"),
            name="Altitude",
        )
    )
    _fig.add_trace(
        go.Scatter(
            x=plot_x_3,
            y=plot_y2_3,
            yaxis="y2",
            mode="lines",
            line=dict(color="orange"),
            name="Airspeed",
        )
    )
    _fig.add_trace(
        go.Scatter(
            x=plot_x_3,
            y=plot_y3_3,
            yaxis="y3",
            mode="lines",
            line=dict(color="purple"),
            name="Power",
        )
    )
    _fig.update_layout(
        title=plot_title_3,
        xaxis_title=lbl.time,
        yaxis=dict(title=lbl.alt, color="red"),
        yaxis2=dict(
            title=lbl.aspd, overlaying="y", side="right", color="orange"
        ),
        yaxis3=dict(
            title=lbl.power,
            overlaying="y",
            anchor="free",
            autoshift=True,
            color="purple",
        ),
    )
    _fig.update_xaxes(tickformat="%H:%M:%S", type="date")
    _fig.show()
    return


@app.cell
def _(df_stable):
    df_stable["voltage", "current", "power", "speed", "altitude"].describe()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## 4. Landing stage""")
    return


@app.cell
def _(df_5, pl):
    last_reached = df_5.filter(
        pl.col("z_altitude") >= df_5.max()["z_altitude"][0] - 0.2
    ).tail(1)
    last_reached_time = last_reached["time"][0]
    _q = df_5.lazy().filter(pl.col("time") > last_reached_time, pl.col("current") > 4)
    df_landing = _q.collect()
    df_landing.glimpse()
    return (df_landing,)


@app.cell
def _(df_landing):
    plot_x_4 = df_landing["visual_time"]
    plot_y1_4 = df_landing["altitude"]
    plot_y2_4 = df_landing["speed"]
    plot_y3_4 = df_landing["power"]
    plot_title_4 = "Full Descent Visualization"
    return plot_title_4, plot_x_4, plot_y1_4, plot_y2_4, plot_y3_4


@app.cell
def _(go, lbl, plot_title_4, plot_x_4, plot_y1_4, plot_y2_4, plot_y3_4):
    _fig = go.Figure()
    _fig.add_trace(
        go.Scatter(
            x=plot_x_4,
            y=plot_y1_4,
            mode="lines",
            line=dict(color="red"),
            name="Altitude",
        )
    )
    _fig.add_trace(
        go.Scatter(
            x=plot_x_4,
            y=plot_y2_4,
            yaxis="y2",
            mode="lines",
            line=dict(color="orange"),
            name="Airspeed",
        )
    )
    _fig.add_trace(
        go.Scatter(
            x=plot_x_4,
            y=plot_y3_4,
            yaxis="y3",
            mode="lines",
            line=dict(color="purple"),
            name="Power",
        )
    )
    _fig.update_layout(
        title=plot_title_4,
        xaxis_title=lbl.time,
        yaxis=dict(title=lbl.alt, color="red"),
        yaxis2=dict(
            title=lbl.aspd, overlaying="y", side="right", color="orange"
        ),
        yaxis3=dict(
            title=lbl.power,
            overlaying="y",
            anchor="free",
            autoshift=True,
            color="purple",
        ),
    )
    _fig.update_xaxes(tickformat="%H:%M:%S", type="date")
    _fig.show()
    return


@app.cell
def _(df_landing):
    df_landing["voltage", "current", "power", "speed", "altitude"].describe()
    return


if __name__ == "__main__":
    app.run()
