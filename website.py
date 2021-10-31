import base64
import io
import time
from csv import DictWriter
from datetime import datetime, timedelta

# import closed_loop_3

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_daq as daq
import dash_html_components as html
import plotly.graph_objs as go
from apscheduler.schedulers.background import BackgroundScheduler
from dash.dependencies import Input, Output, State
from plotly.subplots import make_subplots


# %%

import numpy as np


def closed_loop_3():
    # ser=serial.Serial('COM8',115200)
    # ser.timeout=1
    # try:
    #     ser.close()

    #     ser.open()
    # except Exception:
    #     ser.close()
    #     ser.open()
    # csvl=[]
    k = 0
    Nsamples = 100
    templ = []
    temp_meas = []

    gi_1 = 0.062
    i0_1 = -109.69
    gi_2n = 0.0432
    i0_2n = -77.31
    gi_2p = 0.0607
    i0_2p = -108.15
    gi_3n = 0.0492
    i0_3n = -87.338
    gi_3p = 0.0693
    i0_3p = -123.33

    zer_i2n = -i0_2n / gi_2n
    zer_i2p = -i0_2p / gi_2p
    zer_i2 = (zer_i2n + zer_i2p) / 2
    zer_i3n = -i0_3n / gi_3n
    zer_i3p = -i0_3p / gi_3p
    zer_i3 = (zer_i3n + zer_i3p) / 2

    kadcv_1 = 7.4531
    adcv1_0 = +7.9142
    kadcv_2 = 7.3441
    adcv2_0 = -3.8098
    kadcv_3 = 7.2585
    adcv3_0 = 9.542

    gv_1 = 1 / kadcv_1
    v0_1 = -adcv1_0 / kadcv_1
    gv_2 = 1 / kadcv_2
    v0_2 = -adcv2_0 / kadcv_2
    gv_3 = 1 / kadcv_3
    v0_3 = -adcv3_0 / kadcv_3

    V3_offset = 2
    V2_offset = 2
    V1_offset = 2
    # I3_offset=0.4;
    # I2_offset=0.4;
    # I1_offset=0.4;
    Imax = 50
    Vmax = 100

    Nvar = 8
    Nbytes = 2 + Nvar * 2

    global dictoflist

    # dictoflist={'Phi12':[1],'Phi13':[2],'V1_adc':[3],'V2_adc':[4],'V3_adc':[5],'I1_adc':[6],'I2_adc':[7],'I3_adc':[8]}
    # print(dictoflist)
    try:
        # while True:

        # s=ser.read(Nbytes)
        # if len(list(s))==Nbytes:
        #     if k<=Nsamples:
        #         templ=[]
        #         for i in range(Nvar):
        #             templ.append(struct.unpack("<H",s[1+2*i:2*(i+1)+1],)[0])
        templ = [10, 20, 30, 40, 50, 60, 180, 180]
        temp_meas.append(templ)
        k = k + 1

        # else:

        measures_mean = np.mean(temp_meas, 0)
        I3_adc = np.round(measures_mean[0] / 10 - Imax, 2)
        I2_adc = np.round(measures_mean[1] / 10 - Imax, 2)
        I1_adc = np.round(measures_mean[2] / 10 - Imax, 2)
        V3_adc = np.round(measures_mean[3] / 10 - Vmax, 2)
        V2_adc = np.round(measures_mean[4] / 10 - Vmax, 2)
        V1_adc = np.round(measures_mean[5] / 10 - Vmax, 2)

        if I3_adc < zer_i3:
            I3 = np.round(gi_3n * I3_adc + i0_3n, 2)
        else:
            I3 = np.round(gi_3p * I3_adc + i0_3p, 2)

        if I2_adc <= zer_i2:
            I2 = np.round(gi_2n * I2_adc + i0_2n, 2)
        else:
            I2 = np.round(gi_2p * I2_adc + i0_2p, 2)

        I1 = np.round(gi_1 * I1_adc + i0_1, 2)

        # I3=np.round(gi_3*measures_mean[0]+i0_3+I3_offset,2)
        # I2=np.round(gi_2*measures_mean[1]+i0_2+I2_offset,2)
        # I1=np.round(gi_1*measures_mean[2]+i0_1+I1_offset,2)
        V3 = np.round(gv_3 * V3_adc + v0_3 + V3_offset, 2)
        V2 = np.round(gv_2 * V2_adc + v0_2 + V2_offset, 2)
        V1 = np.round(gv_1 * V1_adc + v0_1 + V1_offset, 2)
        Phi12 = np.round(measures_mean[6] - 90, 2)
        Phi13 = np.round(measures_mean[7] - 90, 2)
        # # measures_std=np.std(temp_meas,0)
        # results=[Phi12,Phi13,V1_adc,V2_adc,V3_adc,I1_adc,I2_adc,I3_adc]

        # dictoflist={'Phi12':[Phi12],'Phi13':[Phi13],'V1_adc':[V1_adc],'V2_adc':[V2_adc],'V3_adc':[V3_adc],'I1_adc':[I1_adc],'I2_adc':[I2_adc],'I3_adc':[I3_adc]}
        dictoflist["phi12"].append(Phi12)
        dictoflist["phi13"].append(Phi13)
        dictoflist["V1"].append(V1_adc)
        dictoflist["V2"].append(V2_adc)
        dictoflist["V3"].append(V3_adc)
        dictoflist["I1"].append(I1_adc)
        dictoflist["I2"].append(I2_adc)
        dictoflist["I3"].append(I3_adc)

        # dictoflist={'Phi12':[1],'Phi13':[2],'V1_adc':[3],'V2_adc':[4],'V3_adc':[5],'I1_adc':[6],'I2_adc':[7],'I3_adc':[8]}
        # print(dictoflist)
        # •     print(measures_mean)

        # csvl.append(results)

        temp_meas = []
        k = 0

    # if s[1]==1:
    #     csvl.append(s[2:-1])
    except Exception as e:
        print(e)
        pass


