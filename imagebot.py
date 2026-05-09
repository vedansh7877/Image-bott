from flask import Flask, render_template_string, request, redirect, url_for, session, flash
import openai
import os
from datetime import datetime
import base64
from io import BytesIO
import requests

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'super-secret-image-bot')

# OpenAI API Key (get free credits: platform.openai.com)
openai.api_key = os.environ.get('OPENAI_API_KEY')

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>🎨 AI Image Generator</title>
    <meta name="viewport" content="width=device-width">
    <style>
        *{margin:0;padding:0;box-sizing:border-box;}
        body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;padding:20px;}
        .container{max-width:800px;margin:0 auto;}
        .header{background:rgba(255,255,255,0.95);backdrop-filter:blur(20px);border-radius:25px;padding:30px;margin-bottom:30px;box-shadow:0 20px 40px rgba(0,0,0,0.1);text-align:center;}
        .header h1{font-size:2.5em;color:#333;margin-bottom:10px;}
        .header p{color:#666;font-size:1.1em;}
        .form-container{background:rgba(255,255,255,0.95);backdrop-filter:blur(20px);border-radius:25px;padding:40px;box-shadow:0 20px 40px rgba(0,0,0,0.1);}
        .prompt-input{width:100%;padding:20px;border:3px solid #e1e5e9;border-radius:20px;font-size:18px;font-family:inherit;transition:all 0.3s;margin-bottom:20px;}
        .prompt-input:focus{outline:none;border-color:#667eea;box-shadow:0 0 0 4px rgba(102,126,234,0.1);}
        .generate-btn{width:100%;background:linear-gradient(45deg,#ff6b6b,#ee5a52);color:white;border:none;padding:20px;border-radius:20px;font-size:20px;font-weight:bold;cursor:pointer;transition:all 0.3s;text-transform:uppercase;letter-spacing:1px;}
        .generate-btn:hover{transform:translateY(-3px);box-shadow:0 15px 30px rgba(255,107,107,0.4);}
        .generate-btn:disabled{opacity:0.6;cursor:not-allowed;transform:none;}
        .loading{display:none;text-align:center;padding:40px;color:#666;}
        .loading.show{display:block;}
        .loading i{font-size:3em;animation:spin 1s linear infinite;}
        @keyframes spin{100%{transform:rotate(360deg);}}
        .image-result{margin-top:30px;text-align:center;}
        .generated-image{max-width:100%;border-radius:20px;box-shadow:0 20px 40px rgba(0,0,0,0.2);margin:20px 0;}
        .history{margin-top:40px;}
        .history-item{background:#f8f9ff;border-radius:15px;padding:20px;margin:15px 0;box-shadow:0 5px 15px rgba(0,0,0,0.1);}
        .flash{padding:20px;margin:20px 0;border-radius:15px;text-align:center;font-weight:bold;}
        .flash.success{background:#d4edda;color:#155724;border:2px solid #c3e6cb;}
        .flash.error{background:#f8d7da;color:#721c24;border:2px solid #f5c6cb;}
        @media(max-width:768px){.container{padding:10px;}.header h1{font-size:2em;padding:0 20px;}}
    </style>
</head>
<body>
    <div class="container">
        {% with messages=get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category,message in messages %}
                    <div class="flash {{category}}">{{message}}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <div class="header">
            <h1>🎨 AI Image Generator</h1>
            <p>Describe anything → Get DALL-E 3 images instantly!</p>
        </div>
        
        <div class="form-container">
            <form method="POST">
                <textarea class="prompt-input" name="prompt" placeholder="✨ A majestic dragon flying over a cyberpunk city at sunset, ultra-detailed, cinematic lighting..." rows="4" required>{{ request.form.prompt if request.form else '' }}</textarea>
                <button type="submit" class="generate-btn" id="generateBtn">
                    ✨ Generate Image
                </button>
            </form>
            
            <div class="loading" id="loading">
                <i>🎨</i><br>
                <strong>Creating your masterpiece... (10-30s)</strong>
            </div>
        </div>
        
        {% if image_data %}
        <div class="image-result">
            <h3 style="color:white;text-align:center;margin:20px 0;">✨ Your Generated Image</h3>
            <img src="data:image/png;base64,{{ image_data }}" class="generated-image" alt="Generated">
            <p style="color:white;text-align:center;margin-top:10px;">
                Generated: {{ timestamp }}
            </p>
        </div>
        {% endif %}
    </div>

    <script>
        document.getElementById('generateBtn').onclick = function() {
            document.getElementById('loading').classList.add('show');
            document.getElementById('generateBtn').disabled = true;
            document.getElementById('generateBtn').innerText = '🎨 Generating...';
        }
    </script>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def generate():
    image_data = None
    timestamp = None
    
    if request.method == 'POST':
        prompt = request.form['prompt'].strip()
        
        if not openai.api_key:
            flash('❌ OpenAI API Key required! Set OPENAI_API_KEY environment variable.', 'error')
            return render_template_string(HTML, image_data=image_data, timestamp=timestamp)
        
        try:
            response = openai.Image.create(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )
            
            image_url = response.data[0].url
            image_response = requests.get(image_url)
            image_base64 = base64.b64encode(image_response.content).decode('utf-8')
            
            image_data = image_base64
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            flash('✨ Image generated successfully!', 'success')
            
        except Exception as e:
            flash(f'❌ Error: {str(e)}', 'error')
    
    return render_template_string(HTML, image_data=image_data, timestamp=timestamp, request=request)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 AI Image Bot Ready!")
    print("🌐 http://localhost:5000")
    print("🔑 Set OPENAI_API_KEY environment variable")
    app.run(host='0.0.0.0', port=port, debug=True)