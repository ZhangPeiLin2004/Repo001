from flask import Flask, render_template, request
import pandas as pd
import os
import plotly.express as px

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
temp_path = os.path.join(BASE_DIR, 'data', 'Temperatures.csv')
landsea_path = os.path.join(BASE_DIR, 'data', 'landsea_temp.csv')
df = pd.read_csv(temp_path)
df.columns = df.columns.str.strip()

df_new = pd.read_csv(landsea_path, comment="#")
df_new.columns = df_new.columns.str.strip()

year_columns = [str(year) for year in range(1961, 2025)]
df_long = df.melt(
    id_vars=["Country"],
    value_vars=year_columns,
    var_name="Year",
    value_name="Temperature Change"
)
df_long["Year"] = df_long["Year"].astype(int)

df_new["Anomaly"] = df_new["Anomaly"].replace(-999, pd.NA)
df_new["LS_Date"] = pd.to_datetime(df_new["Date"], format="%Y%m")
df_new["LS_Year"] = df_new["LS_Date"].dt.year

fig_new = px.line(
    df_new,
    x="LS_Year",
    y="Anomaly",
    title="Global Land and Ocean Average Temperature Anomalies (1850–Present)",
    markers=True
)
fig_new.update_layout(template="plotly_white")

graph_html_new = fig_new.to_html(full_html=False)

all_countries = sorted(df_long["Country"].dropna().unique().tolist())

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/data", methods=["GET", "POST"])
def data():
    selected_country = request.form.get("country", all_countries[0])

    # Filter data for selected country
    country_data = df_long[df_long["Country"] == selected_country]

    # Generate temperature change line plot
    fig = px.line(
        country_data,
        x="Year",
        y="Temperature Change",
        title=f"Temperature Change in {selected_country} (1961–2024)",
        markers=True
    )
    fig.update_layout(template="plotly_white")

    graph_html = fig.to_html(full_html=False)

    # Existing second dataset graph (Global Land and Ocean Temperature Anomalies)
    graph_html_new = fig_new.to_html(full_html=False)

    return render_template(
        "data.html",
        countries=all_countries,
        selected=selected_country,
        graph=graph_html,
        graph_new=graph_html_new
    )

if __name__ == "__main__":
    app.run(debug=True)