# %% Setup

dictoflist = dict()
dictoflist = {  ## pour read  et récuperer les valeurs
    "phi12": [],
    "phi13": [],
    "V1": [],
    "V2": [],
    "V3": [],
    "I1": [],
    "I2": [],
    "I3": [],
}
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css", dbc.themes.GRID]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

write_dict = dict()
result = []

fig = go.Figure(data=[go.Scatter(x=[], y=[])])

# %% Layout

tab_style_div1 = {
    "textAlign": "left",
    "padding": "70px 0px",
    "position": "absolute",
    "height": "0%",
    "width": "0%",
}

tab_style_div2 = {"margin-right": "100px", "padding": "22px 0px"}


style_bouton = {"marginTop": 20, "marginBottom": 15}

style_hide_div = {"display": "none"}

app.layout = html.Div(
    [
        dcc.Download(id="download-dataframe-csv"),
        html.Div(id="hidden", style=style_hide_div),
        html.Div(id="hidden1", style=style_hide_div),
        html.Div(id="hidden2", style=style_hide_div),
        html.Div(id="start_hidden", style=style_hide_div),
        html.Div(id="stop_hidden", style=style_hide_div),
        html.Div(id="stop_start_triggerd", style=style_hide_div),
        html.Div(id="hidden5"),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            "Mode: ",
                            html.Button("v2v", id="btn-nclicks-1", n_clicks=0),
                            html.Button("g2v", id="btn-nclicks-2", n_clicks=0),
                            html.Button("v26", id="btn-nclicks-3", n_clicks=0),
                            html.Div(
                                id="container-button-timestamp", style=style_hide_div
                            ),
                        ],
                        style={"marginTop": 20, "marginBottom": 15},
                    ),
                    width="auto",
                ),
                dbc.Col(
                    html.Div(
                        [
                            "Frequence: ",
                            dcc.Input(
                                id="frequence",
                                value=0,
                                type="number",
                                debounce=True,
                            ),
                            html.Div(id="number_freq", style=style_hide_div),
                        ],
                        style={"marginTop": 20, "marginBottom": 15},
                    ),
                    width="auto",
                ),
                dbc.Col(
                    html.Button(
                        "start measurement",
                        id="btn_mesure",
                        n_clicks=0,
                        style={"marginTop": 20, "marginBottom": 15},
                    ),
                    width="auto",
                ),
                dbc.Col(
                    html.Button(
                        "stop measurement",
                        id="btn_stop",
                        n_clicks=0,
                        style={"marginTop": 20, "marginBottom": 15},
                    ),
                    width="auto",
                ),
                dbc.Col(
                    html.Button(
                        "start saving",
                        id="btn_csv",
                        n_clicks=0,
                        style={"marginTop": 20, "marginBottom": 15},
                    ),
                    width="auto",
                ),
                dbc.Col(
                    html.Div(
                        [
                            daq.BooleanSwitch(
                                id="boolean_switch",
                                on=False,
                                label=" start_control ",
                                labelPosition="left",
                            ),
                            html.Div(id="boolean-switch-output", style=style_hide_div),
                        ],
                        style={"marginTop": 20, "marginBottom": 15},
                    ),
                    width="auto",
                ),
                dbc.Col(
                    html.Div(
                        [
                            daq.BooleanSwitch(
                                id="closed_loop",
                                on=True,
                                label=" closed_loop ",
                                labelPosition="left",
                            ),
                            html.Div(
                                id="is-closed-switch-output", style=style_hide_div
                            ),
                        ],
                        style={"marginTop": 20, "marginBottom": 15},
                    ),
                    width="auto",
                ),
                dbc.Col(
                    html.Div(id="div_fi1213"),
                ),
            ],
            style={"flex-wrap": "nowrap"},
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            "Voffset_1: ",
                            dcc.Input(
                                id="Voffset_1",
                                value=0,
                                type="number",
                                debounce=True,
                            ),
                            html.Div(id="Voffset1", style=style_hide_div),
                            "Voffset_2: ",
                            dcc.Input(
                                id="Voffset_2",
                                value=0,
                                type="number",
                                debounce=True,
                            ),
                            html.Div(id="Voffset2", style=style_hide_div),
                            "Voffset_3: ",
                            dcc.Input(
                                id="Voffset_3",
                                value=0,
                                type="number",
                                debounce=True,
                            ),
                            html.Div(id="Voffset3", style=style_hide_div),
                            "ioffset_1: ",
                            dcc.Input(
                                id="ioffset_1",
                                value=0,
                                type="number",
                                debounce=True,
                            ),
                            html.Div(id="ioffset1", style=style_hide_div),
                            "ioffset_2: ",
                            dcc.Input(
                                id="ioffset_2",
                                value=0,
                                type="number",
                                debounce=True,
                            ),
                            html.Div(id="ioffset2", style=style_hide_div),
                            "ioffset_3: ",
                            dcc.Input(
                                id="ioffset_3",
                                value=0,
                                type="number",
                                debounce=True,
                            ),
                            html.Div(id="ioffset3", style=style_hide_div),
                        ],
                        style={"marginTop": 20, "marginBottom": 15},
                    ),
                ),
                dbc.Col(
                    html.Button(
                        "reset_control",
                        id="btn_reset",
                        n_clicks=0,
                        style={
                            "marginTop": 20,
                            "marginBottom": 15,
                            "margin-right": "10px",
                        },
                    ),
                    width="auto",
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Button(
                        "send",
                        id="btn_send",
                        n_clicks=0,
                        style={
                            "marginTop": 20,
                            "marginBottom": 15,
                            "margin-right": "10px",
                        },
                    ),
                    width="auto",
                ),
                html.Div(id="send", style=style_hide_div),
            ]
        ),
        dcc.Graph(id="graph1", figure=fig, style={}),
        dcc.Dropdown(
            id="value_graph",
            options=[
                {"label": "φ12", "value": "phi12"},
                {"label": "φ13", "value": "phi13"},
                {"label": "V1", "value": "V1"},
                {"label": "V2", "value": "V2"},
                {"label": "V3", "value": "V3"},
                {"label": "I1", "value": "I1"},
                {"label": "I2", "value": "I2"},
                {"label": "I3", "value": "I3"},
            ],
            multi=True,
            style={"margin-right": "80%", "margin-left": "5px"},
        ),
        html.Div(
            [
                html.Button("Download graph", id="btnhistss", style={"margin": 10}),
                dcc.Download(id="downloadhistss"),
            ],
        ),
        html.Div(
            [
                dcc.Checklist(
                    id="CheckID",
                    options=[
                        {"label": "φ12", "value": "phi12"},
                        {"label": "φ13", "value": "phi13"},
                        {"label": "V1", "value": "V1"},
                        {"label": "V2", "value": "V2"},
                        {"label": "V3", "value": "V3"},
                        {"label": "I1", "value": "I1"},
                        {"label": "I2", "value": "I2"},
                        {"label": "I3", "value": "I3"},
                    ],
                    inputStyle={"margin-left": "20px", "margin-right": "5px"},
                    labelStyle={"display": "inline-block"},
                )
            ],
            style={"width": "50%", "display": "inline-block"},
        ),
        html.P("Choose one graph:", style={"margin-left": "10px"}),
        dcc.RadioItems(id="radio", options=[], style={"margin-left": "35px"}),
        dcc.Interval(
            id="interval-component",
            interval=1 * 500,  # actualiser le callback update_graphe chaque 0.5 seconds
            n_intervals=0,
        ),
    ]
)


