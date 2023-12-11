import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html
from dash.dependencies import ALL, State
from myfuns import (
    genres,
    get_displayed_movies,
    get_popular_movies,
    get_recommended_movies,
)


app = dash.Dash(
    external_stylesheets=[dbc.themes.LUMEN, dbc.icons.BOOTSTRAP],
    suppress_callback_exceptions=True,
)
server = app.server

nav_style = {
    "display": "flex",
    "flexDirection": "row",
    "justifyContent": "space-between",
    "padding": "40px",
}

link_style = {":hover": "#df6919", "border-radius": "20px", "margin-right": "20px"}


def pull_movie_image(movie_id, movie_title, with_rating=False):
    return html.Div(
        dbc.Card(
            [
                dbc.CardImg(
                    src=f"https://liangfgithub.github.io/MovieImages/{movie_id}.jpg?raw=true",
                    top=True,
                    style={"borderRadius": "50px"},
                ),
                dbc.CardBody(
                    [
                        html.H6(
                            movie_title,
                            style={"justify-content": "center", "display": "flex"},
                        ),
                    ]
                ),
            ]
            + (
                [
                    dcc.RadioItems(
                        options=[
                            {"label": "1", "value": "1"},
                            {"label": "2", "value": "2"},
                            {"label": "3", "value": "3"},
                            {"label": "4", "value": "4"},
                            {"label": "5", "value": "5"},
                        ],
                        className="text-center",
                        id={"type": "movie_rating", "movie_id": movie_id},
                        inline=True,
                        inputStyle={"margin": "6px"},
                    )
                ]
                if with_rating
                else []
            ),
            style={"borderRadius": "50px"},
        ),
        className="col mb-4",
    )


navbar = html.Div(
    [
        html.H2("Movie Recommender", className="display-8", style={"color": "#df6919"}),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("System I", href="/", active="exact", style=link_style),
                dbc.NavLink(
                    "System II", href="/system-ii", active="exact", style=link_style
                ),
            ],
            pills=True,
            style={"margin-right": "50px"},
        ),
    ],
    style=nav_style,
)


content = html.Div(id="page-content", style={"margin": "100px"})
app.layout = html.Div([dcc.Location(id="url"), navbar, content])


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return html.Div(
            [
                html.Div(
                    [
                        html.H3("Select the genre for recommendations: "),
                        dcc.Dropdown(
                            id="genre-dropdown",
                            options=[{"label": k, "value": k} for k in genres],
                            value=None,
                            className="mb-4",
                            style={
                                "width": "50%",
                            },
                        ),
                    ],
                    style={"display": "flex", "flex-direction": "row", "gap": "40px"},
                ),
                html.Div(id="genre-output", className=""),
            ]
        )
    elif pathname == "/system-ii":
        movies = get_displayed_movies()
        return html.Div(
            [
                html.Div(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.H1("Enter your preferences: \t"),
                                    width="auto",
                                    style={"color": "#df6919"},
                                ),
                                dbc.Col(
                                    dbc.Button(
                                        children=[
                                            "Generate Recommendations",
                                        ],
                                        size="lg",
                                        className="btn-success",
                                        id="button-recommend",
                                    ),
                                    className="p-0",
                                ),
                            ],
                            className="sticky-top bg-white py-2",
                        ),
                        html.Div(
                            [
                                pull_movie_image(movie_id, movie, with_rating=True)
                                for movie_id, movie in movies
                            ],
                            className="row row-cols-1 row-cols-6",
                            id="rating-movies",
                        ),
                    ],
                    id="rater",
                ),
                html.H3(
                    "Generated Recommendations",
                    id="generated-recommendation",
                    style={"color": "#df6919"},
                ),
                html.Div(
                    className="row row-cols-1 row-cols-6",
                    id="recommended-movies",
                ),
            ]
        )


@app.callback(Output("genre-output", "children"), Input("genre-dropdown", "value"))
def update_output(genre):
    if genre is None:
        return html.Div()
    else:
        return [
            dbc.Row(
                [
                    html.Div(
                        [
                            *[
                                pull_movie_image(movie_id, movie)
                                for movie_id, movie in get_popular_movies(genre)
                            ],
                        ],
                        className="row row-cols-1 row-cols-5",
                    ),
                ]
            ),
        ]

@app.callback(
    Output("recommended-movies", "children"),
    Input("button-recommend", "n_clicks"),
    [
        State({"type": "movie_rating", "movie_id": ALL}, "id"),
        State({"type": "movie_rating", "movie_id": ALL}, "value"),
    ],
    prevent_initial_call=True,
)
def generate_recommendations(click, movie_ids, movie_ratings):
    rating_input = {
        movie_ids[i]["movie_id"]: int(rating)
        for i, rating in enumerate(movie_ratings)
        if rating is not None
    }

    recommended_movies = get_recommended_movies(rating_input)

    return [
        pull_movie_image(movie_id, movie_title)
        for movie_id, movie_title in recommended_movies
    ]
@app.callback(
    Output("rater", "style"),
    Output("generated-recommendation", "style"),
    [Input("button-recommend", "n_clicks")],
    prevent_initial_call=True,
)
def on_recommend_button_clicked(n):
    return {"display": "none"}, {"display": "block"}


@app.callback(
    Output("button-recommend", "disabled"),
    Input({"type": "movie_rating", "movie_id": ALL}, "value"),
)
def update_button_recommend_visibility(values):
    return not list(filter(None, values))


if __name__ == "__main__":
    app.run_server(port=8080, debug=True)
