from django.http import HttpResponse


def home(request):
    return HttpResponse("""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>RescueHub</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f4f6f8;
                margin: 0;
                padding: 0;
            }

            .container {
                max-width: 900px;
                margin: 80px auto;
                background: white;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 4px 16px rgba(0,0,0,0.08);
                text-align: center;
            }

            h1 {
                color: #2c3e50;
                margin-bottom: 16px;
            }

            p {
                color: #555;
                font-size: 18px;
            }

            .status {
                margin-top: 24px;
                padding: 12px 20px;
                display: inline-block;
                background: #e8f5e9;
                color: #2e7d32;
                border-radius: 8px;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>RescueHub</h1>
            <p>Sistema web para gestão de abrigos, animais e processos de adoção.</p>
            <div class="status">Aplicação Django rodando com sucesso</div>
        </div>
    </body>
    </html>
    """)