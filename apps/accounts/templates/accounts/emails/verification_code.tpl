{% extends "mail_templated/base.tpl" %}

{% block subject %}
Your Verification Code
{% endblock %}

{% block html %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Verification</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333333;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
        }
        .container {
            max-width: 600px;
            margin: 20px auto;
            background-color: #ffffff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .header {
            background-color: #4CAF50;
            color: white;
            padding: 20px;
            text-align: center;
        }
        .content {
            padding: 30px;
        }
        .code-box {
            background-color: #f8f9fa;
            border: 2px dashed #4CAF50;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            margin: 20px 0;
        }
        .code {
            font-size: 36px;
            font-weight: bold;
            letter-spacing: 8px;
            color: #4CAF50;
            margin: 0;
        }
        .footer {
            background-color: #f8f9fa;
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: #666666;
        }
        .warning {
            color: #e74c3c;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Email Verification</h1>
        </div>
        <div class="content">
            <h2>Hello!</h2>
            <p>Thank you for registering. Please use the following verification code to verify your email address:</p>
            
            <div class="code-box">
                <p style="margin-bottom:5px;color:#666;">Your verification code:</p>
                <p class="code">{{ code }}</p>
            </div>
            
            <p>This code will expire in <strong>10 minutes</strong>.</p>
            <p>If you did not request this verification, please ignore this email.</p>
            <p class="warning">Do not share this code with anyone.</p>
        </div>
        <div class="footer">
            <p>This is an automated message. Please do not reply to this email.</p>
            <p>&copy; {% now "Y" %} Your Company. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
{% endblock %}

{% block plaintext %}
Hello!

Your verification code is: {{ code }}

This code will expire in 10 minutes.

If you did not request this verification, please ignore this email.

Do not share this code with anyone.
{% endblock %}