# %% callback pour changer le mode
@app.callback(
    Output("container-button-timestamp", "children"),
    Input("btn-nclicks-1", "n_clicks"),
    Input("btn-nclicks-2", "n_clicks"),
    Input("btn-nclicks-3", "n_clicks"),
)
def mode(btn1, btn2, btn3):
    changed_id = [p["prop_id"] for p in dash.callback_context.triggered][0]
    if "btn-nclicks-1" in changed_id:
        write_dict.update({"mode": 0})
        return 0
    elif "btn-nclicks-2" in changed_id:
        write_dict.update({"mode": 1})
        return 1
    elif "btn-nclicks-3" in changed_id:
        write_dict.update({"mode": 2})
        return 2
    else:
        return ""


#%% callback pour exporter les données en temps réel en format csv
@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    Input("value_graph", "options"),  # les valeurs pour read (phi12,phi13,V1,etc.)
    prevent_initial_call=True,
)
def saving(n_clicks, options_values):
    list_options = []
    for i in range(len(options_values)):
        list_options.append(list(options_values[i].values())[1])
    now = datetime.now()
    download_buffer = io.StringIO()
    writer = DictWriter(download_buffer, list_options)  ## colonnes
    writer.writeheader()

    for i in range(
        len(dictoflist["phi12"])
    ):  # j'ai choisi phi12 par hasard car on a chaque fois la même longeur pour toutes les valeurs
        writer.writerows(
            [
                {
                    "phi12": dictoflist["phi12"][i],
                    "phi13": dictoflist["phi13"][i],
                    "V1": dictoflist["V1"][i],
                    "V2": dictoflist["V2"][i],
                    "V3": dictoflist["V3"][i],
                    "I1": dictoflist["I1"][i],
                    "I2": dictoflist["I2"][i],
                    "I3": dictoflist["I3"][i],
                },
            ]
        )
    content = download_buffer.getvalue()
    # print(content)
    download_buffer.close()
    return dict(content=content, filename=now.strftime("%Y-%m-%d_%H:%M") + "_" + ".csv")


