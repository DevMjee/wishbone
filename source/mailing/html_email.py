"""creates the html email body"""


def create_html_email(game_name, old_price, new_price):
    """creates the html email to be sent by wishbone"""

    email_template = f"""
    <!DOCTYPE html>
    <html lang="en">

    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width" />
        <title>Price Drop</title>

        <style>
            body {{
                margin: 0;
                padding: 0;
                background-color: #ffffff; 
                font-family: Arial, Helvetica, sans-serif;
            }}

            .outer {{
                width: 100%;
                background-color: #ffffff;
                padding: 20px 0;
            }}

            .card {{
                width: 600px;
                margin: 0 auto;
                background-color: #ffffff; 
                border-radius: 6px;
                overflow: hidden;
            }}

            .hero img {{
                width: 100%;
                display: block;
            }}

            h1 {{
                font-size: 32px;
                margin: 20px;
            }}

            p {{
                font-size: 16px;
                line-height: 1.4;
                margin: 20px;
            }}

            .divider {{
                width: 100%;
                border-top: 1px solid #ddd;
                margin: 20px 0;
            }}
        </style>
    </head>

    <body>

        <div class="outer">

            <div class="card">

                <div class="hero">
                    <img src="https://raw.githubusercontent.com/DevMjee/wishbone/refs/heads/main/assets/logo.png" alt="Header" />
                </div>

                <div class="divider"></div>

                <h1>Wishbone had detected a drop in price for {game_name}</h1>

                <p>
                    The game <strong>{game_name}</strong> you have been tracking has dropped in price!
                </p>

                <p>
                    It was <strong>{old_price}</strong> and is now <strong>{new_price}</strong> 
                </p>

                <p>
                    Check it out on <a href="www.google.com">Wishbone</a>
                </p>

                <div class="divider"></div>

                <div class="hero">
                    <img src="https://raw.githubusercontent.com/DevMjee/wishbone/refs/heads/main/assets/footer.png" alt="Game Image" />
                </div>

            </div>
        </div>

    </body>
    </html>
    """

    return email_template
