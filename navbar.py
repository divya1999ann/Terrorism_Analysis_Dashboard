import dash_bootstrap_components as dbc


def Navbar():
     navbar = dbc.NavbarSimple(
           children=[
              dbc.NavItem(dbc.NavLink("Visualizations", href="/chart-plots")),
                    ],
          brand="Dashboard",
          brand_href="/home",
          color="#000000",
          sticky="top",
          dark=True
        )
     return navbar