#%% callback pour le switch start_control


@app.callback(
    Output("boolean-switch-output", "children"), [Input("boolean_switch", "on")]
)
def start_control(on):
    if on == False:
        print(0)
        write_dict.update({"start_control": 0})
        # print(closed_loop_3.closed_loop_3())
        return 0
    else:
        write_dict.update({"start_control": 1})
        print(1)
        return 1


#%% callback pour frequence input


@app.callback(
    Output("number_freq", "children"),
    Input("frequence", "value"),
)
def frequence_value(val):
    if val == None:
        return 0
    print(val)
    write_dict.update({"frequence_value": val})
    return val


#%% callback pour le switch is_closed_loop
@app.callback(
    Output("is-closed-switch-output", "children"), [Input("closed_loop", "on")]
)
def is_closed_loop(on):
    if on == False:
        write_dict.update({"is_closed_loop": 0})
        return 0
    else:
        write_dict.update({"is_closed_loop": 1})
        return 1


#%% callback pour switcher entre k et phi
@app.callback(
    Output("div_fi1213", "children"),
    Input("closed_loop", "on"),
)
def fi_12_13(on):
    if on == True:  # affiche kp,ki
        return dbc.Col(
            html.Div(
                [
                    "kp: ",
                    dcc.Input(
                        id="kp",
                        value=0,
                        type="number",
                        debounce=True,
                    ),
                    " ki: ",
                    dcc.Input(
                        id="ki",
                        value=0,
                        type="number",
                        debounce=True,
                    ),
                ],
                style={"marginTop": 10, "marginBottom": 15, "margin-left": 15},
            )
        )
    else:  # affiche phi12,phi13
        return dbc.Col(
            html.Div(
                [
                    "φ12c: ",
                    dcc.Input(
                        id="fi12c",
                        value=0,
                        type="number",
                        debounce=True,
                    ),
                    " φ13c: ",
                    dcc.Input(
                        id="fi13c",
                        value=0,
                        type="number",
                        debounce=True,
                    ),
                ],
                style={"marginTop": 5, "marginBottom": 15},
            )
        )


#%%
@app.callback(
    Output("hidden", "children"),
    Input("fi12c", "value"),
    Input("fi13c", "value"),
)
def fi_values(fi12, fi13):
    write_dict.update({"fi12": fi12})
    write_dict.update({"fi13": fi13})
    return fi12, fi13


#%%
@app.callback(
    Output("hidden2", "children"),
    Input("kp", "value"),
    Input("ki", "value"),
)
def k_values(kp, ki):
    # print(kp, ki)
    write_dict.update({"kp": kp})
    write_dict.update({"ki": ki})
    return kp, ki


#%%
@app.callback(
    Output("Voffset1", "children"),
    Output("Voffset2", "children"),
    Output("Voffset3", "children"),
    Output("ioffset1", "children"),
    Output("ioffset2", "children"),
    Output("ioffset3", "children"),
    Input("Voffset_1", "value"),
    Input("Voffset_2", "value"),
    Input("Voffset_3", "value"),
    Input("ioffset_1", "value"),
    Input("ioffset_2", "value"),
    Input("ioffset_3", "value"),
)
def offset_values(Voffset1, Voffset2, Voffset3, ioffset1, ioffset2, ioffset3):
    write_dict.update({"Voffset_1": Voffset1})
    write_dict.update({"Voffset_2": Voffset2})
    write_dict.update({"Voffset_3": Voffset3})
    write_dict.update({"ioffset_1": ioffset1})
    write_dict.update({"ioffset_2": ioffset2})
    write_dict.update({"ioffset_3": ioffset3})
    return Voffset1, Voffset2, Voffset3, ioffset1, ioffset2, ioffset3


#%%
@app.callback(
    Output("hidden1", "children"),
    Input("btn_reset", "n_clicks"),
)
def reset_bouton(n_clicks):
    if n_clicks > 0:
        write_dict.update({"reset_bouton": 1})
        print(write_dict)
        time.sleep(0.5)
        write_dict.update({"reset_bouton": 0})
        print(write_dict)
        return 0


#%% callback pour start measurement

scheduler = BackgroundScheduler()


@app.callback(
    Output("start_hidden", "children"),
    Input("btn_mesure", "n_clicks"),
)
def start_bouton(n_clicks):
    if n_clicks > 0:
        global dictoflist
        dictoflist = {
            "phi12": [],
            "phi13": [],
            "V1": [],
            "V2": [],
            "V3": [],
            "I1": [],
            "I2": [],
            "I3": [],
        }
        scheduler.add_job(
            closed_loop_3, "interval", seconds=0.5, id="my_job"
        )  # éxecute le script closed_loop_3 chaque 0.5 seconds
        scheduler.start()
        return 0


#%% callback pour stopper la mesure
@app.callback(
    Output("stop_hidden", "children"),
    Input("btn_stop", "n_clicks"),
)
def stop_bouton(n_clicks):

    if n_clicks > 0:

        scheduler.remove_job("my_job")  # arrêter le job qui éxecute le script closed_loop_3
        return 0


#%% callback pour write in dsp 
@app.callback(
    Output("send", "children"),
    Input("btn_send", "n_clicks"),
)
def send_bouton(n_clicks):

    write_list = list(write_dict.values())
    print(write_list)
    return write_list


#%% callback pour savoir si on est en mode off/on pour la mesure (pour éviter les bruits dans le shell)
@app.callback(
    Output("stop_start_triggerd", "children"),
    Input("btn_mesure", "n_clicks"),
    Input("btn_stop", "n_clicks"),
)
def stop_triggered(n_clicks_stop, n_clicks_start):

    ctx = dash.callback_context
    c = ctx.triggered[0]["prop_id"].split(".")[0]

    if c == "btn_mesure":
        return 1
    else:
        return 0


#%% callback pour afficher les graphes avec les données en temps réel qu'on récupere


@app.callback(
    Output("graph1", "figure"),
    Output("radio", "options"),
    [
        Input("value_graph", "value"),
        Input("value_graph", "options"),
        Input("CheckID", "options"),
        Input("CheckID", "value"),
        Input("radio", "value"),
        Input("radio", "options"),
        Input("interval-component", "n_intervals"),
        State("stop_start_triggerd", "children"),
    ],
    prevent_initial_call=True,
)
def update_graph(
    value,
    options,
    check_options,
    value_check,
    radio_value,
    radio_opt,
    n,
    start_triggered,
):
    radio_options = []
    if start_triggered:  # si on a appuyé sur le bouton start measurment
        list_options = []
        list_options_check = []
        fig_hist = go.Figure()
        for i in range(len(options)):
            list_options.append(
                list(options[i].values())[1]
            )  # une liste avec les valeurs de read

        for i in range(len(check_options)):
            list_options_check.append(list(check_options[i].values())[1])

        # print("list_options" + str(list_options))
        # print("list_options_check" + str(list_options_check))

        if value != None:
            if len(value) == 1:  # si on a qu'un seul graphe
                fig_hist.add_trace(go.Scatter(y=dictoflist[value[0]], name=value[0]))
                if value_check != None and value_check != []:
                    for i in range(len(value_check)):
                        # print("check" + str(value_check))
                        fig_hist.add_trace(
                            go.Scatter(
                                y=dictoflist[value_check[i]], name=value_check[i]
                            )
                        )
            else:  # si on en a plusieurs
                fig_hist = make_subplots(rows=1, cols=len(value))
                cpt = 0
                for i in range(len(value)):
                    trace = go.Scatter(y=dictoflist[value[i]], name=value[i])
                    fig_hist.append_trace(trace, 1, 1 + cpt)
                    fig_hist.update_xaxes(title_text=value[i], row=1, col=1 + cpt)
                    radio_options.append(
                        {"label": value[i], "value": value[i]})  # liste des graphe sélectionnés
                    cpt += 1

                if (value_check != None and value_check != [] and radio_value != None):  # ajouter des valeurs sur le graphe sélectionné
                    for i in range(len(value_check)):
                        # print("check" + str(value_check))
                        fig_hist.append_trace(
                            go.Scatter(
                                y=dictoflist[value_check[i]], name=value_check[i]
                            ),1,1 + value.index(radio_value),)
        return fig_hist, radio_options
    else: 
        return "", radio_options


#%% callback pour télecharger le graphe en format html
@app.callback(
    Output("downloadhistss", "data"),
    [Input("btnhistss", "n_clicks"), State("graph1", "figure")],
    prevent_initial_call=True,
)
def download(n_clicks, f):
    fig = go.Figure(f)
    mybuff = io.StringIO()
    fig.write_html(mybuff, include_plotlyjs="cdn")
    data_value = mybuff.getvalue().encode()
    mybuff.close()
    content = base64.b64encode(data_value).decode()
    return dict(content=content, filename="plot.html", base64=True)


#%%
if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8071, threaded=True)
